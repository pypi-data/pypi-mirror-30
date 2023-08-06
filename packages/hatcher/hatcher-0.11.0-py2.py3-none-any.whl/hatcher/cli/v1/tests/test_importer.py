import os
import shutil
import sys
import tempfile
import textwrap
from collections import namedtuple

import mock
from requests.exceptions import HTTPError
import six
import testfixtures

from hatcher.cli import importer, main
from hatcher.cli.utils import makedirs
from hatcher.tests.common import (
    MainTestingMixin, patch_brood_client, patch_organization, patch_repository,
)
from hatcher.testing import unittest


class TestImport(MainTestingMixin, unittest.TestCase):

    @patch_repository
    @patch_brood_client
    def setUp(self, BroodClient, Repository):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--api-version', '1', '--url', self.host,
                             'import']

        self.tempdir = tempfile.mkdtemp()
        self.api_ver_root = os.path.join(self.tempdir, 'v1')
        self.org_dir = os.path.join(self.api_ver_root, self.organization)
        self.repo_dir = os.path.join(self.org_dir, self.repository)
        self.plat_dir = os.path.join(self.repo_dir, self.platform)
        makedirs(self.plat_dir)

        self.m_brood_client = self._mock_brood_client_class(BroodClient)
        self.m_brood_client._api_version = 1
        self.m_brood_client.list_organizations.return_value = [
            self.organization]

        self.m_org = self.m_brood_client.organization(self.organization)
        self.m_org.list_repositories.return_value = [self.repository]

        self.m_repo, self.m_plat_repo = self._mock_repository_class(Repository)
        self.m_plat_repo._repository = self.m_repo
        self.m_plat_repo.name = self.platform

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_no_artefacts_in_tree(self):
        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts"
            ) as find_arts:
                result = self.runner.invoke(
                    main.hatcher, self.initial_args + [self.tempdir])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 3)
        self.m_plat_repo.upload_egg.assert_not_called()
        self.m_repo.upload_runtime.assert_not_called()
        self.m_repo.upload_app.assert_not_called()
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, False)

    def test_simple_only_eggs(self):
        # Given
        final_args = ['--artefact-kind', 'eggs']
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                        "hatcher.core.utils.EggMetadata.from_file",
                        side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                            "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                            side_effect=['foo_remote_metadata',
                                         'bar_remote_metadata',
                                         'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher,
                            self.initial_args + [self.tempdir] + final_args
                        )

        # Then
        self.assertEqual(result.exit_code, 0)
        find_arts.assert_called_once_with(
            os.path.join(self.plat_dir, 'eggs'))
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.m_repo.upload_runtime.assert_not_called()
        self.m_repo.upload_app.assert_not_called()
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, False)

    def test_only_apps(self):
        # Given
        final_args = ['--artefact-kind', 'apps']

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                result = self.runner.invoke(
                    main.hatcher,
                    self.initial_args + [self.tempdir] + final_args
                )

        # Then
        self.assertEqual(result.exit_code, 0)
        find_arts.assert_called_once_with(
            os.path.join(self.plat_dir, 'apps'))
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        self.m_plat_repo.upload_egg.assert_not_called()
        self.m_repo.upload_runtime.assert_not_called()
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, False)

    def test_eggs_and_apps(self):
        # Given
        final_args = ['--artefact-kind', 'eggs', '--artefact-kind', 'apps']
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                        "hatcher.core.utils.EggMetadata.from_file",
                        side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                            "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                            side_effect=['foo_remote_metadata',
                                         'bar_remote_metadata',
                                         'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher,
                            self.initial_args + [self.tempdir] + final_args
                        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 2)
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        self.m_repo.upload_runtime.assert_not_called()
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, False)

    def test_only_runtimes(self):
        # Given
        final_args = ['--artefact-kind', 'runtimes']

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ):
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                result = self.runner.invoke(
                    main.hatcher,
                    self.initial_args + [self.tempdir] + final_args
                )

        # Then
        self.assertEqual(result.exit_code, 0)
        find_arts.assert_called_once_with(
            os.path.join(self.plat_dir, 'runtimes'))
        self.assertEqual(self.m_repo.upload_runtime.call_count, 3)
        self.m_plat_repo.upload_egg.assert_not_called()
        self.m_repo.upload_app.assert_not_called()

    def test_all_artefacts(self):
        # Given
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                    "hatcher.core.utils.EggMetadata.from_file",
                    side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                        "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                        side_effect=['foo_remote_metadata',
                                     'bar_remote_metadata',
                                     'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher, self.initial_args + [self.tempdir])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 3)
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.assertEqual(self.m_repo.upload_runtime.call_count, 3)
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, False)

    def test_specify_repo_all_artefacts(self):
        # Given
        initial_args = self.initial_args + ['--repository', 'acme/dev']
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                        "hatcher.core.utils.EggMetadata.from_file",
                        side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                            "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                            side_effect=['foo_remote_metadata',
                                         'bar_remote_metadata',
                                         'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher, initial_args + [self.tempdir])

        # Then
        # self.assertEqual(result.output, '')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 3)
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.assertEqual(self.m_repo.upload_runtime.call_count, 3)
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root,
            {self.organization: [self.repository]}, None, False
        )

    def test_specify_plat_all_artefacts(self):
        # Given
        initial_args = self.initial_args + ['--platform', self.platform]
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                        "hatcher.core.utils.EggMetadata.from_file",
                        side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                            "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                            side_effect=['foo_remote_metadata',
                                         'bar_remote_metadata',
                                         'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher, initial_args + [self.tempdir])

        # Then
        # self.assertEqual(result.output, '')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 3)
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.assertEqual(self.m_repo.upload_runtime.call_count, 3)
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, (self.platform, ), False
        )

    def test_create_missing(self):
        # Given
        initial_args = self.initial_args + ['--create-missing']
        m_metadata = namedtuple('MockMetadata', ['python_tag', 'name', 'full_version'])
        foo_metadata = m_metadata(python_tag='cp27', name='foo', full_version='1.1.1-1')
        bar_metadata = m_metadata(python_tag='cp27', name='bar', full_version='1.1.1-1')
        baz_metadata = m_metadata(python_tag='cp27', name='baz', full_version='1.1.1-1')

        # When
        with mock.patch(
            "hatcher.cli.importer.iter_plat_repos_from_root",
            return_value=iter([(self.m_plat_repo, self.plat_dir)])
        ) as m_iter_plat_repos:
            with mock.patch(
                "hatcher.cli.importer.find_artefacts",
                return_value=['foo', 'bar', 'baz'],
            ) as find_arts:
                with mock.patch(
                        "hatcher.core.utils.EggMetadata.from_file",
                        side_effect=[foo_metadata, bar_metadata, baz_metadata]
                ) as m_metadata:
                    with mock.patch(
                            "hatcher.core.v0.repository.SinglePlatformRepository.egg_metadata",
                            side_effect=['foo_remote_metadata',
                                         'bar_remote_metadata',
                                         'baz_remote_metadata']
                    ) as m_metadata_func:
                        result = self.runner.invoke(
                            main.hatcher, initial_args + [self.tempdir])

        # Then
        # self.assertEqual(result.output, '')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(find_arts.call_count, 3)
        self.assertEqual(self.m_plat_repo.upload_egg.call_count, 3)
        self.assertEqual(self.m_repo.upload_runtime.call_count, 3)
        self.assertEqual(self.m_repo.upload_app.call_count, 3)
        m_iter_plat_repos.assert_called_once_with(
            mock.ANY, self.api_ver_root, None, None, True
        )


class TestMisc(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.tempdir = tempfile.mkdtemp()
        self.api_ver_root = os.path.join(self.tempdir, 'v1')
        self.org_dir = os.path.join(self.api_ver_root, self.organization)
        self.repo_dir = os.path.join(self.org_dir, self.repository)
        self.plat_dir = os.path.join(self.repo_dir, self.platform)

        makedirs(self.plat_dir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch_organization
    @patch_brood_client
    def test_iter_orgs_from_path(self, BroodClient, Organization):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)
        mocked_org = self._mock_organization_class(Organization)

        brood_client.list_organizations.return_value = [self.organization]
        brood_client.organization.return_value = mocked_org

        expected_results = [(mocked_org, self.org_dir)]

        # When
        results = [result for result
                   in importer.iter_orgs_from_path(
                       brood_client, self.api_ver_root, [self.organization])
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_organization
    @patch_brood_client
    def test_iter_orgs_from_requested(self, BroodClient, Organization):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)
        mocked_org = self._mock_organization_class(Organization)

        brood_client.list_organizations.return_value = [
            self.organization, 'foo']
        brood_client.organization.return_value = mocked_org

        expected_results = [(mocked_org, self.org_dir)]

        requested_org = [self.organization]

        # When
        results = [result for result in
                   importer.iter_orgs_from_path(
                       brood_client, self.api_ver_root, requested_org)
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_brood_client
    def test_ensure_orgs_exist_fail(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)

        brood_client.list_organizations.return_value = [self.organization]

        bogus_org = 'bogus_org'

        expected_output = (
            "Organization(s) `{0}` do not exist in the database."
        ).format(bogus_org)

        requested_orgs = [bogus_org, self.organization]

        # When
        with self.assertRaises(SystemExit) as sys_exit:
            with testfixtures.OutputCapture() as output:
                importer.ensure_specified_orgs_exist(
                    requested_orgs, brood_client)

        # Then
        output.compare(expected_output)
        self.assertEqual(sys_exit.exception.code, -1)

    @patch_brood_client
    def test_ensure_orgs_in_root_fail(self, BroodClient):
        # Given
        missing_org = 'other_org'
        brood_client = self._mock_brood_client_class(BroodClient)

        brood_client.list_organizations.return_value = [
            self.organization, missing_org]

        expected_output = (
            "Organization(s) `{}` do not exist in the specified directory."
        ).format(missing_org)

        requested_orgs = [missing_org, self.organization]

        # When
        with self.assertRaises(SystemExit) as sys_exit:
            with testfixtures.OutputCapture() as output:
                importer.ensure_specified_orgs_in_root(
                    requested_orgs, self.api_ver_root)

        # Then
        output.compare(expected_output)
        self.assertEqual(sys_exit.exception.code, -1)

    @patch_brood_client
    def test_ensure_orgs_exist_pass(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)

        brood_client.list_organizations.return_value = [self.organization]

        expected_output = ""

        requested_orgs = [self.organization]

        # When
        with testfixtures.OutputCapture() as output:
            importer.ensure_specified_orgs_exist(requested_orgs, brood_client)

        # Then
        output.compare(expected_output)

    @patch_brood_client
    def test_ensure_orgs_in_root_pass(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)

        brood_client.list_organizations.return_value = [self.organization]

        expected_output = ""

        requested_orgs = [self.organization]

        # When
        with testfixtures.OutputCapture() as output:
            importer.ensure_specified_orgs_in_root(
                requested_orgs, self.api_ver_root)

        # Then
        output.compare(expected_output)

    @patch_organization
    def test_iter_repos_from_path(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_repo = mocked_org.repository(self.repository)

        mocked_org.list_repositories.return_value = [self.repository]
        mocked_org.name = self.organization
        expected_results = [(mocked_repo, self.repo_dir)]

        # When
        results = [result for result
                   in importer.iter_repos_from_path(mocked_org, self.org_dir)]

        # Then
        self.assertEqual(results, expected_results)

    @patch_organization
    def test_iter_repos_from_requested(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_repo = mocked_org.repository(self.repository)

        mocked_org.list_repositories.return_value = [self.repository]
        mocked_org.name = self.organization
        expected_results = [(mocked_repo, self.repo_dir)]

        requested_repos = [self.repository]

        # When
        results = [result for result
                   in importer.iter_repos_from_path(
                       mocked_org, self.org_dir, requested_repos)
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_organization
    def test_iter_repos_from_requested_not_existing(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_org.repository.side_effect = HTTPError
        mocked_org.name = self.organization

        expected_results = []
        expected_output = textwrap.dedent("""\
           Requested repositories `{}` do not exist in the database.
           Continuing with any remaining repositories.
           Use `create-missing` to create these repositories.
           """).format(self.organization + '/' + self.repository)

        requested_repos = [self.repository]

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_repos_from_path(
                           mocked_org, self.org_dir, requested_repos)
                       ]

        # Then
        self.assertEqual(results, expected_results)
        output.compare(expected_output)

    @patch_organization
    def test_iter_repos_from_requested_not_in_path(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_repo = mocked_org.repository(self.repository)

        mocked_org.list_repositories.return_value = [
            self.repository, 'foo', 'bar']
        mocked_org.name = self.organization

        expected_results = [(mocked_repo, self.repo_dir)]
        expected_output = textwrap.dedent("""\
        Requested repositories `{}` do not exist in the directory.
        Continuing with any remaining repositories.""").format(
            "acme/bar, acme/foo")

        requested_repos = [self.repository, 'foo', 'bar']

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_repos_from_path(
                           mocked_org, self.org_dir, requested_repos)
                       ]

        # Then
        self.assertEqual(results, expected_results)
        output.compare(expected_output)

    @patch_organization
    def test_iter_repos_from_path_no_repo(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_repo = mocked_org.repository(self.repository)

        mocked_org.list_repositories.return_value = [self.repository]
        mocked_org.name = self.organization

        non_existing_repo = 'no_repo'
        makedirs(os.path.join(self.org_dir, non_existing_repo))

        expected_results = [(mocked_repo, self.repo_dir)]
        expected_output = textwrap.dedent("""\
            Requested repositories `{}` do not exist in the database.
            Continuing with any remaining repositories.
            Use `create-missing` to create these repositories.
            """).format(self.organization + '/' + non_existing_repo)

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_repos_from_path(
                           mocked_org, self.org_dir)
                       ]

        # Then
        self.assertEqual(results, expected_results)
        output.compare(expected_output)

    @patch_organization
    def test_iter_repos_from_path_create_missing(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_repo = mocked_org.repository(self.repository)

        mocked_org.list_repositories.return_value = [self.repository]
        mocked_org.name = self.organization

        non_existing_repo = 'no_repo'
        non_existing_repo_dir = os.path.join(self.org_dir, non_existing_repo)
        makedirs(non_existing_repo_dir)

        expected_results = [(mocked_repo, self.repo_dir),
                            (mocked_repo, non_existing_repo_dir)]
        expected_output = ""

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_repos_from_path(
                           mocked_org, self.org_dir, create_missing=True)
                       ]

        # Then
        six.assertCountEqual(self, results, expected_results)
        output.compare(expected_output)

    @patch_organization
    def test_iter_repos_from_requested_create_missing(self, Organization):
        self.maxDiff = None
        # Given
        mocked_org = self._mock_organization_class(Organization)
        mocked_org.name = self.organization
        mocked_org.repository.side_effect = [HTTPError, self.repository] * 3

        non_existing_repos = ['bar', 'foo']

        non_existing_repo_dirs = [
            os.path.join(self.org_dir, repo) for repo in non_existing_repos
        ]
        for new_dir in non_existing_repo_dirs:
            makedirs(new_dir)

        expected_results = [(self.repository, self.repo_dir)]
        expected_results.extend(
            [(self.repository, repo_dir)
             for repo_dir in non_existing_repo_dirs]
        )
        expected_output = ""

        requested_repos = [self.repository, 'bar', 'foo']

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_repos_from_path(
                           mocked_org, self.org_dir, requested_repos,
                           create_missing=True)
                       ]

        # Then
        if sys.version_info < (3, 0):
            self.assertItemsEqual(results, expected_results)
        else:
            self.assertCountEqual(results, expected_results)
        output.compare(expected_output)

    @patch_organization
    def test_create_repositories(self, Organization):
        # Given
        mocked_org = self._mock_organization_class(Organization)

        missing_repos = ['foo', 'bar', 'baz']

        description = 'Created automatically with `hatcher import`'
        expected_calls = [mock.call(repo_name, description)
                          for repo_name in missing_repos]

        # When
        importer.create_missing_repos(mocked_org, missing_repos)

        # Then
        mocked_org.create_repository.assert_has_calls(
            expected_calls, any_order=True)

    @patch_repository
    def test_iter_plat_repos_from_path(self, Repository):
        # Given
        mocked_repo, mocked_plat_repo = self._mock_repository_class(Repository)

        expected_results = [(mocked_plat_repo, self.plat_dir)]

        # When
        results = [result for result
                   in importer.iter_plat_repos_from_path(
                       mocked_repo, self.repo_dir)
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_repository
    def test_iter_plat_repos_from_path_specified(self, Repository):
        # Given
        mocked_repo, mocked_plat_repo = self._mock_repository_class(Repository)

        expected_results = [(mocked_plat_repo, self.plat_dir)]

        # When
        results = [result for result
                   in importer.iter_plat_repos_from_path(
                       mocked_repo, self.repo_dir, (self.platform,))
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_repository
    def test_iter_plat_repos_from_path_invalid_specified(self, Repository):
        # Given
        mocked_repo, mocked_plat_repo = self._mock_repository_class(Repository)

        expected_results = [(mocked_plat_repo, self.plat_dir)]
        expected_output = (
            "Requested platforms `rh5_INVALID` do not exist in the specified "
            "directory. Continuing with any remaining platforms."
        )

        # When
        with testfixtures.OutputCapture() as output:
            results = [result for result
                       in importer.iter_plat_repos_from_path(
                           mocked_repo, self.repo_dir,
                           (self.platform, 'rh5_INVALID'))
                       ]

        # Then
        self.assertEqual(results, expected_results)
        output.compare(expected_output)

    @patch_brood_client
    def test_iter_plat_repos_from_root(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)
        brood_client.list_organizations.return_value = [self.organization]

        mocked_org = brood_client.organization(self.organization)
        mocked_org.list_repositories.return_value = [self.repository]
        mocked_repo = mocked_org.repository(self.repository)
        mocked_plat_repo = mocked_repo.platform(self.platform)

        expected_results = [(mocked_plat_repo, self.plat_dir)]

        # When
        results = [result for result
                   in importer.iter_plat_repos_from_root(
                       brood_client, self.api_ver_root)
                   ]

        # Then
        self.assertEqual(results, expected_results)

    @patch_brood_client
    def test_iter_plat_repos_from_root_plat_specified(self, BroodClient):
        # Given
        other_plat = os.path.join(self.repo_dir, 'win-x86')
        makedirs(other_plat)

        brood_client = self._mock_brood_client_class(BroodClient)
        brood_client.list_organizations.return_value = [self.organization]

        mocked_org = brood_client.organization(self.organization)
        mocked_org.list_repositories.return_value = [self.repository]
        mocked_repo = mocked_org.repository(self.repository)
        mocked_plat_repo = mocked_repo.platform(self.platform)

        expected_results = [(mocked_plat_repo, self.plat_dir)]

        # When
        results = [result for result
                   in importer.iter_plat_repos_from_root(
                       brood_client, self.api_ver_root,
                       requested_platforms=(self.platform,))
                   ]

        # Then
        self.assertEqual(len(results), 1)
        self.assertEqual(results, expected_results)

    def test_find_artefacts(self):
        # Given
        artefacts_dir = os.path.join(self.plat_dir, 'eggs')
        cp35_dir = os.path.join(artefacts_dir, 'cp27')
        cp27_dir = os.path.join(artefacts_dir, 'cp35')
        makedirs(cp35_dir)
        makedirs(cp27_dir)

        fake_egg_cp35 = tempfile.NamedTemporaryFile(dir=cp35_dir)
        fake_egg_cp27 = tempfile.NamedTemporaryFile(dir=cp27_dir)

        expected_results = [fake_egg_cp35.name, fake_egg_cp27.name]

        # When
        results = importer.find_artefacts(artefacts_dir)

        # Then
        self.assertEqual(sorted(results), sorted(expected_results))

    @patch_repository
    def test_error_uploading(self, Repository):
        # Given
        artefact_file = 'foo'
        _, plat_repo = self._mock_repository_class(Repository)
        plat_repo.upload_egg.side_effect = Exception
        upload_kwargs = {'overwrite': True, 'verify': True}

        expected_output = "Error uploading {0}".format(artefact_file)

        # When
        with self.assertRaises(Exception):
            with testfixtures.OutputCapture() as output:
                importer.batch_upload(
                    plat_repo.upload_egg, [artefact_file], upload_kwargs
                )

        # Then
        output.compare(expected_output)

    def test_validate_requested_repo_format(self):
        # Given
        org_repo = 'foo/bar'
        expected_result = ('foo', 'bar')

        # When
        result = importer.validate_requested_repo_format(org_repo)

        # Then
        self.assertEqual(result, expected_result)

    def test_validate_requested_repo_format_invalid(self):
        # Given
        org_repo = 'foo-bar'
        expected_output = (
            "Repository must be in the format `organization/repository`\n"
        )

        # When
        with self.assertRaises(SystemExit) as sys_exit:
            with testfixtures.OutputCapture() as output:
                importer.validate_requested_repo_format(org_repo)

        # Then
        output.compare(expected_output)
        self.assertEqual(sys_exit.exception.code, -1)

        # Given
        org_repo = 'foo/bar/baz'

        # When
        with self.assertRaises(SystemExit) as sys_exit:
            with testfixtures.OutputCapture() as output:
                importer.validate_requested_repo_format(org_repo)

        # Then
        output.compare(expected_output)
        self.assertEqual(sys_exit.exception.code, -1)
