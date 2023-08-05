import logging

from pathlib import Path

import click

from opx import debian
from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--build-deps/--no-build-deps', default=False,
              help='Build dependencies first.')
@click.option('--dist',
              help='Change OPX distribution to build against.')
@click.option('--rm/--no-rm', default=False,
              help='Remove container when command exits.')
@click.option('--sort/--no-sort', default=True,
              help='Move artifacts from workspace to workspace/pkg/repo/.')
@click.argument('repo')
@workspace.pass_context
def build(ws, build_deps: bool, dist: str, rm: bool, sort: bool, repo):
    """Build one or all OpenSwitch repositories.

    REPO is built using git-buildpackage inside a container.

    OpenSwitch build dependencies are pulled from the DIST distribution if not
    present locally.
    """
    # Create build-order list of required OPX packages
    if build_deps or repo == 'all':
        repos = debian.opx_build_dependencies(repo)
    else:
        repos = [repo]

    for repo in repos:
        ws.buildpackage(repo, rm, dist or ws.dist, sort, tag=False)
