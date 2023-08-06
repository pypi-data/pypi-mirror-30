from collections import defaultdict
import os
import sys
import textwrap

import click
from requests.exceptions import HTTPError

from .repository_actions import batch_upload
from .main import hatcher
from .utils import ArtefactKinds, pass_brood_client


def find_artefacts(artefact_dir):
    """ Given directory find all of the files.

    Parameter
    ---------
    artefact_dir : str
        The root path containing all of the files of a given artefact type to
        be imported.

    Returns
    -------
    list : Containing all of the filepaths of the artefacts.

    """
    return [os.path.join(path, filename)
            for path, _, files in os.walk(artefact_dir)
            for filename in files]


def validate_requested_repo_format(org_repo):
    """ Validate a given org_repo string is formatted correctly.

    Parameter
    ---------
    org_repo : string
        Expected to be formatted as `org/repo`

    Returns
    -------
    tuple : Containing (org, repo)

    """
    try:
        org, repo = org_repo.split('/')
        return (org, repo)
    except ValueError:
        click.secho(
            "Repository must be in the format `organization/repository`",
            fg='red', err=True
        )
        sys.exit(-1)


def create_missing_repos(org, missing_repos):
    """ Create any missing repos in the specified organization.

    Parameters
    ----------
    org : Organization
        hatcher.core.v*.organization.Organization instance

    missing_repos : list
        containing the names of the missing repositories

    """
    description = "Created automatically with `hatcher import`"
    for repo_name in missing_repos:
        org.create_repository(repo_name, description)


def ensure_specified_orgs_exist(specified_orgs, brood_client):
    """ Ensure that all orgs specified exist in the brood database

    Parameters
    ----------
    specified_orgs : list
        Organizations to be imported

    brood_client : BroodClient
        hatcher.core.brood_client.BroodClient instance

    """
    existing_orgs = brood_client.list_organizations()

    missing_orgs = set(specified_orgs).difference(existing_orgs)

    if len(missing_orgs) > 0:
        click.secho(
            "Organization(s) `{0}` do not exist in the database.".format(
                ', '.join(i for i in missing_orgs)),
            fg='red', err=True
        )
        sys.exit(-1)


def ensure_specified_orgs_in_root(specified_orgs, root_dir):
    """ Ensure that all orgs specified exist in the root directory being
    imported. Only applies when an org/repo is specified with --repository.

    Parameters
    ----------
    specified_orgs : list
        Organizations to be imported

    root_dir : str
        Path to the root directory being imported

    """
    orgs_on_path = os.listdir(root_dir)

    missing_orgs = set(specified_orgs).difference(orgs_on_path)

    if len(missing_orgs) > 0:
        click.secho(
            "Organization(s) `{0}` do not exist in the specified "
            "directory. ".format(', '.join(i for i in missing_orgs)),
            fg='red', err=True
        )
        sys.exit(-1)


def iter_orgs_from_path(brood_client, root_dir, requested_orgs):
    """ Generator yielding every organization in a structured directory.

    If the organization does not exist in brood or a requested organization
    does not exist in root_dir, an error will print to the console and that
    organization will be skipped.

    Parameters
    ----------
    brood_client : BroodClient
        hatcher.core.brood_client.BroodClient instance

    root_dir : str
        Path to the root of a structured directory containing the result of
        exporting a brood database.

    requested_orgs : list
        Requested organizations

    Yields
    ------
    tuple : Containing the Organization object and a string of the path to that
           organization in the structured directory

    """
    for org_name in requested_orgs:
        org_dir = os.path.join(root_dir, org_name)
        org = brood_client.organization(org_name)
        yield (org, org_dir)


def iter_repos_from_path(org, org_dir, requested_repos=None,
                         create_missing=False):
    """ Generator yielding every repository in a structured directory.

    If the repository does not exist in brood or the requested repository does
    not exist in org_dir, an error will print to the console and that
    repository will be skipped.

    Parameters
    ----------
    org : Organization
        hatcher.core.v*.organization.Organization instance

    org_dir : string
        The path to the organization in the structured directory.

    requested_repos : list
        List of requested repositories for a given organization

    create_missing : bool
        Whether or not to create missing orgs and repos

    Yields
    ------
    tuple : Containing the Repository object and a string of the path to
           the repository in the structured directory

    """

    def _get_org_repo_str(repos_names):
        return ', '.join(org.name + '/' + r for r in repos_names)

    missing_repo_message = textwrap.dedent("""\
    Requested repositories `{0}` do not exist in the database.
    Continuing with any remaining repositories.
    Use `create-missing` to create these repositories.""")

    repo_names_from_path = set(next(os.walk(org_dir))[1])

    if requested_repos is not None:
        requested_repos = set(requested_repos)

        requested_repos_not_in_path = sorted(
            requested_repos.difference(repo_names_from_path)
        )
        if requested_repos_not_in_path:
            msg = textwrap.dedent("""\
            Requested repositories `{0}` do not exist in the directory.
            Continuing with any remaining repositories.""")

            click.secho(
                msg.format(_get_org_repo_str(requested_repos_not_in_path)),
                fg='red', err=True
            )

        valid_repo_names = sorted(
            requested_repos.intersection(repo_names_from_path)
        )
    else:
        existing_repos = set(org.list_repositories())
        valid_repo_names = sorted(
            repo_names_from_path.intersection(existing_repos)
        )
        non_existing_repos = sorted(
            repo_names_from_path.difference(existing_repos)
        )
        if non_existing_repos and not create_missing:
            click.secho(
                missing_repo_message.format(
                    _get_org_repo_str(non_existing_repos)),
                fg='red', err=True
            )

        elif non_existing_repos and create_missing:
            create_missing_repos(org, non_existing_repos)
            valid_repo_names.extend(non_existing_repos)

    for repo_name in valid_repo_names:
        repo_dir = os.path.join(org_dir, repo_name)
        try:
            repo = org.repository(repo_name)
            yield (repo, repo_dir)
        # When specifying repositories, we don't check if the repository exists
        # which requires admin privileges. Rather, catch and handle HTTPError's
        except HTTPError:
            if create_missing:
                create_missing_repos(org, repo_name)
                repo = org.repository(repo_name)
                yield (repo, repo_dir)
            else:
                click.secho(
                    missing_repo_message.format(org.name + '/' + repo_name),
                    fg='red', err=True
                )


def iter_plat_repos_from_path(repo, repo_dir, platforms=None):
    """ Generator yielding every platform repository in a structured directory.

    Parameters
    ----------
    repo : Repository
        hatcher.v*.repository.Repository instance

    repo_dir : string
        The path to the repository in the structured directory.

    platforms : tuple
        Containing the platforms requested

    Yields
    ------
    tuple : Containing the SinglePlatformRepository object and a string of the
           path to the platform in the structured directory

    """
    plats_in_path = os.listdir(repo_dir)
    if platforms is not None:
        requested_plats = set(platforms)
        requested_plats_not_in_path = requested_plats.difference(plats_in_path)
        if requested_plats_not_in_path:
            click.secho(
                "Requested platforms `{0}` do not exist in the specified"
                " directory. Continuing with any remaining platforms.".format(
                    ', '.join(requested_plats_not_in_path)
                ),
                fg='red', err=True
            )
        valid_platforms = requested_plats.intersection(plats_in_path)
    else:
        valid_platforms = set(plats_in_path)

    for plat_name in valid_platforms:
        plat_dir = os.path.join(repo_dir, plat_name)
        plat_repo = repo.platform(plat_name)
        yield (plat_repo, plat_dir)


def iter_plat_repos_from_root(
        brood_client, api_root_dir, requested_org_repos=None,
        requested_platforms=None, create_missing=False
):
    """ Generator yielding every platform repository from the root directory.

    Parameters
    ----------
    brood_client : BroodClient
        hatcher.core.brood_client.BroodClient instance

    root_dir : string
        The path to the root of the structured directory.

    requested_org_repos : dict
        Dictionary of requested repositories keyed by organization

    requested_platforms : tuple
        Containing the platforms requested

    create_missing : bool
        Whether or not to create missing orgs and repos

    Yields
    ------
    tuple: Containing the SinglePlatformRepository object and a string of the
           path to the platform in the structured directory

    """
    if requested_org_repos is not None:
        requested_orgs = requested_org_repos.keys()
        ensure_specified_orgs_in_root(requested_orgs, api_root_dir)
    else:
        requested_orgs = os.listdir(api_root_dir)
        ensure_specified_orgs_exist(requested_orgs, brood_client)

    for (org, org_dir) in iter_orgs_from_path(
        brood_client, api_root_dir, requested_orgs
    ):
        if requested_org_repos is not None:
            requested_repos = requested_org_repos[org.name]
        else:
            requested_repos = None

        for (repo, repo_dir) in iter_repos_from_path(
            org, org_dir, requested_repos, create_missing
        ):
            for (plat_repo, plat_dir) in iter_plat_repos_from_path(
                 repo, repo_dir, requested_platforms):
                yield (plat_repo, plat_dir)


@hatcher.command(
    'import', help='Import exported artefacts into EDS.',
    api_versions=[1]
)
@click.option(
    '--artefact-kind', '-a', 'artefact_kinds', multiple=True,
    type=click.Choice([artefact.name for artefact in ArtefactKinds]),
    help="Artefact kind to import."
)
@click.option('--repository', '-r', 'requested_repos', multiple=True,
              help="Repository to import (must be in format `org/repo`)")
@click.option('--platform', '-p', 'requested_platforms', multiple=True,
              help="Platforms to import (e.g., `win-x86_64`)")
@click.option('--force', '-f', default=False, is_flag=True,
              help="Overwrite existing artefacts (default=False)")
@click.option('--create-missing', '-c', 'create_missing', default=False,
              is_flag=True,
              help="Create missing repositories")
@click.argument(
    'root_dir', nargs=1, type=click.Path(exists=True, dir_okay=True)
)
@pass_brood_client
def import_db(brood_client, artefact_kinds, requested_repos,
              requested_platforms, force, create_missing, root_dir):
    """ Import artefacts from a given structured directory into brood.
    `root_dir` must be <root_dir>/v<api_ver>/<org>/<repo>/<platform>/
    <artefact_kind>
    """
    if len(artefact_kinds) > 0:
        requested_artefact_kinds = [
            ArtefactKinds[name] for name in artefact_kinds]
    else:
        requested_artefact_kinds = ArtefactKinds

    if len(requested_repos) > 0:
        requested_repos_dict = defaultdict(list)
        for org_repo in requested_repos:
            org, repo = validate_requested_repo_format(org_repo)
            requested_repos_dict[org].append(repo)
    else:
        requested_repos_dict = None

    requested_platforms = requested_platforms or None

    api_version_root = os.path.join(
        root_dir, 'v{0}'.format(brood_client._api_version))

    for (plat_repo, plat_dir) in iter_plat_repos_from_root(
            brood_client, api_version_root, requested_repos_dict,
            requested_platforms, create_missing
    ):
        click.echo("Updating {0} for {1}".format(
            plat_repo._repository, plat_repo.name)
        )
        for artefact_kind in requested_artefact_kinds:
            artefact_dir = os.path.join(plat_dir, artefact_kind.name)
            artefact_files = find_artefacts(artefact_dir)
            upload_kwargs = {'overwrite': force, 'verify': True}

            if len(artefact_files) > 0:
                click.echo("Uploading {0}...".format(artefact_kind.name))
                if artefact_kind == ArtefactKinds.eggs:
                    upload_kwargs['enabled'] = False
                    batch_upload(
                        plat_repo.upload_egg, artefact_files, upload_kwargs,
                        plat_repo.reindex, plat_repo.egg_metadata
                    )
                elif artefact_kind == ArtefactKinds.runtimes:
                    batch_upload(
                        plat_repo._repository.upload_runtime,
                        artefact_files, upload_kwargs
                    )
                elif artefact_kind == ArtefactKinds.apps:
                    batch_upload(
                        plat_repo._repository.upload_app,
                        artefact_files, upload_kwargs
                    )
