import shutil
import tempfile

import mock

from hatcher.cli import main
from hatcher.testing import unittest
from hatcher.tests.common import (
    MainTestingMixin, patch_brood_client, patch_repository
)


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

        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', self.host, 'export']

        # Patch function calls

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

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.patched_download_runtimes.stop()
        self.patched_iter_repos_from_brood.stop()
        self.patched_iter_plat_repos.stop()

    @patch_brood_client
    def test_runtimes(self, BroodClient):
        # Given
        m_brood_client = self._mock_brood_client_class(BroodClient)
        m_brood_client._api_version = 0

        final_args = ['-a', 'runtimes', self.tempdir]

        exp_output = "Exporting runtimes is not supported for api version 0"

        # When
        result = self.runner.invoke(
                main.hatcher, self.initial_args + final_args,
            )

        # Then
        self.assertEqual(result.output.strip(), exp_output)
        self.assertEqual(result.exit_code, 0)
        m_brood_client.list_platforms.assert_called_once()
        self.m_iter_repos_from_brood.assert_called_once()
        self.m_plat_repo.runtime_index.assert_not_called()
        self.m_download_runtimes.assert_not_called()
