import logging

import click

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('-b', default='opx-onie-installer/release_bp/OPX_dell_base.xml',
              help='Installer blueprint to use')
@click.option('-n', default=9999,
              help='Release number')
@click.option('-s', default='',
              help='Release suffix')
@click.option('--debug/--no-debug', default=False,
              help='Run opx_rel_pkgasm with --debug.')
@click.option('--dist',
              help='OPX distribution to build against.')
@click.option('--rm/--no-rm', default=False,
              help='Remove container when command exits.')
@workspace.pass_context
def assemble(ws, b, n, s, debug: bool, dist: str, rm: bool) -> None:
    """Assemble an OpenSwitch ONIE installer.

    Local packages always have the highest priority. If packages are not found
    locally, they are pulled from the chosen DIST on deb.openswitch.net.
    The DIST chosen is used in the image for package updates.

    Examples:

    opx assemble

        Create an ONIE installer. Installer will have version "unstable.9999".
        Packages will be pulled from 'http://deb.openswitch.net/ unstable main'

    opx assemble --dist testing -n 5

        Create an ONIE installer. Installer will have version "testing.5".
        Packages will be pulled from 'http://deb.openswitch.net/ testing main'

    opx assemble --dist 2.2.0 -n 0

        Create an ONIE installer. Installer will have version "2.2.0".
        Packages will be pulled from 'http://deb.openswitch.net/ 2.2.0 main'
   """
    dist = dist or ws.dist
    cmd = 'opx_rel_pkgasm.py -b {} -n {} --dist {}'.format(b, n, dist)
    if s != "":
        cmd += ' -s {s}'.format(s=s)
    if debug:
        cmd += ' --debug -v 9'

    ws.run(rm, dist or ws.dist, cmd)
