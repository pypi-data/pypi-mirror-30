#
# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import json
import os.path
from requests import HTTPError
import sys
import time

import click
from tabulate import tabulate

from ..core.utils import (
    EggMetadata,
    EggNameSorter,
    AppSorter,
)
from .common import allow_assume_yes, request_confirmation
from .main import hatcher
from .utils import (
    pass_organization, pass_repository, HTTPErrorHandlingUploadCommand,
    upload_context_table
)


@hatcher.group('repositories', api_versions=[0, 1])
def repositories():
    """Perform operations on repositories.
    """


@hatcher.group('apps', api_versions=[0, 1])
def apps():
    """Perform operations on apps.
    """


@hatcher.group('eggs', api_versions=[0, 1])
def eggs():
    """Perform operations on eggs.
    """


@hatcher.group('runtimes', api_versions=[0, 1])
def runtimes():
    """Perform operations on runtimes.
    """


@repositories.command(
    'list', api_versions=[0, 1],
    help='List all of the repositories from a given organization.')
@click.argument('organization')
@pass_organization
def list_repositories(organization):
    for repository in sorted(organization.list_repositories()):
        print(repository)


@repositories.command('create', help='Create a new repository.',
                      api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('description')
@pass_organization
def create_repository(organization, repository, description):
    organization.create_repository(repository, description)


@repositories.command('delete', help='Delete a repository.',
                      api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.option('--force', default=False, is_flag=True)
@allow_assume_yes
@pass_repository
def delete_repository(repository, force, assume_yes):
    if not assume_yes:
        prompt = "{0} will be deleted. Proceed?".format(repository)
        request_confirmation(prompt)

    repository.delete(force=force)


@apps.command('list', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@pass_repository
def list_apps(repository, platform):
    """List all apps in a repository.
    """
    sort_key = lambda app: AppSorter(*app)
    apps = repository.platform(platform).list_apps()
    sorted_apps = sorted(apps, key=sort_key)
    headers = ['App Name', 'Version', 'Python Tag']
    click.echo(tabulate(sorted_apps, headers=headers, floatfmt='f'))


@apps.command('upload', help='Upload a single app to a repository.',
              cls=HTTPErrorHandlingUploadCommand, api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.pass_context
def upload_app(ctx, organization, repository, filename, force):
    repo = ctx.obj.organization(organization).repository(repository)
    context = upload_context_table(ctx, 'App', filename, repo)
    click.echo(tabulate(context, tablefmt='plain'))
    repo.upload_app(filename, overwrite=force)


@apps.command('metadata', help='Get the metadata for a single app.',
              api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('app_id')
@click.argument('version')
@pass_repository
def app_metadata(repository, platform, python_tag, app_id, version):
    metadata = repository.platform(platform).app_metadata(
        python_tag, app_id, version)
    print(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('metadata', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@pass_repository
def egg_metadata(repository, platform, python_tag, name, version):
    """Get the metadata for a single egg.
    """
    metadata = repository.platform(platform).egg_metadata(
        python_tag, name, version)
    click.echo(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('download', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@click.argument('destination', required=False)
@pass_repository
def download_egg(repository, platform, python_tag, name, version,
                 destination=None):
    """Download an egg.
    """
    if destination is None:
        destination = os.getcwd()

    length, iterator = repository.platform(platform).iter_download_egg(
        python_tag, name, version, destination)

    with click.progressbar(length=length) as bar:
        for chunk_size in iterator:
            bar.update(chunk_size)


@eggs.command('delete', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@allow_assume_yes
@pass_repository
def delete_egg(repository, platform, python_tag, name, version, assume_yes):
    """Delete an egg.
    """
    if not assume_yes:
        prompt = "{0}-{1} ({2}) will be deleted from {3}. Proceed?".format(
            name, version, python_tag, repository)
        request_confirmation(prompt)

    repository.platform(platform).delete_egg(python_tag, name, version)


@eggs.command('upload', help='Upload a single egg to a repository.',
              cls=HTTPErrorHandlingUploadCommand, api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.option('--verify/--no-verify', default=False)
@click.pass_context
def upload_egg(ctx, organization, repository, platform, filename, force,
               verify):
    repo = ctx.obj.organization(organization).repository(repository)
    repo_plat = repo.platform(platform)
    context = upload_context_table(
        ctx, 'Egg', filename, repo, platform=platform)
    click.echo(tabulate(context, tablefmt='plain'))
    repo_plat.upload_egg(filename, overwrite=force, verify=verify)


def egg_metadata_verified(metadata_func, local_metadata):
    """Check if the remote egg is found

    This calls the platform_repository.egg_metadata function given by
    metadata_func. This in turn calls the command "hatcher eggs metadata"
    with the following result:
    - If the eggs exists the call returns an http response of 200 with the
    remote egg metadata and this function returns TRUE.
    - If the egg does not exist then an http response of 404 is returned and
    this function returns FALSE.

    Parameters
    ----------
    metadata_func: the egg_metadata() method of platform_repository
    local_metadata: the local egg metadata used to get parameters
        (versus the remote metadata which is not returned here).
    Returns: TRUE if the remote egg is found
             FALSE if the remote egg is not found
    """
    try:
        metadata_func(
            local_metadata.python_tag,
            local_metadata.name,
            local_metadata.full_version
        )
    except HTTPError as exc:
        if exc.response.status_code != 404:
            raise
        # Http response code 404 means egg not found
        return False
    # Http response code 200 means egg is found
    return True


def batch_upload(upload_func, artefacts, upload_kwargs=None, index_func=None,
                 metadata_func=None, index_timeout=10):
    """ Upload the artefacts for a given artefact kind into brood.

    Parameters
    ----------
    upload_func: func
        Function that will perform the upload
    artefacts: list
        Contains the filepaths to the artefacts
    upload_kwargs: dict
        Contains the keyword arguments to be passed to the upload function.
    index_func: func
        Function that will be used to update the index.
    index_timeout: int
        Number of attempts to check for eggs before indexing.
        There is a wait time of 1 second between attempts.
    """
    kwargs = upload_kwargs or {}
    with click.progressbar(length=len(artefacts)) as bar:
        for artefact in artefacts:
            try:
                upload_func(artefact, **kwargs)
                bar.update(1)
            except Exception:
                # Move to the line after the progress bar
                click.echo('', err=True)
                click.secho(
                    'Error uploading {0}'.format(artefact),
                    fg='red', err=True
                )
                raise

    if index_func is not None:
        if not callable(metadata_func):
            raise ValueError(
                "Must have a valid egg_metadata function"
                " if indexing is turned on."
            )
        unverified_metadata = [EggMetadata.from_file(egg) for egg in artefacts]
        for t in range(index_timeout):
            if not unverified_metadata:
                # No eggs left to verify
                break
            for metadata in list(unverified_metadata):
                if egg_metadata_verified(metadata_func, metadata):
                    unverified_metadata.remove(metadata)
            # sleep before next attempt to verify eggs
            time.sleep(1)
        else:
            click.echo(
                "Time out waiting for eggs to be available for indexing."
            )
            sys.exit(1)

        click.echo("Verified uploaded eggs for indexing after"
                   " {0} of {1} attempts.".format(t, index_timeout))
        click.echo("Updating the index...")
        index_func(artefacts)


@eggs.command('batch-upload', api_versions=[0, 1],
              cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('eggs', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--force', default=False, is_flag=True)
@click.option('--index/--no-index', default=True,
              help='Control automatic indexing of new eggs after upload')
@click.option('--index_timeout', default=10,
              help='Number of attempts to verify uploaded eggs before indexing.')
@click.pass_context
def batch_upload_eggs(ctx, organization, repository, platform, eggs, force,
                      index, index_timeout):
    """Upload a batch of eggs.

    The upload will terminate on the first failure, and the indexing will be
    'transactionaly' in the sense that it will happen exactly once, once all
    the files have been successfully uploaded.
    """
    repo = ctx.obj.organization(organization).repository(repository)
    platform_repository = repo.platform(platform)

    egg_count = len(eggs)
    egg_count_text = '{0} egg{1} to upload'.format(
        egg_count, 's' if egg_count != 1 else '')
    context = upload_context_table(
        ctx, 'Batch egg', egg_count_text, repo, platform=platform)
    click.echo(tabulate(context, tablefmt='plain'))

    upload_kwargs = {'overwrite': force, 'enabled': False, 'verify': True}

    if index:
        batch_upload(
            platform_repository.upload_egg, eggs, upload_kwargs,
            platform_repository.reindex,
            platform_repository.egg_metadata,
            index_timeout
        )
    else:
        batch_upload(
            platform_repository.upload_egg, eggs, upload_kwargs
        )


@eggs.command('update-index', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('eggs', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@pass_repository
def index_eggs(repository, platform, eggs):
    """Enable a batch of eggs and re-index the repository.
    """
    repository.platform(platform).reindex(eggs)


@eggs.command('list', help='List all eggs in a repository',
              api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@pass_repository
def list_eggs(repository, platform, python_tag):
    eggs_iter = sorted(repository.platform(platform).list_eggs(python_tag),
                       key=lambda egg: EggNameSorter(egg['name'].lower()))
    eggs = [(egg['name'], egg['python_tag']) for egg in eggs_iter]
    headers = ['Egg Name', 'Python Tag']
    click.echo(tabulate(eggs, headers=headers))
