import sys

from pathlib import Path

import click
import click_completion
import click_log

from opx import workspace
from opx.cmd import (
    assemble, build, init, release, remove, shell, status,
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
opx.add_command(release)
opx.add_command(remove)
opx.add_command(shell)
opx.add_command(status)
