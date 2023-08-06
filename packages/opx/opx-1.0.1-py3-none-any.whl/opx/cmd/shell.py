import logging

import click

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--rm/--no-rm', default=False,
              help='Remove container when command exits.')
@workspace.pass_context
def shell(ws: workspace.Workspace, rm: bool):
    """Launch an OpenSwitch development container.

    Creates a build container and runs bash inside.
    """
    ws.run(remove=rm)
