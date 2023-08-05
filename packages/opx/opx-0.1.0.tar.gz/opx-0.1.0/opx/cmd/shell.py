import logging

import click

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--dist',
              help='Change OPX distribution to build against.')
@click.option('--rm/--no-rm', default=False,
              help='Remove container when command exits.')
@workspace.pass_context
def shell(ws, dist: str, rm: bool) -> None:
    """Launch an OpenSwitch development container.

    Creates a build container and runs bash inside.

    Build dependencies are pulled from the DIST distribution of OPX if not
    present locally.
    """
    ws.run(dist=dist or ws.dist, remove=rm)
