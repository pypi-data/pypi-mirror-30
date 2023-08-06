import os
import shutil
import tempfile

import mock
from testfixtures import OutputCapture

from hatcher.cli import exporter, main
from hatcher.testing import unittest
from hatcher.tests.common import (
    MainTestingMixin, patch_brood_client, patch_repository
)

DUMMY_EGG_DICT_BY_SHA = {
    'abc1234def456': {
        'name': 'mkl',
        'egg_basename': 'MKL',
        'version': '10.3',
        'build': 1,
        'full_version': '10.3-1',
        'packages': [],
        'md5': 'abc1234',
        'sha256': 'abc1234def456',
        'python_tag': None,
        'python': None,
        'product': None,
        'size': 12345,
        'type': 'egg',
        'enabled': True,
        'indexed_tag': 'cp27'
    },
    "sha256abcd1234cp27": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c930f94332bdcp27",
        "sha256": "sha256abcd1234cp27",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp27",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.6.0",
        "product": "free",
        "indexed_tag": "cp27",
        "full_version": "1.6.0-2",
    },
    "sha256efgh5678cp27": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c4891983744cp27",
        "sha256": "sha256efgh5678cp27",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp27",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.7.0",
        "product": "free",
        "indexed_tag": "cp27",
        "full_version": "1.7.0-2",
    },
    "sha256abcd1234cp34": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c930f94332bdcp34",
        "sha256": "sha256abcd1234cp34",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp34",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.6.0",
        "product": "free",
        "indexed_tag": "cp34",
        "full_version": "1.6.0-2",
    },
    "sha256efgh5678cp34": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c4891983744cp34",
        "sha256": "sha256efgh5678cp34",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp34",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.7.0",
        "product": "free",
        "indexed_tag": "cp34",
        "full_version": "1.7.0-2",
    },
}

DUMMY_EGG_INDEX_CP27 = {
    'MKL-10.3-1.egg': {
        'name': 'mkl',
        'egg_basename': 'MKL',
        'version': '10.3',
        'build': 1,
        'full_version': '10.3-1',
        'packages': [],
        'md5': 'abc1234',
        'sha256': 'abc1234def456',
        'python_tag': None,
        'python': None,
        'product': None,
        'size': 12345,
        'type': 'egg',
        'enabled': True
    },
    "numpy-1.6.0-2.egg": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c930f94332bdcp27",
        "sha256": "sha256abcd1234cp27",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp27",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.6.0",
        "product": "free",
        "full_version": "1.6.0-2",
    },
    "numpy-1.7.0-2.egg": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c4891983744cp27",
        "sha256": "sha256efgh5678cp27",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp27",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.7.0",
        "product": "free",
        "full_version": "1.7.0-2",
    },
}

DUMMY_EGG_INDEX_CP34 = {
    'MKL-10.3-1.egg': {
        'name': 'mkl',
        'egg_basename': 'MKL',
        'version': '10.3',
        'build': 1,
        'full_version': '10.3-1',
        'packages': [],
        'md5': 'abc1234',
        'sha256': 'abc1234def456',
        'python_tag': None,
        'python': None,
        'product': None,
        'size': 12345,
        'type': 'egg',
        'enabled': True
    },
    "numpy-1.6.0-2.egg": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c930f94332bdcp34",
        "sha256": "sha256abcd1234cp34",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp34",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.6.0",
        "product": "free",
        "full_version": "1.6.0-2",
    },
    "numpy-1.7.0-2.egg": {
        "size": 3382229,
        "md5": "41b0cfa9cff92d40b124c4891983744cp34",
        "sha256": "sha256efgh5678cp34",
        "packages": ["MKL 10.3-1"],
        "type": "egg",
        "name": "numpy",
        "build": 2,
        "python_tag": "cp34",
        "available": True,
        "mtime": 1408370414.56413,
        "version": "1.7.0",
        "product": "free",
        "full_version": "1.7.0-2",
    },
}

DUMMY_V1_RUNTIME_INDEX = {
    "cpython": {
        "2.7.10+1": {
            "abi": "gnu",
            "filename": "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
            "implementation": "cpython",
            "language_version": "2.7.10",
            "platform": "rh5-x86_64",
            "sha256": "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608",  # noqa
            "version": "2.7.10+1",
        },
        "3.4.3+2": {
            "abi": "gnu",
            "filename": "cpython-3.4.3+2-rh5_x86_64-gnu.runtime",
            "implementation": "cpython",
            "language_version": "3.4.3",
            "platform": "rh5-x86_64",
            "sha256": "2846e306bb3f1dd8ce572ffbe859ace160881ec4d15bd8b131c80eb72cb0f522",  # noqa
            "version": "3.4.3+2",
        },
    },
}

DUMMY_V1_RUNTIME_DICT_BY_SHA = {
    "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608": {  # noqa
        "abi": "gnu",
        "filename": "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
        "implementation": "cpython",
        "language_version": "2.7.10",
        "platform": "rh5-x86_64",
        "sha256": "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608",  # noqa
        "version": "2.7.10+1",
        },
    "2846e306bb3f1dd8ce572ffbe859ace160881ec4d15bd8b131c80eb72cb0f522": {  # noqa
        "abi": "gnu",
        "filename": "cpython-3.4.3+2-rh5_x86_64-gnu.runtime",
        "implementation": "cpython",
        "language_version": "3.4.3",
        "platform": "rh5-x86_64",
        "sha256": "2846e306bb3f1dd8ce572ffbe859ace160881ec4d15bd8b131c80eb72cb0f522",  # noqa
        "version": "3.4.3+2",
        },
    }


class TestExport(MainTestingMixin, unittest.TestCase):

    @patch_repository
    def setUp(self, Repository):
        self.maxDiff = None

        MainTestingMixin.setUp(self)
        self.tempdir = tempfile.mkdtemp()

        self.m_repo, self.m_plat_repo = self._mock_repository_class(Repository)
        self.m_repo.platform.return_value = self.m_plat_repo
        self.m_repo.name = self.repository
        self.m_plat_repo._repository = self.m_repo
        self.m_plat_repo.name = self.platform
        self.m_plat_repo.runtime_index.return_value = DUMMY_V1_RUNTIME_INDEX

        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', self.host, 'export']

        # Patch function calls
        self.patched_download_eggs = mock.patch(
            'hatcher.cli.exporter.download_eggs')
        self.m_download_eggs = self.patched_download_eggs.start()

        self.patched_download_runtimes = mock.patch(
            'hatcher.cli.exporter.download_runtimes')
        self.m_download_runtimes = self.patched_download_runtimes.start()

        self.patched_iter_repos_from_brood = mock.patch(
            'hatcher.cli.exporter.iter_repos_from_brood',
            return_value=iter([self.m_repo]),
        )
        self.m_iter_repos_from_brood = \
            self.patched_iter_repos_from_brood.start()

        self.patched_iter_plat_repos = mock.patch(
            'hatcher.cli.exporter.iter_plat_repos',
            return_value=iter([self.m_plat_repo]),
        )
        self.m_iter_plat_repos = self.patched_iter_plat_repos.start()

        self.patched_find_eggs_for_plat_repo = mock.patch(
            'hatcher.cli.exporter.find_eggs_for_plat_repo',
            return_value=DUMMY_EGG_DICT_BY_SHA,
        )
        self.m_find_eggs_for_plat_repo = \
            self.patched_find_eggs_for_plat_repo.start()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.patched_download_eggs.stop()
        self.patched_download_runtimes.stop()
        self.patched_iter_repos_from_brood.stop()
        self.patched_iter_plat_repos.stop()
        self.patched_find_eggs_for_plat_repo.stop()

    @patch_brood_client
    def test_simple(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 1
        root_target = self.tempdir
        platform_target = os.path.join(
            root_target, 'v1', self.organization, self.repository,
            self.platform
        )
        eggs_target = os.path.join(platform_target, 'eggs')
        runtimes_target = os.path.join(platform_target, 'runtimes')
        final_args = [self.tempdir]

        # When
        result = self.runner.invoke(
            main.hatcher, self.initial_args + final_args,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_called_once()
        self.m_find_eggs_for_plat_repo.assert_called_once()
        self.m_iter_plat_repos.assert_called_once()
        self.m_iter_repos_from_brood.assert_called_once()
        self.m_plat_repo.runtime_index.assert_called_once()
        self.m_download_runtimes.assert_called_once_with(
            self.m_plat_repo, DUMMY_V1_RUNTIME_DICT_BY_SHA, runtimes_target)
        self.m_download_eggs.assert_called_once_with(
            self.m_plat_repo, DUMMY_EGG_DICT_BY_SHA, eggs_target)

    @patch_brood_client
    def test_only_runtimes(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 1
        root_target = self.tempdir
        runtimes_target = os.path.join(
            root_target, 'v1', self.organization, self.repository,
            self.platform, 'runtimes'
        )
        final_args = ['-a', 'runtimes', self.tempdir]

        # When
        result = self.runner.invoke(
            main.hatcher, self.initial_args + final_args,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_called_once()
        self.m_find_eggs_for_plat_repo.assert_not_called()
        self.m_iter_plat_repos.assert_called_once()
        self.m_iter_repos_from_brood.assert_called_once()
        self.m_plat_repo.runtime_index.assert_called_once()
        self.m_download_runtimes.assert_called_once_with(
            self.m_plat_repo, DUMMY_V1_RUNTIME_DICT_BY_SHA, runtimes_target)
        self.m_download_eggs.assert_not_called()

    @patch_brood_client
    def test_only_eggs(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 1
        root_target = self.tempdir
        eggs_target = os.path.join(
            root_target, 'v1', self.organization, self.repository,
            self.platform, 'eggs'
        )
        final_args = ['-a', 'eggs', self.tempdir]

        # When
        result = self.runner.invoke(
            main.hatcher, self.initial_args + final_args,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_called_once()
        self.m_find_eggs_for_plat_repo.assert_called_once()
        self.m_iter_plat_repos.assert_called_once()
        self.m_iter_repos_from_brood.assert_called_once()
        self.m_plat_repo.runtime_index.assert_not_called()
        self.m_download_runtimes.assert_not_called()
        self.m_download_eggs.assert_called_once_with(
            self.m_plat_repo, DUMMY_EGG_DICT_BY_SHA, eggs_target)

    @patch_brood_client
    def test_specify_repo(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 1
        root_target = self.tempdir
        platform_target = os.path.join(
            root_target, 'v1', self.organization, self.repository,
            self.platform
        )
        eggs_target = os.path.join(platform_target, 'eggs')
        runtimes_target = os.path.join(platform_target, 'runtimes')
        final_args = [
            '-r', r'/'.join([self.organization, self.repository]), self.tempdir
        ]

        # When
        result = self.runner.invoke(
            main.hatcher, self.initial_args + final_args,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_called_once()
        self.m_find_eggs_for_plat_repo.assert_called_once()
        self.m_iter_plat_repos.assert_called_once()
        self.m_iter_repos_from_brood.assert_not_called()
        self.m_plat_repo.runtime_index.assert_called_once()
        self.m_download_runtimes.assert_called_once_with(
            self.m_plat_repo, DUMMY_V1_RUNTIME_DICT_BY_SHA, runtimes_target)
        self.m_download_eggs.assert_called_once_with(
            self.m_plat_repo, DUMMY_EGG_DICT_BY_SHA, eggs_target)

    @patch_brood_client
    def test_specify_platform(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 1

        root_target = self.tempdir
        platform_target = os.path.join(
            root_target, 'v1', self.organization, self.repository,
            self.platform
        )
        eggs_target = os.path.join(platform_target, 'eggs')
        runtimes_target = os.path.join(platform_target, 'runtimes')
        final_args = ['-p', self.platform, self.tempdir]

        # When
        result = self.runner.invoke(
            main.hatcher, self.initial_args + final_args,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_not_called()
        self.m_find_eggs_for_plat_repo.assert_called_once()
        self.m_iter_plat_repos.assert_called_once()
        self.m_iter_repos_from_brood.assert_called_once()
        self.m_plat_repo.runtime_index.assert_called_once()
        self.m_download_runtimes.assert_called_once_with(
            self.m_plat_repo, DUMMY_V1_RUNTIME_DICT_BY_SHA, runtimes_target)
        self.m_download_eggs.assert_called_once_with(
            self.m_plat_repo, DUMMY_EGG_DICT_BY_SHA, eggs_target)


class TestMisc(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

        MainTestingMixin.setUp(self)
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch_repository
    def test_download_runtimes_v1(self, Repository):
        # Given
        m_repo, m_plat_repo = self._mock_repository_class(Repository)

        runtimes = DUMMY_V1_RUNTIME_DICT_BY_SHA

        expected_calls = [
            mock.call(
                runtime['implementation'],
                runtime['version'],
                self.tempdir,
                runtime['sha256'],
            )
            for runtime in runtimes.values()
        ]

        # When
        with OutputCapture():
            exporter.download_runtimes(m_plat_repo, runtimes, self.tempdir)

        # Then
        self.assertEqual(m_plat_repo.download_runtime.call_count, 2)
        m_plat_repo.download_runtime.assert_has_calls(
            expected_calls, any_order=True)

    def test_unpack_index(self):
        # Given
        expected_output = DUMMY_V1_RUNTIME_DICT_BY_SHA

        # When
        result = exporter.unpack_index(DUMMY_V1_RUNTIME_INDEX)

        # Then
        self.assertEqual(result, expected_output)

    @patch_repository
    def test_download_eggs(self, Repository):
        # Given
        m_repo, m_plat_repo = self._mock_repository_class(Repository)

        expected_target_by_py_tag = {
            'None': os.path.join(self.tempdir, 'None'),
            'cp27': os.path.join(self.tempdir, 'cp27'),
            'cp34': os.path.join(self.tempdir, 'cp34'),
        }

        expected_calls = [
            mock.call(
                egg['indexed_tag'],
                egg['name'],
                egg['full_version'],
                expected_target_by_py_tag[egg['python_tag'] or 'None'],
                egg['sha256'],
                '{}-{}.egg'.format(egg['name'], egg['full_version']),
            )
            for egg in DUMMY_EGG_DICT_BY_SHA.values()
        ]

        # When
        with OutputCapture():
            exporter.download_eggs(
                m_plat_repo, DUMMY_EGG_DICT_BY_SHA, self.tempdir)

        # Then
        self.assertEqual(m_plat_repo.download_egg.call_count, 5)
        m_plat_repo.download_egg.assert_has_calls(
            expected_calls, any_order=True)

    @patch_repository
    @patch_brood_client
    def test_find_eggs_for_plat_repo(self, BroodClient, Repository):

        def _get_index_by_python_tag(py_tag):
            if py_tag == 'cp27':
                return DUMMY_EGG_INDEX_CP27
            elif py_tag == 'cp34':
                return DUMMY_EGG_INDEX_CP34

        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        _, m_plat_repo = self._mock_repository_class(Repository)

        python_tags = ['cp27', 'cp34']
        r_meta = DUMMY_EGG_DICT_BY_SHA

        m_brood_client.list_python_tags.return_value = iter(python_tags)
        m_plat_repo.egg_index.side_effect = _get_index_by_python_tag

        dummy_egg_meta = list(DUMMY_EGG_INDEX_CP27.values())
        dummy_egg_meta.extend(list(DUMMY_EGG_INDEX_CP34.values()))
        m_plat_repo.egg_metadata.side_effect = dummy_egg_meta

        # When
        result = exporter.find_eggs_for_plat_repo(m_brood_client, m_plat_repo)

        # Then
        self.assertEqual(result, r_meta)
        self.assertEqual(m_plat_repo.egg_index.call_count, 2)
        self.assertEqual(
            m_plat_repo.egg_metadata.call_count, len(dummy_egg_meta))
