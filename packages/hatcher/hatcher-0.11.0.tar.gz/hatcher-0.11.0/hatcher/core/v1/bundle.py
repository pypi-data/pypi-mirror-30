""" Provide interaction with server-side bundle resources."""

import json

from hatcher.core.utils import compute_sha256 as compute_hash
from hatcher.core.utils import python_tag


class BundleResourceController(object):
    """ A controller for bundle resource requests.

    Attributes
    ----------
    collection : BundleCollectionController
        The controller for this bundle's collection
    python_tag : str
        The python tag for the bundle resource
    name : str
        The name of the bundle resource
    version : str
        The full version (including build) of the bundle resource
    url_handler : BroodURLHandler
        A BroodURLHandler instance
    """

    def __init__(self, collection, python_tag, name, version):
        """ Instantiate a new BundleResourceController.

        Parameters
        ----------
        collection : BundleResourceCollection
            The bundle collection to which this bundle belongs
        python_tag : str
            The python tag (e.g. "cp36") of the bundle
        name : str
            The name of the bundle
        version : str
            The full version (including build number) of the bundle.
        filepath : str
            The path to a file used to create this controller, if
            applicable
        """
        self.collection = collection
        self.python_tag = python_tag
        self.name = name
        self.version = version
        self.url_handler = self.collection.url_handler

    def __eq__(self, other):
        """ Return whether two controllers are equivalent.

        Two controllers are equivalent if their respective bundle
        metadata is equivalent.
        """
        if self.python_tag != other.python_tag:
            return False
        if self.name != other.name:
            return False
        if self.version != other.version:
            return False
        self_plat = self.collection.platform
        other_plat = other.collection.platform
        if self_plat.organization_name != other_plat.organization_name:
            return False
        if self_plat.repository_name != other_plat.repository_name:
            return False
        if self_plat.name != other_plat.name:
            return False
        return True

    def __repr__(self):
        return (
            '<{0.__class__.__name__} '
            'organization={0.collection.platform.organization_name} '
            'repository={0.collection.platform.repository_name} '
            'platform={0.collection.platform.name} '
            'python_tag={0.python_tag} '
            'name={0.name} '
            'version={0.version}>'.format(self)
        )

    def __str__(self):
        return '{}/{}/{}/{}'.format(
            self.collection, self.python_tag, self.name, self.version
        )

    @property
    def lazy_dict(self):
        """ Lazily return a dict of local attributes.

        This property is explicitly lazy, in that it provides a
        representation of the resource without requiring any
        communication with the server.

        The lazy dict should contain enough information to build
        up a request to the Brood server if required.

        Returns
        -------
        dict
            A dict representation of the bundle managed by the controller
        """
        return {
            'python_tag': self.python_tag,
            'name': self.name,
            'version': self.version,
        }

    @property
    def metadata_path(self):
        """ Return the metadata URL for the bundle.

        Returns
        -------
        str
            The URL for the bundle's metadata
        """
        return self.collection.path('metadata', **vars(self))

    @property
    def upload_path(self):
        """ Return the path to which one may upload a bundle.

        Returns
        -------
        str
            The path to which a bundle may be uploaded
        """
        return self.collection.path('upload')

    def metadata(self):
        """ Return the bundle's metadata from the brood server.

        Returns
        -------
        dict
            The bundle metadata, which is currently of the form::

                {
                    'name': str,
                    'version': str,
                    'build': str,
                    'full_version': str,
                    'platform': str
                }

        """
        return self.url_handler.get_json(self.metadata_path)


class BundleResourceFileController(object):
    """ Controller for a bundle file associated with a bundle resource.

    Attributes
    ----------
    bundle : BundleResourceController
        The :class:`BundleResourceController` associated with this file
        controller
    filepath : str
        The path to the bundle file
    """

    def __init__(self, bundle, filepath):
        """ Instantiate a BundleFileResourceController.

        Parameters
        ----------
        bundle : BundleResourceController
            A bundle controller to use as the basis for this bundle
            file controller. The bundle controller is used to determine
            not found in the bundle file, like ``name`` and ``version``
        filepath : str
            The path to the bundle file
        """
        self.bundle = bundle
        self.filepath = filepath

    def __eq__(self, other):
        """ Return whether two bundle file controllers are equal.

        The controllers are equal if their filepaths are equal AND
        they satisfy all conditions of equality for a
        :class:`BundleResourceController`.
        """
        if self.filepath != other.filepath:
            return False
        return self.bundle == other

    def __getattr__(self, attr):
        """ Return any attributes from the bundle if not defined here."""
        return getattr(self.bundle, attr)

    def __repr__(self):
        return (
            '<{0.__class__.__name__} '
            'bundle={0.bundle!r} '
            'filepath={0.filepath}>'.format(self)
        )

    def upload(self, overwrite=False):
        """ Upload the bundle file to the server.

        Parameters
        ----------
        overwrite : bool, optional
            whether the bundle should be overwritten if it already
            exists on the server
        """
        self.url_handler.upload(
            self.upload_path,
            self._upload_metadata(),
            self.filepath,
            overwrite=overwrite
        )

    def _upload_metadata(self):
        """ Return the expected metadata dict for the bundle file."""
        version, build = self.version.split('-')
        return {
            'sha256': compute_hash(self.filepath),
            'bundle_name': self.name,
            'bundle_version': version,
            'bundle_build': build,
        }


class BundleCollectionController(object):
    """ A controller for a collection of bundle resources.

    Attributes
    ----------
    platform : hatcher.core.v1.repository.SinglePlatformRepository
        a :class:`SinglePlatformRepository` instance, used to determine
        the organization name, repository name, and platform of
        bundle resources
    url_handler : hatcher.core.brood_url_handler.BroodURLHandler
        a :class:`BroodURLHandler` instance
    urls : Dict[str, hatcher.core.url_templates.UrlBuilder]
        a dict mapping hatcher method names (e.g. :meth:`index`) to
        :class:`UrlBuilder` instances, used in generating paths
    """

    def __init__(self, platform, url_template):
        """ Instantiate a BundleCollectionController.

        Parameters
        ----------
        platform : hatcher.core.v1.repository.SinglePlatformRepository
            a :class:`SinglePlatformRepository` instance, used to
            determine the organization name, repository name, and
            platform of bundle resources
        url_template: hatcher.core.url_templates.UrlBuilder
            a :class:`BroodURLHandler` instance to serve as the base
            for URL paths
        """
        self.platform = platform
        self.url_handler = self.platform._url_handler  # pylint: disable=W0212
        self.urls = {
            'index': url_template.indices.bundles,
            'metadata': url_template.metadata.artefacts.bundles,
            'upload': url_template.data.bundles.upload,
        }

    def __iter__(self):
        """ Iterate over BundleResourceControllers for this collection.

        .. warning::
            Because of the vagaries of the server, the only way to get
            information about a collection of bundles is to get the
            entire index. So, there's no efficient way to iterate over
            them. When such a capability is added, this method should
            be updated to use it. Until then, it's not very efficient.

        Yields
        ------
        BundleResourceController
            :class:`BundleResourceController` instances generated from
            bundles specified in the index
        """
        for bundle in self._bundles_from_index(self.index()):
            yield BundleResourceController(
                self,
                **self._bundle_list_item(bundle)
            )

    def __repr__(self):
        return (
            '<{0.__class__.__name__} '
            'organization={0.platform.organization_name} '
            'repository={0.platform.repository_name} '
            'platform={0.platform.name}>'.format(self)
        )

    def __str__(self):
        return '{}/bundles'.format(self.platform)

    @property
    def index_path(self):
        """ Return the path for retrieving the bundle index.

        Returns
        -------
        str
            The path to retrieve the bundle index
        """
        return self.path('index')

    def get(self, python_tag, name, version):
        """ Return a BundleResourceController for the specified options.

        Parameters
        ----------
        python_tag : str
            The python tag (e.g. "cp36") of the bundle
        name : str
            The name of the bundle
        version : str
            The full version (including build number) of the bundle.

        Returns
        -------
        BundleResourceController
            A controller for the requested bundle
        """
        return BundleResourceController(self, python_tag, name, version)

    def index(self):
        """ Return the bundle index for the parent platform.

        Returns
        -------
        dict
            The bundle index, of the form::

                {
                    "python_tag": {
                        "name": {
                            "version": {
                                "build": {{metadata}},
                                ...
                            },
                            ...
                        },
                        ...
                    },
                    ...
                }

        """
        return self.url_handler.get_json(self.index_path)

    def list(self):
        """ Return a list of bundles info for the parent platform.

        .. warning::
            Because of the vagaries of the server, the only way to get
            information about a collection of bundles is to get the
            entire index. So, there's no efficient way to iterate over
            them. When such a capability is added, this method should
            be updated to use it. Until then, it's not very efficient.

        Returns
        -------
        List[dict]:
            A list of bundle metadatafrom the index, filtered by field
            mask
        """
        return list(
            self._bundle_list_item(b)
            for b in self._bundles_from_index(self.index())
        )

    def path(self, operation, **kwargs):
        """ Return the Brood URL for the specified bundle.

        Parameters
        ----------

        operation: str
            One of the operations specified in ``self.urls``
        **kwargs
            Extra keyword arguments to pass to the format operator for
            the specified URL base

        Returns
        -------

        str
            The bundle download URL
        """
        return self.urls[operation].format(
            organization_name=self.platform.organization_name,
            repository_name=self.platform.repository_name,
            platform=self.platform.name,
            **kwargs
        )

    @classmethod
    def _bundles_from_index(cls, index):
        """ Yield bundle metadata dicts from the index.

        Assume that the terminal nodes of the index tree are the bundle
        metadata, and simply traverse the tree until we find a node
        whose values are not dictionaries. Assume this node is a
        metadata dict, and yield it.
        """
        for val in index.values():
            if not isinstance(val, dict):
                yield index
                break
            else:
                for bundle in cls._bundles_from_index(val):
                    yield bundle

    @staticmethod
    def _bundle_list_item(metadata):
        """ Return bits of metadata required for a bundle list item."""
        return {
            'python_tag': metadata['python_tag'],
            'name': metadata['name'],
            'version': metadata['full_version'],
        }


class BundleControllerFactory(object):
    """ Create bundle controllers.

    Attributes
    ----------
    repository : brood.core.v1.repository.Repository
        The repository for which the controllers will be created
    url_template : brood.core.url_templates.UrlBuilder
        An instance of :class:`UrlBuilder` to serve as the base for
        generated URLs
    """

    def __init__(self, repository, url_template):
        """ Instantiate a BundleControllerFactory.

        Parameters
        ----------
        repository : brood.core.v1.repository.Repository
            The repository for which the controllers will be created
        url_template : brood.core.url_templates.UrlBuilder
            An instance of :class:`UrlBuilder` to serve as the base for
            generated URLs
        """
        self.repository = repository
        self.url_template = url_template

    def from_file(self, filepath, name, version):
        """ Create BundleResourceFileController from a bundle file.

        Parameters
        ----------
        filepath : str
            The path to the bundle file
        name : str
            The name of the bundle
        version : str
            The full version of the bundle, including build

        Returns
        -------
        BundleResourceFileController
            A file controller for the specified bundle file and info
        """
        with open(filepath) as bundle_file:
            runtime = json.load(bundle_file)['runtime']
        return BundleResourceFileController(
            bundle=self.from_runtime_dict(runtime, name, version),
            filepath=filepath,
        )

    def from_runtime_dict(self, runtime, name, version):
        """ Create a BundleResourceController from a runtime dict.

        Parameters
        ----------
        runtime : dict
            A dict of python runtime data. This must contain, minimally,
            keys "platform", "implementation", and "version"
        name : str
            The name of the bundle
        version : str
            The full version of the bundle, including build

        Returns
        -------
        BundleResourceController
            A bundle controller for the specified runtime and bundle
            data
        """
        plat = self.repository.platform(runtime['platform'])
        coll = BundleCollectionController(plat, self.url_template)
        py_tag = python_tag(runtime['implementation'], runtime['version'])
        return coll.get(py_tag, name, version)
