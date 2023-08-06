from hatcher.testing import unittest
from hatcher.tests.common import (
    MainTestingMixin,
    patch_brood_client,
    patch_organization,
    patch_repository,
    patch_team,
    patch_user,
)
from hatcher.cli import main


class TestMainOrganizationActions(MainTestingMixin, unittest.TestCase):

    @patch_brood_client
    def test_create_organization(self, BroodClient):
        # Given
        description = 'Acme Co.'
        brood_client = self._mock_brood_client_class(BroodClient)
        create_organization = brood_client.create_organization

        args = ['--url', 'brood-dev.invalid', 'organizations', 'create',
                self.organization, description]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        create_organization.assert_called_once_with(
            self.organization, description)
        self.assertEqual(result.exit_code, 0)

    @patch_brood_client
    def test_list_organizations(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)
        list_organizations = brood_client.list_organizations
        list_organizations.return_value = ['one', 'two']
        expected_output = 'one\ntwo\n'

        args = ['--url', 'brood-dev.invalid', 'organizations', 'list']

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        list_organizations.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)

    @patch_organization
    def test_create_repository(self, Organization):
        # Given
        description = 'a repository'
        organization = self._mock_organization_class(Organization)
        create_repository = organization.create_repository

        args = ['--url', 'brood-dev.invalid', 'repositories', 'create',
                self.organization, self.repository, description]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        create_repository.assert_called_once_with(self.repository, description)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_delete_repository(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        delete = repository.delete

        initial_args = ['--url', 'brood-dev.invalid', 'repositories', 'delete']
        final_args = [self.organization, self.repository]

        r_output = "{0} will be deleted. Proceed? [y/N]: "

        # When
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='N')

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertTrue(result.output.startswith(r_output.format(repository)))
        delete.assert_not_called()
        self.assertEqual(result.exit_code, 0)

        # When
        Repository.reset_mock()
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='Y')

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertTrue(result.output.startswith(r_output.format(repository)))
        delete.assert_called_once_with(force=False)
        self.assertEqual(result.exit_code, 0)

        # When
        Repository.reset_mock()
        args = initial_args + ['-y'] + final_args
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        delete.assert_called_once_with(force=False)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_delete_repository_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        delete = repository.delete

        initial_args = ['--url', 'brood-dev.invalid', 'repositories', 'delete',
                        '--force']
        final_args = [self.organization, self.repository]

        r_output = "{0} will be deleted. Proceed? [y/N]: "

        # When
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='N')

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertTrue(result.output.startswith(r_output.format(repository)))
        delete.assert_not_called()
        self.assertEqual(result.exit_code, 0)

        # When
        Repository.reset_mock()
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='Y')

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertTrue(result.output.startswith(r_output.format(repository)))
        delete.assert_called_once_with(force=True)
        self.assertEqual(result.exit_code, 0)

        # When
        Repository.reset_mock()
        args = initial_args + ['-y'] + final_args
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        delete.assert_called_once_with(force=True)
        self.assertEqual(result.exit_code, 0)

    @patch_organization
    def test_list_repositories(self, Organization):
        # Given
        repositories = ['dev', 'staging', 'prod']
        expected = '{0}\n'.format('\n'.join(sorted(repositories)))
        organization = self._mock_organization_class(Organization)
        list_repositories = organization.list_repositories
        list_repositories.return_value = repositories

        args = ['--url', 'brood-dev.invalid', 'repositories', 'list',
                self.organization]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        list_repositories.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)

    @patch_organization
    def test_create_user(self, Organization):
        # Given
        organization = self._mock_organization_class(Organization)
        create_user = organization.create_user

        args = ['--url', 'brood-dev.invalid', 'users', 'create',
                self.organization, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        create_user.assert_called_once_with(self.user)
        self.assertEqual(result.exit_code, 0)

    @patch_user
    def test_delete_user(self, User):
        # Given
        user = self._mock_user_class(User)
        delete_user = user.delete

        initial_args = ['--url', 'brood-dev.invalid', 'users', 'delete']
        final_args = [self.organization, self.user]

        r_output = "{0} will be deleted. Proceed? [y/N]: "

        # When
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='N')

        # Then
        self.assertTrue(result.output.startswith(r_output.format(self.user)))
        delete_user.assert_not_called()
        self.assertEqual(result.exit_code, 0)

        # When
        User.reset_mock()
        args = initial_args + final_args
        result = self.runner.invoke(main.hatcher, args=args, input='Y')

        # Then
        self.assertTrue(result.output.startswith(r_output.format(self.user)))
        delete_user.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)

        # When
        User.reset_mock()
        args = initial_args + ['-y'] + final_args
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertUserConstructedCorrectly(User)
        delete_user.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
