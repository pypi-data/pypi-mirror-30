""" Common utilities for various hatcher resources."""

import functools
import hashlib
import os
import re
import sys
import time
import warnings

try:
    from zipfile import BadZipFile
except ImportError:
    from zipfile import BadZipfile as BadZipFile

from requests.utils import default_user_agent as requests_user_agent
from requests import HTTPError

from okonomiyaki import file_formats
from okonomiyaki.errors import (
    UnsupportedMetadata, InvalidRequirementString,
    InvalidMetadataField, MissingMetadata, InvalidMetadata)
from okonomiyaki.platforms import EPDPlatform
from okonomiyaki.runtimes import IRuntimeMetadata
from okonomiyaki.versions import EnpkgVersion, PEP440Version, MetadataVersion

import hatcher
from hatcher.errors import ChecksumMismatchError, InvalidEgg, InvalidRuntime


_MAX_RETRY_WAIT_TIME = 1.0
_MINIMUM_PYTHON_VERSION = (2, 5)
_PYTHON_IMPL_TO_PREFIX = {
    'cpython': 'cp',
    'pypy': 'pp',
}
_PYTHON_VERSION_PREFIX_RE = re.compile(r'^(?P<version>\d+\.\d+).*$')
_R_RUNTIME = re.compile("""
    ^(?P<language>[\w]+)_runtime
    _
    (?P<version>[^_]+)
    _
    (?P<build_system_version>[^_]+)
    _
    (?P<platform>[^_]+)
    _
    (?P<build>\d+)
    \.
    (?P<extension>.+$)
    """, re.VERBOSE)


try:
    unicode = unicode
except NameError:
    unicode = str


def python_tag_name(tag):
    if tag is None:
        return 'none'
    return tag


def is_str_or_unicode(value):
    """ Check if value is an instance of str or unicode.

    Python 2/3 compatible string check, where the string may either
    be a Python 2 string or a Python 3 string (unicode)

    Parameters
    ----------
    value : str
        The value to check

    Returns
    -------
    bool
        True if ``value`` is an instance of ``str`` or, in Python 2,
        ``unicode``
    """
    return isinstance(value, str) or isinstance(value, unicode)


def python_tag(implementation, version):
    """ Return the Python tag for the given implementation and version.

    Parameters
    ----------
    implementation : str
        The Python implementation, e.g. "cpython" or "pypy"
    version : str
        The Python version string, in the form of "<major>.<minor>"*

    Returns
    -------
    str
        The python tag, e.g. "cp36"

    Raises
    ------
    TypeError
        If the implementation or version is not a string
    ValueError:
        If the implementation is not supported, the version cannot be
        parsed, or the version is older than the
        ``_MINIMUM_PYTHON_VERSION``
    """
    if not is_str_or_unicode(implementation):
        raise TypeError(
            'Invalid implementation. Expected str, got '
            '{}'.format(type(implementation))
        )
    if not is_str_or_unicode(version):
        raise TypeError(
            'Invalid version. Expected str, got {}'.format(type(version))
        )
    if implementation not in _PYTHON_IMPL_TO_PREFIX:
        raise ValueError(
            'Invalid implementation. Expected one of {}, got '
            '{}'.format(tuple(_PYTHON_IMPL_TO_PREFIX), implementation)
        )
    version_match = _PYTHON_VERSION_PREFIX_RE.match(version)
    if version_match is None:
        raise ValueError(
            'Could not parse provided version. Expected "<major>.<minor>*"'
        )
    version_info = _version_info(version_match.group('version'))
    if not _valid_version(version_info):
        raise ValueError(
            'Python {0[0]}.{0[1]} is no longer supported. '
            'Please update your Python.'.format(version_info)
        )
    return '{0}{1[0]}{1[1]}'.format(
        _PYTHON_IMPL_TO_PREFIX[implementation], version_info
    )


class RuntimeMetadataV0(object):
    _PYTHON_VERSION_TO_PYTHON_TAG = {
        "3.4": "cp34",
        "3.3": "cp33",
        "3.2": "cp32",
        "3.1": "cp31",
        "3.0": "cp30",
        "2.7": "cp27",
        "2.6": "cp26",
        "2.5": "cp25",
    }
    _VERSION_PREFIX_RE = re.compile(r'^(?P<version>\d+\.\d+)\.\d+$')

    def __init__(self, language, version, build, platform,
                 build_system_version, file_format, path):
        self.language = language
        self.version = version
        self.build = build
        self.platform = platform
        self.build_system_version = build_system_version
        self.file_format = file_format
        self._sha256 = None
        self.path = path

    @property
    def full_version(self):
        return '{0}-{1}'.format(self.version, self.build)

    @property
    def python_tag(self):
        match = self._VERSION_PREFIX_RE.match(self.version)
        if match is None:
            raise ValueError(
                'Unrecognized Python version: {0!r}'.format(self.version))
        version_prefix = match.group('version')
        if version_prefix not in self._PYTHON_VERSION_TO_PYTHON_TAG:
            raise ValueError(
                'Unsupported Python version: {0!r}'.format(self.version))
        return self._PYTHON_VERSION_TO_PYTHON_TAG[version_prefix]

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def sha256(self):
        if self._sha256 is None:
            self._sha256 = compute_sha256(self.path)
        return self._sha256

    @classmethod
    def from_file(cls, path, platform=None):
        basename = os.path.basename(path)
        m = _R_RUNTIME.match(basename)
        if m is None:
            raise InvalidRuntime(
                'Invalid filename format for {0!r}'.format(basename))
        attrs = m.groupdict()
        attrs['file_format'] = attrs.pop('extension')
        attrs['build'] = int(attrs['build'])
        return cls(path=path, **attrs)


class RuntimeMetadata(RuntimeMetadataV0):

    def __init__(self, *args, **kwargs):
        warnings.warn(
            ('hatcher.core.utils.RuntimeMetadata has been renamed to '
             'hatcher.core.utils.RuntimeMetadataV0'),
            DeprecationWarning,
        )
        super(RuntimeMetadata, self).__init__(*args, **kwargs)


class RuntimeMetadataV1(object):

    def __init__(self, path, metadata):
        self.path = path
        self._sha256 = None
        self._metadata = metadata

    @property
    def implementation(self):
        return self._metadata.implementation

    @property
    def version(self):
        return self._metadata.version

    @property
    def platform(self):
        return str(EPDPlatform(self._metadata.platform))

    @property
    def sha256(self):
        if self._sha256 is None:
            self._sha256 = compute_sha256(self.path)
        return self._sha256

    @classmethod
    def from_file(cls, path):
        basename = os.path.basename(path)
        try:
            metadata = IRuntimeMetadata.factory_from_path(path)
        except BadZipFile:
            raise InvalidRuntime(
                '{0!r} is not an Enthought runtime package'.format(basename))
        except InvalidMetadata as exc:
            error = '{0!r}: {1}'.format(basename, str(exc))
            raise InvalidRuntime(error)
        except UnsupportedMetadata as exc:
            error = '{0!r}: {1}'.format(basename, str(exc))
            raise InvalidRuntime(error)
        return cls(path, metadata)


class EggMetadata(object):

    MAX_METADATA_VERSION = MetadataVersion.from_string('1.3')

    def __init__(self, metadata, path):
        self._egg_metadata = metadata
        self._sha256 = None
        self.path = path

    @property
    def full_version(self):
        return str(self._egg_metadata.version)

    @property
    def python_tag(self):
        return self._egg_metadata.python_tag_string

    @property
    def name(self):
        return self._egg_metadata.egg_basename

    @property
    def sha256(self):
        if self._sha256 is None:
            self._sha256 = compute_sha256(self.path)
        return self._sha256

    @classmethod
    def from_file(cls, path):
        basename = os.path.basename(path)

        if not file_formats.is_egg_name_valid(basename):
            raise InvalidEgg("Invalid egg name: '{0}'".format(basename))

        try:
            metadata = file_formats.EggMetadata.from_egg(path)
        except BadZipFile:
            raise InvalidEgg(
                "Bad zip file when validating egg '{0}'.".format(basename))
        except UnsupportedMetadata as exc:
            raise InvalidEgg(
                "Egg '{0}' uses an unsupported metadata version {1}. "
                "Maximum supported metadata version is {2}.".format(
                    basename, exc.metadata_version, cls.MAX_METADATA_VERSION))
        except InvalidRequirementString as exc:
            raise InvalidEgg(
                "Egg '{0}' has an invalid requirement string in egg "
                "dependency list: '{1}'".format(
                    basename, exc.requirement_string))
        except InvalidMetadataField as exc:
            error = ("Egg '{0}' metadata field is invalid: "
                     "({1} = {2!r})".format(
                         basename, exc.name, exc.value))
            raise InvalidEgg(error)
        except MissingMetadata as exc:
            raise InvalidEgg(
                "Egg '{0}' is missing Enthought metadata and may not be "
                "in the enpkg egg format.".format(basename))
        except InvalidMetadata as exc:
            raise InvalidEgg(str(exc))
        except Exception:
            raise InvalidEgg(
                "Unexpected error parsing egg '{0}'.".format(basename))

        metadata_version = metadata.metadata_version
        if not (metadata_version.major == cls.MAX_METADATA_VERSION.major and
                metadata_version.minor <= cls.MAX_METADATA_VERSION.minor):
            raise InvalidEgg(
                "Egg '{0}' uses an unsupported metadata version {1}. "
                "Hatcher {2} supports only eggs up to {3}.".format(
                    basename, metadata.metadata_version, hatcher.__version__,
                    cls.MAX_METADATA_VERSION))

        return cls(metadata, path)


class _SorterMixin(object):

    def __init__(self, key):
        self.key = key

    def _assert_can_compare(self, other):
        cls = type(self)
        if not isinstance(other, cls):
            msg = "Cannot compare {0!r} and {1!r}"
            raise TypeError(msg.format(cls, type(other)))

    def __eq__(self, other):
        self._assert_can_compare(other)
        return self.key == other.key

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        self._assert_can_compare(other)
        return self.key < other.key

    def __le__(self, other):
        return not (self > other)

    def __gt__(self, other):
        self._assert_can_compare(other)
        return self.key > other.key

    def __ge__(self, other):
        return not (self < other)

    def __hash__(self):
        return hash(self.key)


class AppSorter(_SorterMixin):

    def __init__(self, name, version, python_tag):
        self._name = name
        self._version = version
        self._python_tag = python_tag

        comparable_version = EnpkgVersion.from_string(version)

        key = (name.lower(), comparable_version, python_tag)
        super(AppSorter, self).__init__(key)

    def __repr__(self):
        return '{0}({1!r}, {2!r}, {3!r})'.format(
            type(self).__name__, self._name, self._version, self._python_tag)


class RuntimeV0Sorter(AppSorter):

    def __init__(self, filename):
        self._filename = filename
        metadata = RuntimeMetadataV0.from_file(filename)
        super(RuntimeV0Sorter, self).__init__(
            metadata.language, metadata.full_version, metadata.python_tag)

    def __repr__(self):
        return '{0}({1!r})'.format(type(self).__name__, self._filename)


class EggNameSorter(_SorterMixin):

    def __init__(self, egg_file_name):
        self._egg_file_name = egg_file_name
        egg_name, upstream, build = file_formats.split_egg_name(egg_file_name)
        comparable_version = EnpkgVersion.from_upstream_and_build(
            upstream, build)

        _, extension = os.path.splitext(egg_file_name)

        key = (egg_name, comparable_version, extension)
        super(EggNameSorter, self).__init__(key)

    def __repr__(self):
        return '{0}({1!r})'.format(type(self).__name__, self._egg_file_name)


class NameVersionPairSorter(_SorterMixin):

    def __init__(self, name, version, version_parser=PEP440Version):
        self._name = name
        self._version = version
        self._version_parser = version_parser

        comparable_version = version_parser.from_string(version)

        key = (name, comparable_version)
        super(NameVersionPairSorter, self).__init__(key)

    def __repr__(self):
        return '{0}({1!r})'.format(
            type(self).__name__, self._name, self._version,
            self._version_parser)


def _hash_file(hasher, filename, block_size):
    with open(filename, "rb") as fp:
        while True:
            data = fp.read(block_size)
            if data == b"":
                break
            hasher.update(data)
    return hasher.hexdigest()


def compute_sha256(filename, block_size=16384):
    return _hash_file(hashlib.sha256(), filename, block_size)


def compute_md5(filename, block_size=16384):
    return _hash_file(hashlib.md5(), filename, block_size)


def hatcher_user_agent():
    return 'hatcher/{0} {1}'.format(
        hatcher.__version__, requests_user_agent())


def upload_verify(filename, local_metadata, get_remote_metadata,
                  do_upload, verify, overwrite):
    """Handle uploading a file with the feature to verify if the same file
    has been uploaded before.

    .. note:: this should probably be done on the server side

    Parameters
    ----------
    filename : str
        The path to the file to upload
    local_metadata : object
        A local metadata specification type.
    get_remote_metadata : callable
        A closure that accepts a ``local_metadata`` specification and will
        return the remote metadata dictionary.
    do_upload : callable
        A closure that takes no arguments and will upload the file.
    verify : bool
        True to verify if the file has been uploaded before; False to
        simply attempt to upload.
    overwrite : bool
        True to skip any verification and force-overwrite the object if
        it already exists on the server.

    """
    if verify and not overwrite:
        try:
            remote_metadata = get_remote_metadata(local_metadata)
        except HTTPError as exc:
            if exc.response.status_code != 404:
                raise
            # If the object is not found (status code 404), do the upload.
            return do_upload()
        else:
            if local_metadata.sha256 != remote_metadata['sha256']:
                raise ChecksumMismatchError(
                    'A file called {0} has already been uploaded with '
                    'different content'.format(os.path.basename(filename)))
            # The sha256 matches, we don't need to upload.
            return
    else:
        return do_upload()


def retry_on_exception(exception, max_retries=0, backoff_factor=0.1):
    """Decorator to retry a function if it throws `exception`. Up to
    `max_tries` attempts are made, after which the `exception is propagated.
    Parameters
    ----------
    `exception` : Exception
        The exception to be handled by the decorator.
    `max_retries` : int
        Maximum number of attempts.
    `backoff_factor` : float
        Multiplier used for computing exponential backoff between
        successive attempts. This is identical to the keyword argument of the
        same name in `urllib3.util.retry.Retry`. Execution will `time.sleep()`
        for `backoff_factor * 2 ^ { (attempt_num - 1) }` seconds. The wait time
        is capped at `1.0` second.
    Note
    ----
    As an example, given max_retries=10, after the first call failure, retries
    will happen at following times from the first call until it succeeds:
        0.1,  0.3,  0.7,  1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5
    """
    def retry_decorator(func, *args, **kwargs):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exception:
                    attempts += 1
                    if (attempts >= max_retries):
                        raise
                    else:
                        wait = min(
                            backoff_factor * (2 ** (attempts - 1)),
                            _MAX_RETRY_WAIT_TIME
                        )
                        time.sleep(wait)
        return decorated_function
    return retry_decorator


if sys.platform == "win32":
    @retry_on_exception(WindowsError, max_retries=6)
    def reliable_rename(source, target):
        os.rename(source, target)
else:
    reliable_rename = os.rename


def _valid_version(version_info):
    return version_info[:2] >= _MINIMUM_PYTHON_VERSION


def _version_info(version):
    return tuple(int(i) for i in version.split('.'))
