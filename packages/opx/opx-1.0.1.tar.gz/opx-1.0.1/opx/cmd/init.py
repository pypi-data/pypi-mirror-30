import logging
import sys

from pathlib import Path

import click
import sh

from opx import debian
from opx import workspace

L = logging.getLogger('opx')

SOURCES = 'http://deb.openswitch.net/dists/{}/opx/source/Sources.gz'


@click.command()
@click.option('--url', '-u',
              default='git://github.com/open-switch/opx-manifest',
              help='Manifest repository URL')
@click.option('--manifest', '-m', default='default.xml',
              help='Manifest file within repository')
@click.option('--branch', '-b', default='master',
              help='Branch of repository to use')
@click.option('--release', '-r', default='',
              help='OPX release to use')
@workspace.pass_context
def init(
        ws: workspace.Workspace,
        url: str,
        manifest: str,
        branch: str,
        release: str,
):
    """Initialize an OpenSwitch workspace.

    Runs repo init and repo sync.

    URL, MANIFEST, and BRANCH are passed directly to repo.

    If a RELEASE is passed, all repos will be checked out to the correct commit
    for said release.

    Examples:

    opx init

        Create a workspace with the latest content from each repository.

    opx init --release 2.2.1

        Create a workspace with each repository's HEAD pointing to the tag of
        the package in the release. When building, missing dependencies are
        pulled from the exact set of packages used to build the release
        initially. A release can be recreated from code by running:

            opx build all --release 2.2.1 && opx assemble --release 2.2.1 -n 0
    """
    if ws.temp:
        root = Path.cwd()

        L.info('Initializing repositories...')
        try:
            # When we want streaming stdout/err, use _fg=True
            sh.repo.init(u=url, m=manifest, b=branch, _fg=True)
        except sh.ErrorReturnCode as e:
            L.error(f'RAN: {e.full_cmd}')
            sys.exit(1)

        ws = workspace.Workspace(root, temp=False)
        ws.save()

        L.info('Synchronizing repositories...')
        try:
            sh.repo.sync(no_clone_bundle=True, _fg=True)
        except sh.ErrorReturnCode as e:
            L.error(f'RAN: {e.full_cmd}')
            sys.exit(1)

        if release:
            packages_url = SOURCES.format(release)
            for k, v in debian.release_versions(packages_url).items():
                if Path(k).exists():
                    sh.git('-C', k, 'checkout', f'debian/{v}')
    else:
        L.error('This workspace has already been initialized.')
