"""CLI module.

This module serves as the entrypoint to the program.

* ``AliasedGroup`` enables command aliases.
* ``opx`` runs the program itself, and is used as the entrypoint.
"""
import sys

from pathlib import Path

import click
import click_completion
import click_log
import sh

from opx import workspace
from opx.cmd import (
    assemble, build, init, publish, remove, shell, status,
)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

click_completion.init()
click_log.basic_config('opx')


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(prog_name='OpenSwitch Development Tool')
@click_log.simple_verbosity_option('opx')
@click.pass_context
def opx(ctx):
    if not _check_dependencies():
        sys.exit(1)

    parser = workspace.parser_read()
    workspace.cleanup_deleted_workspaces(parser)
    workspace.cleanup_removed_containers(parser)
    workspace.parser_write(parser)

    pwd = Path.cwd()

    try:
        ctx.obj = workspace.Workspace.load(pwd)
    except workspace.ForeignWorkspaceException:
        click.secho('I have no knowledge of this workspace.',
                    fg='magenta')
        click.secho('Shall I add it to my archives? [yn] ',
                    fg='magenta', nl=False)
        c = click.getchar()
        click.echo()
        if c == 'y':
            ctx.obj = workspace.Workspace(pwd, temp=False)
            ctx.obj.save()
        elif c == 'n':
            ctx.obj = workspace.Workspace(pwd)
        else:
            click.secho('Invalid key. Aborting...', fg='red')
            sys.exit(1)
    except workspace.InvalidWorkspaceException:
        ctx.obj = workspace.Workspace(pwd)


opx.add_command(assemble)
opx.add_command(build)
opx.add_command(init)
opx.add_command(publish)
opx.add_command(remove)
opx.add_command(shell)
opx.add_command(status)


def _check_dependencies() -> bool:
    try:
        # Check if these commands exist in our PATH
        sh.docker
        sh.git
        sh.repo
    except sh.CommandNotFound as e:
        click.secho(f'error: {e} not found in $PATH.',
                    fg='red', bold=True)
        return False

    return True
