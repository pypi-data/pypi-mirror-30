import logging
from pathlib import Path

import click
import docker

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@workspace.pass_context
def remove(ws) -> None:
    """Remove container from current workspace."""
    if not ws.temp and ws.cid:
        L.debug('[remove   ] Removing {}...'.format(ws.cid))
        client = docker.from_env()
        container = client.containers.get(ws.cid)
        container.remove(force=True)
        ws.cid = ''
        ws.save()
