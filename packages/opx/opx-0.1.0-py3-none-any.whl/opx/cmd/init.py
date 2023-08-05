import logging
import sys

from pathlib import Path

import click
import sh

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--dist', default='unstable',
              help='OPX distribution to build against.')
@click.option('--url', '-u',
              default='git://git.openswitch.net/opx/opx-manifest',
              help='Manifest repository URL')
@click.option('--manifest', '-m', default='default.xml',
              help='Manifest file within repository')
@click.option('--branch', '-b', default='master',
              help='Branch of repository to use')
@click.argument('projects', nargs=-1,)
@workspace.pass_context
# projects does not have a type since python3.4 does not have the typing module
def init(ws, dist: str, url: str, manifest: str, branch: str, projects):
    """Initialize an OpenSwitch workspace.

    Runs repo init and repo sync. DIST will be saved in workspace configuration.

    URL, MANIFEST, BRANCH, and PROJECTS are passed directly to repo.

    Examples:

    opx init

        Create a workspace with the latest content from each repository.

    opx init --dist stable

        Create a workspace with the latest stable packages.

    opx init --dist 2.2.1

        Create a workspace for the 2.2.1 release.

    opx init --release 2.2 (coming soon)

        Create a workspace with each repository's HEAD pointing to the tag of
        the package in the release. When building, missing dependencies are
        pulled from the exact set of packages used to build the release
        initially. A release can be recreated from code by running:

            opx build all && opx assemble --dist 2.2 -n 0
    """
    if ws.temp:
        root = Path.cwd()

        L.info('Initializing repositories...')
        try:
            # When we want streaming stdout/err, use _fg=True
            sh.repo.init(u=url, m=manifest, b=branch, _fg=True)
        except sh.ErrorReturnCode as e:
            L.error('RAN: {}'.format(e.full_cmd))
            sys.exit(1)

        ws = workspace.Workspace(root, dist, temp=False)
        ws.save()

        L.info('Synchronizing repositories...')
        try:
            sh.repo.sync(_fg=True)
        except sh.ErrorReturnCode as e:
            L.error('RAN: {}'.format(e.full_cmd))
            sys.exit(1)
    else:
        L.error('This workspace has already been initialized.')
