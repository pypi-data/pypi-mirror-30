from collections import Mapping
import enum
import os

import click
from concurrent.futures import ThreadPoolExecutor, as_completed

from hatcher.testing import python_tag_from_metadata
from .main import hatcher
from .utils import makedirs, pass_brood_client


MAX_WORKERS = 4


@enum.unique
class ArtefactKinds(enum.Enum):
    eggs = 0
    runtimes = 1


def iter_repos_from_brood(brood_client):
    """ Generator that yield a Repository for every repository and every
    organization in a brood_client.

    Parameter
    ---------
    brood_client: BroodClient
        hatcher.core.brood_client.BroodClient instance

    Yields
    ------
    Repository: hatcher.core.v*.repository.Repository instance

    """
    for org_name in brood_client.list_organizations():
        org = brood_client.organization(org_name)
        for repo_name in org.list_repositories():
            yield org.repository(repo_name)


def iter_plat_repos(repos, platforms):
    """ Generator that yield a SinglePlatformRespository for every repository,
    platform combination.

    Parameters
    ----------
    repos: list
        Containing Repository objects
    platforms: list
        Containing strings of valid platforms

    Yields
    ------
    SinglePlatformRepository:
        hatcher.core.v*.repository.SinglePlatformRespository instance

    """
    for repo in repos:
        for platform in platforms:
            yield repo.platform(platform)


def download_runtimes(plat_repo, runtimes_metadatas, artefact_root):
    """ Download runtimes into a structured directory.

    Parameters
    ----------

    plat_repo: SinglePlatformRepository
        hatcher.core.v*.repository.SinglePlatformRepository instance

    runtimes: dict
        Containing metadata dictionaries keyed by sha256

    artefact_root: path
        <target_root>/<meta_ver>/<org>/<repo>/<plat>/runtimes

    """
    makedirs(artefact_root)
    with click.progressbar(length=len(runtimes_metadatas)) as bar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {}
            for runtime_meta in runtimes_metadatas.values():
                task = executor.submit(
                    plat_repo.download_runtime,
                    runtime_meta['implementation'],
                    runtime_meta['version'],
                    artefact_root,
                    runtime_meta['sha256'],
                )
                tasks[task] = runtime_meta

            for task in as_completed(tasks):
                try:
                    task.result()
                    bar.update(1)
                except Exception:
                    # Move to the line after the progress bar
                    click.echo('', err=True)
                    click.secho(
                        'Error downloading {0}'.format(
                            tasks[task]['filename']),
                        fg='red', err=True
                    )
                    raise


def find_eggs_for_plat_repo(brood_client, plat_repo):
    """ Find the unique eggs for a given platform repository. Some eggs are
    listed in multiple indexed python tags, so we want to ensure that each
    egg is only referenced once to prevent duplication.

    Parameters
    ----------

    brood_client: BroodClient
        hatcher.core.brood_client.BroodClient instance

    plat_repo: SinglePlatformRepository
        hatcher.core.v*.repository.SinglePlatformRepository instance

    Returns
    -------
    dict: Containing egg metadata indexed by sha256

    """
    eggs_dict = {}
    for python_tag in sorted(brood_client.list_python_tags()):
        egg_index = plat_repo.egg_index(python_tag)
        for _, index_entry in egg_index.items():
            metadata = plat_repo.egg_metadata(
                python_tag,
                index_entry['name'],
                '-'.join(
                    [str(index_entry['version']), str(index_entry['build'])]
                ),
            )
            sha256_key = metadata['sha256']

            if sha256_key not in eggs_dict:
                eggs_dict[sha256_key] = metadata.copy()
                eggs_dict[sha256_key]['indexed_tag'] = python_tag

    return eggs_dict


def download_eggs(plat_repo, egg_metadatas, artefact_root):
    """ Download eggs into a structured directory.

    Parameters
    ----------

    plat_repo: SinglePlatformRepository
        hatcher.core.v*.repository.SinglePlatformRepository instance

    egg_metadatas: dict
        Dictionary of egg metadata keyed by sha256

    artefact_root: path
        target_root/<meta_ver>/<org>/<repo>/<plat>/eggs

    """
    with click.progressbar(length=len(egg_metadatas)) as bar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {}
            for egg_meta in egg_metadatas.values():
                py_tag = python_tag_from_metadata(egg_meta) or 'None'
                target = os.path.join(artefact_root, py_tag)
                filename = egg_meta.get('filename', None)
                if filename is None:
                    filename = '{}-{}.egg'.format(
                        egg_meta['name'], egg_meta['full_version'])
                makedirs(target)
                task = executor.submit(
                    plat_repo.download_egg,
                    egg_meta['indexed_tag'],
                    egg_meta['name'],
                    egg_meta['full_version'],
                    target,
                    egg_meta['sha256'],
                    filename,
                )
                tasks[task] = egg_meta

            for task in as_completed(tasks):
                try:
                    task.result()
                    bar.update(1)
                except Exception:
                    bad_egg_meta = tasks[task]
                    # Move to the line after the progress bar
                    click.echo('', err=True)
                    click.secho(
                        'Error downloading {0}'.format(
                            '-'.join(bad_egg_meta['name'],
                                     bad_egg_meta['full_version'],)
                        ),
                        fg='red', err=True
                    )
                    raise


def unpack_index(index):
    """ Unpack index into a dictionary of metadata keyed by sha256.

    Parameter
    ---------
    index: dict
        Index returned from brood_client

    Returns
    -------
    dict: Containing metadata keyed by sha256

    """
    def find_metadata(artefact_index):
        for key, value in artefact_index.items():
            if not isinstance(value, Mapping):
                yield artefact_index
            else:
                for new_index in find_metadata(value):
                    yield new_index

    metadatas = {}
    for meta in find_metadata(index):
        sha256_key = meta['sha256']
        metadatas[sha256_key] = meta

    return metadatas


@hatcher.command(
    'export', help='Export artefacts from EDS.',
    api_versions=[0, 1]
)
@click.option(
    '-a', '--artefact-kinds', multiple=True,
    default=[artefact.name for artefact in ArtefactKinds],
    type=click.Choice([artefact.name for artefact in ArtefactKinds]),
    help="Artefact kind to export."
)
@click.option('-r', '--repositories', multiple=True,
              help="Repository to export from (must be in format `org/repo`)")
@click.option('-p', '--platforms', multiple=True,
              help="Plaform to export for. (e.g., `win-x86_64`)")
@click.argument(
    'target-dir', nargs=1, type=click.Path(exists=False, dir_okay=True),
)
@pass_brood_client
def export_db(
        brood_client, artefact_kinds, repositories, platforms, target_dir):
    """ Export all of the desired artefact kinds and repositories into a
    structured directory with the following organization:
    `target_dir/<meta_ver>/<org>/<repo>/<plat>/<artefact-kind>/<python_tag>/
    <file>`.

    """
    if repositories:
        requested_repos = [
            brood_client.organization(org).repository(repo) for
            org_repo in repositories for org, repo in [org_repo.split('/')]
        ]
    else:
        requested_repos = [
            repo for repo in iter_repos_from_brood(brood_client)
        ]
    requested_platforms = platforms or brood_client.list_platforms()
    metadata_version = brood_client._api_version

    # Do not attempt to export runtimes for api version 0
    if (metadata_version == 0 and 'runtimes' in artefact_kinds):
        click.secho(
            "Exporting runtimes is not supported for api version 0",
            fg='red', err=True
        )
        artefact_kinds = list(artefact_kinds)
        artefact_kinds.remove('runtimes')

    for platform_repo in iter_plat_repos(requested_repos, requested_platforms):
        org_name = platform_repo._repository.organization_name
        repo_name = platform_repo._repository.name
        platform = platform_repo.name

        plat_root = os.path.join(
            target_dir, 'v{0}'.format(metadata_version), org_name, repo_name,
            platform
        )

        for artefact_kind in artefact_kinds:
            artefact_root = os.path.join(plat_root, artefact_kind)

            if artefact_kind == 'runtimes':
                runtimes_index = platform_repo.runtime_index()
                if runtimes_index:
                    rt_metadata = unpack_index(runtimes_index)
                    click.echo(
                        "Exporting runtimes from {0}/{1} for {2}".format(
                            org_name, repo_name, platform
                        )
                    )
                    download_runtimes(
                        platform_repo, rt_metadata, artefact_root)

            if artefact_kind == 'eggs':
                eggs = find_eggs_for_plat_repo(brood_client, platform_repo)
                if len(eggs) > 0:
                    click.echo(
                        "Exporting eggs from {0}/{1} for {2}".format(
                            org_name, repo_name, platform
                        )
                    )
                    download_eggs(platform_repo, eggs, artefact_root)
