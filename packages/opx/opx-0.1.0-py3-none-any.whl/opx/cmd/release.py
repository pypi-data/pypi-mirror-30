import logging
import re
import sys

from pathlib import Path

import click
import sh

from opx import workspace

L = logging.getLogger('opx')


@click.command()
@click.option('--build/--no-build', default=True,
              help='Tag without verification.')
@click.option('--push/--no-push', default=True,
              help='Push tags to review.openswitch.net.')
@click.option('--push-url', default='ssh://review.openswitch.net:29418',
              help='Git server to push tags to.')
@click.argument('repo')
@workspace.pass_context
def release(ws, build: bool, push: bool, push_url: str, repo: str):
    """Trigger a release by tagging and pushing.

    Runs in a one-off container. Results are found in pkg/REPO.

    The REPO is built using git-buildpackage inside a container.
    Build dependencies are pulled from the testing distribution of OPX if not
    present locally.
    """

    # Run in temporary workspace as one-time container
    if not ws.temp:
        ws = workspace.Workspace(ws.root, 'testing', temp=True)

    if build:
        # TODO: catch sigint, might have to build into container
        ws.buildpackage(repo, rm=True, sort=True, tag=True, dist='testing')
    else:
        if not Path(repo).exists():
            L.error('{} does not exists.'.format(repo))
            sys.exit(1)

        with Path(ws.root / repo / 'debian/changelog').open() as f:
            version = re.search(r'.*\((.*)\).*', f.readline()).group(1)

        click.secho('Releasing {} version {}. Press [y] to confirm.'
                    .format(repo, version), fg='green', nl=False)
        c = click.getchar()
        click.echo()
        if c != 'y':
            click.secho('Invalid key. Aborting...', fg='red')
            sys.exit(1)

        L.info('Tagging repository...')
        try:
            sh.git.tag(
                'debian/{}'.format(version),
                a=True,
                m='{} Debian release {}'.format(repo, version),
                _cwd=str(repo),
            )
        except sh.ErrorReturnCode as e:
            L.error(e)
            sys.exit(1)

    if push:
        L.info('Pushing tags...')
        try:
            sh.git.push(
                '{}/opx/{}'.format(push_url, repo),
                tags=True,
                _cwd=str(repo),
            )
        except sh.ErrorReturnCode as e:
            L.error(e)
            sys.exit(1)
