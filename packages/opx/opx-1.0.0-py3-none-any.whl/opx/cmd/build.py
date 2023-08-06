import logging

import click

from opx import debian
from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--build-deps/--no-build-deps', default=False,
              help='Build dependencies first.')
@click.option('--release', '-r', default='unstable',
              help='OPX release to build against.')
@click.option('--rm/--no-rm', default=False,
              help='Remove container when command exits.')
@click.option('--sort/--no-sort', default=True,
              help='Move artifacts from workspace to workspace/pkg/repo/.')
@click.argument('repo')
@workspace.pass_context
def build(
        ws: workspace.Workspace,
        build_deps: bool,
        release: str,
        rm: bool,
        sort: bool,
        repo: str,
):
    """Build one or all OpenSwitch repositories.

    REPO is built using git-buildpackage inside a container.

    OpenSwitch build dependencies are pulled from RELEASE if not present
    locally.
    """
    # Create build-order list of required OPX packages
    if build_deps or repo == 'all':
        repos = debian.opx_build_dependencies(repo)
    else:
        repos = [repo]

    for repo in repos:
        ws.buildpackage(repo, release, rm, sort, tag=False)
