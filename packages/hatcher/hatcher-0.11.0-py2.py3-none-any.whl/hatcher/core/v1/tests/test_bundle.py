""" Test bundle controllers."""

import json
import os
from hashlib import sha256
from unittest import TestCase

import responses

from hatcher.core.brood_url_handler import BroodURLHandler
from hatcher.core.model_registry import ModelRegistry
from hatcher.core.tests.common import JsonSchemaTestMixin
from hatcher.core.url_templates import URLS_V1
from hatcher.core.utils import python_tag
from hatcher.core.v1.bundle import (
    BundleCollectionController,
    BundleControllerFactory,
    BundleResourceFileController,
    BundleResourceController
)
from hatcher.core.v1.repository import Repository, SinglePlatformRepository


HASH_FUNC = sha256

BUNDLE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/example_bundle.json',
)


class BundleInfo(object):
    """ Define test info for the bundle."""
    organization = 'org'
    repository = 'repo'
    platform = 'plat'
    python_tag = 'cp36'
    name = 'bundle'
    version = '1.0.0-1'


class BundleURLs(object):
    """ Expected URLs for the bundle described by ``BundleInfo``.

    This is separated out in order to more easily update tests when
    hatcher is no longer the source of truth for its URLs.
    """
    _root = '/api/v1/json'
    _mid = 'org/repo/plat/bundles'
    _tail = 'cp36/bundle/1.0.0-1'

    index = '{}/indices/{}'.format(_root, _mid)
    metadata = '{}/metadata/{}/{}'.format(_root, _mid, _tail)
    upload = '{}/data/org/repo/bundles/upload'.format(_root)


def expected_metadata(bundle):
    """ Return expected metadata for the provided bundle.

    .. note::
        The "real" metadata object returned from the server also has
        a ``data`` key, which contains the unparsed bundle JSON. It
        is not included here for simplicity's sake.

    Parameters
    ----------
    bundle : BundleResourceController
        a BundleInfo object

    Returns
    -------
    dict
        the bundle metadata
    """
    return {
        'build': bundle.version.split('-')[1],
        'full_version': bundle.version,
        'name': bundle.name,
        'platform': bundle.collection.platform.name,
        'python_tag': bundle.python_tag,
        'version': bundle.version.split('-')[0],
    }


def expected_index(*bundles):
    """ Return the expected index for the provided bundles.

    Parameters
    ----------
    *bundles : BundleResourceController
        bundles that should be included in the index.
    """
    index = {}
    for bundle in bundles:
        index.setdefault(bundle.python_tag, {})
        python_tag = index[bundle.python_tag]

        python_tag.setdefault(bundle.name, {})
        name = python_tag[bundle.name]

        version, build = bundle.version.split('-')

        name.setdefault(version, {})
        version = name[version]

        version[build] = expected_metadata(bundle)

    return index


def expected_list(*bundles):
    return [
        {
            'python_tag': b.python_tag,
            'name': b.name,
            'version': b.version
        } for b in bundles
    ]


def url_handler_factory():
    return BroodURLHandler.from_auth('http://brood-dev')


def repository_factory(url_handler_factory_=url_handler_factory):
    return Repository(
        organization_name=BundleInfo.organization,
        name=BundleInfo.repository,
        url_handler=url_handler_factory_(),
        model_registry=ModelRegistry(api_version=1)
    )


def platform_factory(repository_factory_=repository_factory):
    repo = repository_factory_()
    return SinglePlatformRepository(
        repository=repo,
        platform=BundleInfo.platform,
        url_handler=repo._url_handler,
        model_registry=repo._model_registry
    )


def bundle_collection_factory(platform_factory_=platform_factory):
    return BundleCollectionController(
        platform=platform_factory_(), url_template=URLS_V1
    )


def bundle_controller_factory_factory(repository_factory_=repository_factory):
    return BundleControllerFactory(
        repository=repository_factory_(),
        url_template=URLS_V1
    )


def bundle_resource_factory(
        bundle_collection_factory_=bundle_collection_factory,
        bundle_info=BundleInfo):
    return BundleResourceController(
        collection=bundle_collection_factory_(),
        python_tag=bundle_info.python_tag,
        name=bundle_info.name,
        version=bundle_info.version
    )


def bundle_file_resource_factory():
    return bundle_controller_factory_factory().from_file(
        BUNDLE_PATH, BundleInfo.name, BundleInfo.version
    )


def bundle_file_dict(bundle_path=BUNDLE_PATH):
    with open(bundle_path) as bfile:
        return json.load(bfile)


def bundle_file_runtime_dict(bundle_path=BUNDLE_PATH):
    return bundle_file_dict(bundle_path)['runtime']


def response_path(url_handler, path):
    """ Return the full URL for the given path.

    Parameters
    ----------
    url_handler : hatcher.core.brood_url_handler.BroodURLHandler
        a URL handler instance
    path : str
        the URL path

    Returns
    -------
    str
        The full URL path
    """
    return '{}://{}{}'.format(url_handler.scheme, url_handler.host, path)


def add_json_response(rsps, method, bundle, path, data, status):
    """ Add a JSON response to the responses object.

    Parameters
    ----------
    rsps : responses.RequestMock
        request mock instance
    method : str
        request method string (capitalized), e.g. "GET"
    bundle: BundleResourceController or BundleCollectionController
        the bundle for which the request is being generated
    path : str
        the path portion of the URL
    data: dict
        data to return as JSON
    status : int
        HTTP status code
    """
    rsps.add(
        method,
        response_path(bundle.url_handler, path),
        json=data,
        status=status,
        content_type='application/json',
    )


def add_json_bundle_index_response(rsps, collection, *bundles):
    """ Add a standard index GET success response.

    Parameters
    ----------
    rsps : responses.RequestMock
        request mock instance
    *bundles: BundleResourceController or BundleCollectionController
        bundles to add to the index
    """
    add_json_response(
        rsps,
        method=rsps.GET,
        bundle=collection,
        path=collection.index_path,
        data=expected_index(*bundles),
        status=200,
    )


def add_json_bundle_metadata_response(rsps, bundle):
    """ Add a standard metadata GET success response.

    Parameters
    ----------
    rsps : responses.RequestMock
        request mock instance
    bundle: BundleResourceController or BundleCollectionController
        the bundle for which the request is being generated
    """
    add_json_response(
        rsps,
        method=rsps.GET,
        bundle=bundle,
        path=bundle.metadata_path,
        data=expected_metadata(bundle),
        status=200,
    )


def add_upload_bundle_response(rsps, bundle):
    """ Add a standard upload response for the specified bundle."""
    rsps.add(
        rsps.POST,
        response_path(bundle.url_handler, bundle.upload_path),
    )


def assert_valid_bundle_upload(tc, rsps, overwrite=False):
    """ Check the bundle upload request is properly formed.

    Parameters
    ----------
    tc : unittest.TestCase
        a TestCase instance with the JsonSchemaTestMixin mixed in
    rsps : responses.RequestsMock
        a requests mock instance used to perform an upload request
    overwrite : bool
        whether the request was made with overwrite True or False
    """
    tc.assertTrue(len(rsps.calls) == 1)
    request = rsps.calls[0][0]
    tc.assertJsonValid(
        tc._parse_multipart_data(request.body, request.headers),
        'edm_bundle_v2.json'
    )
    if overwrite:
        tc.assertTrue('overwrite=True' in request.url)
    else:
        tc.assertTrue('overwrite=False' in request.url)


class TestBundleResource(TestCase):
    """ Unit tests for the bundle resource."""

    # ------------------------------------------------------------------
    # Local Operations
    # ------------------------------------------------------------------

    def test_metadata_path(self):
        bundle = bundle_resource_factory()
        self.assertEqual(bundle.metadata_path, BundleURLs.metadata)

    def test_upload_path(self):
        bundles = bundle_resource_factory()
        self.assertEqual(bundles.upload_path, BundleURLs.upload)

    def test_lazy_dict(self):
        bundle = bundle_resource_factory()
        exp = {
            'python_tag': BundleInfo.python_tag,
            'name': BundleInfo.name,
            'version': BundleInfo.version,
        }
        self.assertEqual(bundle.lazy_dict, exp)

    def test_equality(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        self.assertTrue(b_one is not b_two)
        self.assertTrue(b_one == b_two)

    def test_inequality_org_name(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.collection.platform._repository.organization_name = 'other'
        self.assertTrue(b_one != b_two)

    def test_inequality_repo_name(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.collection.platform._repository.name = 'other'
        self.assertTrue(b_one != b_two)

    def test_inequality_platform_name(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.collection.platform.name = 'other'
        self.assertTrue(b_one != b_two)

    def test_inequality_python_tag(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.python_tag = 'other'
        self.assertTrue(b_one != b_two)

    def test_inequality_name(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.name = 'other'
        self.assertTrue(b_one != b_two)

    def test_inequality_version(self):
        b_one, b_two = bundle_resource_factory(), bundle_resource_factory()
        b_two.version = 'other'
        self.assertTrue(b_one != b_two)

    def test_str_does_not_error(self):
        str(bundle_resource_factory())

    def test_repr_does_not_error(self):
        repr(bundle_resource_factory())

    # ------------------------------------------------------------------
    # Remote Operations
    # ------------------------------------------------------------------

    def test_metadata(self):
        bundle = bundle_resource_factory()
        with responses.RequestsMock() as rsps:
            add_json_bundle_metadata_response(rsps, bundle)
            self.assertEqual(bundle.metadata(), expected_metadata(bundle))


class TestBundleFileResourceController(TestCase, JsonSchemaTestMixin):
    """ Unit tests for the file resource controller."""

    def test_repr_no_error(self):
        repr(bundle_file_resource_factory())

    def test_equality(self):
        self.assertTrue(
            bundle_file_resource_factory() == bundle_file_resource_factory()
        )

    def test_inequality_filename(self):
        one = bundle_file_resource_factory()
        two = bundle_file_resource_factory()
        two.filepath = 'other'
        self.assertTrue(one != two)

    def test_access_bundle_resources(self):
        bundle = bundle_file_resource_factory()
        attrs = (
            'collection',
            'python_tag',
            'name',
            'version',
            'url_handler',
        )
        for attr in attrs:
            assert getattr(bundle, attr) is getattr(bundle.bundle, attr)

    def test_upload(self):
        bundle = bundle_file_resource_factory()
        with responses.RequestsMock() as rsps:
            add_upload_bundle_response(rsps, bundle)
            bundle.upload()
            assert_valid_bundle_upload(self, rsps, overwrite=False)

    def test_upload_overwrite(self):
        bundle = bundle_file_resource_factory()
        overwrite = True
        with responses.RequestsMock() as rsps:
            add_upload_bundle_response(rsps, bundle)
            bundle.upload(overwrite=overwrite)
            assert_valid_bundle_upload(self, rsps, overwrite=overwrite)


class TestBundleCollection(TestCase):
    """ Unit tests for the bundle collection."""

    # ------------------------------------------------------------------
    # Local Operations
    # ------------------------------------------------------------------

    def test_index_path(self):
        bundles = bundle_collection_factory()
        self.assertEqual(bundles.index_path, BundleURLs.index)

    def test_get(self):
        bundles = bundle_collection_factory()
        exp_bundle = bundle_resource_factory()
        res_bundle = bundles.get(
            BundleInfo.python_tag, BundleInfo.name, BundleInfo.version
        )
        self.assertTrue(exp_bundle == res_bundle)

    def test_str_does_not_error(self):
        str(bundle_collection_factory())

    def test_repr_does_not_error(self):
        repr(bundle_collection_factory())

    # ------------------------------------------------------------------
    # Remote Operations
    # ------------------------------------------------------------------

    def test_index(self):
        collection = bundle_collection_factory()
        bundle_two_info = type('BI2', (BundleInfo,), {'version': '1.0.0-2'})
        bundle_three_info = type('BI3', (BundleInfo,), {'version': '1.1.0-1'})

        bundles = (
            bundle_resource_factory(),
            bundle_resource_factory(bundle_info=bundle_two_info),
            bundle_resource_factory(bundle_info=bundle_three_info)
        )

        with responses.RequestsMock() as rsps:
            add_json_bundle_index_response(rsps, collection, *bundles)
            self.assertEqual(expected_index(*bundles), collection.index())

    def test_list_multi_version(self):
        collection = bundle_collection_factory()
        bundle_two_info = type('BI2', (BundleInfo,), {'version': '1.0.0-2'})
        bundle_three_info = type('BI3', (BundleInfo,), {'version': '1.1.0-1'})
        bundles = (
            bundle_resource_factory(),
            bundle_resource_factory(bundle_info=bundle_two_info),
            bundle_resource_factory(bundle_info=bundle_three_info)
        )

        with responses.RequestsMock() as rsps:
            add_json_bundle_index_response(rsps, collection, *bundles)
            lst = collection.list()

        self.assertEqual(len(bundles), len(lst))
        # order not guaranteed, so sort them first.
        self.assertEqual(
            sorted(expected_list(*bundles), key=lambda d: d['version']),
            sorted(lst, key=lambda d: d['version'])
        )
        assert all(
            b.version in (l['version'] for l in lst) for b in bundles
        )

    def test_list_multi_name(self):
        collection = bundle_collection_factory()
        bundle_two_info = type('BI2', (BundleInfo,), {'name': 'barpak'})
        bundle_three_info = type('BI3', (BundleInfo,), {'name': 'bazpak'})
        bundles = (
            bundle_resource_factory(),
            bundle_resource_factory(bundle_info=bundle_two_info),
            bundle_resource_factory(bundle_info=bundle_three_info)
        )

        with responses.RequestsMock() as rsps:
            add_json_bundle_index_response(rsps, collection, *bundles)
            lst = collection.list()

        self.assertEqual(len(bundles), len(lst))
        # order not guaranteed, so sort them first.
        self.assertEqual(
            sorted(expected_list(*bundles), key=lambda d: d['name']),
            sorted(lst, key=lambda d: d['name'])
        )
        assert all(
            b.name in (l['name'] for l in lst) for b in bundles
        )

    def test_list_multi_python_tag(self):
        collection = bundle_collection_factory()
        bundle_two_info = type('BI2', (BundleInfo,), {'python_tag': 'cp27'})
        bundle_three_info = type('BI3', (BundleInfo,), {'python_tag': 'cp34'})

        bundles = (
            bundle_resource_factory(),
            bundle_resource_factory(bundle_info=bundle_two_info),
            bundle_resource_factory(bundle_info=bundle_three_info)
        )

        with responses.RequestsMock() as rsps:
            add_json_bundle_index_response(rsps, collection, *bundles)
            lst = collection.list()

        self.assertEqual(len(bundles), len(lst))
        # order not guaranteed, so sort them first.
        self.assertEqual(
            sorted(expected_list(*bundles), key=lambda d: d['python_tag']),
            sorted(lst, key=lambda d: d['python_tag'])
        )
        assert all(
            b.python_tag in (l['python_tag'] for l in lst) for b in bundles
        )

    def test_iter(self):
        collection = bundle_collection_factory()
        bundle_two_info = type('BI2', (BundleInfo,), {'version': '1.0.0-2'})
        bundle_three_info = type('BI3', (BundleInfo,), {'version': '1.1.0-1'})
        bundles = (
            bundle_resource_factory(),
            bundle_resource_factory(bundle_info=bundle_two_info),
            bundle_resource_factory(bundle_info=bundle_three_info)
        )

        with responses.RequestsMock() as rsps:
            add_json_bundle_index_response(rsps, collection, *bundles)
            # The explicit call to iter() validates we can make an iterable.
            coll_iter = iter(collection)
            resources = list(coll_iter)

        for bundle in bundles:
            assert bundle in resources


class TestBundleFactory(TestCase):
    """ Test the bundle maker."""

    def test_from_file(self):
        factory = bundle_controller_factory_factory()
        bundle = factory.from_file(
            BUNDLE_PATH, BundleInfo.name, BundleInfo.version
        )
        file_dict = bundle_file_dict()

        runtime = file_dict['runtime']
        exp_py_tag = python_tag(runtime['implementation'], runtime['version'])

        self.assertTrue(isinstance(bundle, BundleResourceFileController))
        self.assertEqual(bundle.collection.platform.name, runtime['platform'])
        self.assertEqual(bundle.python_tag, exp_py_tag)
        self.assertEqual(bundle.name, BundleInfo.name)
        self.assertEqual(bundle.version, BundleInfo.version)

    def test_from_runtime_dict(self):
        factory = bundle_controller_factory_factory()
        runtime = bundle_file_runtime_dict()
        bundle = factory.from_runtime_dict(
            runtime, BundleInfo.name, BundleInfo.version
        )
        exp_py_tag = python_tag(runtime['implementation'], runtime['version'])

        self.assertEqual(bundle.collection.platform.name, runtime['platform'])
        self.assertEqual(bundle.python_tag, exp_py_tag)
        self.assertEqual(bundle.name, BundleInfo.name)
        self.assertEqual(bundle.version, BundleInfo.version)
