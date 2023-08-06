"""Workspace module.

This module defines a common interface for working with component-based
projects.

Example:

    >>> ws = Workspace()
    >>> ws.buildpackage('opx-logging')
"""
import datetime
import logging
import itertools
import os
import platform
import shutil
import sys
import time

from configparser import ConfigParser
from pathlib import Path

import attr
import click
import docker
import dockerpty

from docker.models.containers import Container

L = logging.getLogger('opx')

# Define structure for saved data
CONFIG_MAP = {
    'cid': '',
}


@attr.s()
class Workspace(object):
    """An OpenSwitch development workspace.

    Each workspace is allowed one active container.

    Attributes:
        root (pathlib.Path): Location of workspace. The ``.workspace`` file
            is located in this directory.
        cid (str): Container ID of active workspace container. Will be ``''``
            if no container is running.
        temp (bool): The save method becomes a no-op when this is True.
    """
    root = attr.ib(
        default=Path.cwd(),
        validator=attr.validators.instance_of(Path),
    )
    cid = attr.ib(
        default='',
        validator=attr.validators.instance_of(str),
    )
    temp = attr.ib(
        default=True,
        validator=attr.validators.instance_of(bool),
    )

    def run(self, remove: bool = True, cmd: str = None):
        """Run a command inside a docker container.

        If no command is specified, an interactive bash session is launched.

        Args:
            remove: Deletes container on exit if True
            cmd: The command to run.
        """
        client = docker.from_env()

        image = f'opxhub/build:latest'
        _pull_if_necessary(client, image)

        if self.cid:
            container = client.containers.get(self.cid)
        else:
            container = _create_container(client, image, self.root, self.temp)
            self.cid = container.id
            self.save()

        # TODO: get actual tag from tags and save
        # if not any(dist in t for t in container.image.tags):

        L.debug(f'[container] Using container {container.name}')
        if cmd:
            L.debug(f'[command  ] {cmd}')

        try:
            container.start()
        except docker.errors.APIError as e:
            L.error('Failed to start container.')
            L.error(e.explanation)
            L.debug(f'Removing created container {container.name}.')
            container.remove()
            sys.exit(1)

        # let entrypoint run and user get created
        time.sleep(0.1)

        if cmd:
            cmd = f'sudo -u opx bash --login -c "{cmd}"'
        else:
            cmd = 'sudo -u opx bash'

        dockerpty.exec_command(client.api, container.id, command=cmd)

        if self.temp or remove:
            L.debug(f'[container] Stopping container {container.name}')
            container.stop()
            L.debug(f'[container] Removing container {container.name}')
            container.remove()
            self.cid = ''
            self.save()

    def buildpackage(
            self, pkg: str, release='unstable', rm=False, sort=False,
            tag=False, debian_dist='jessie',
    ):
        """Determines and runs the best build command for a ``pkg`` directory.

        Args:
            pkg: Represents the patch to build
            release: OPX release to build against
            rm: Deletes container on exit if True
            sort: Moves build artifacts into ``pkg/<pkg>/``.
            tag: Uses ``--git-tag`` option with ``git-buildpackage``.
            debian_dist: Debian distribution to build against
        """
        if not Path(pkg).exists():
            L.error(f'{pkg} does not exist.')
            sys.exit(1)

        L.debug(f'[build    ] Building {pkg} for {debian_dist} {release}.')

        try:
            cmd = build_command(Path(pkg), debian_dist, release, tag)
        except InvalidBuildPathException as e:
            L.error(e)
            sys.exit(1)

        self.run(remove=rm, cmd=cmd)

        if sort:
            Path(self.root / 'pkg' / pkg).mkdir(parents=True, exist_ok=True)
            dst = self.root / 'pkg' / pkg
        else:
            dst = self.root

        L.debug('[build    ] Collecting build artifacts.')
        for d in itertools.chain(
                self.root.glob('*.build'),
                self.root.glob('*.deb'),
                self.root.glob('*.dsc'),
                self.root.glob('*.tar.gz'),
        ):
            L.debug(f'[build    ] Found {d.name}!')
            shutil.move(str(d), str(dst / d.name))

    def save(self):
        """Write configuration to disk."""
        if not self.temp:
            parser = parser_read()
            if str(self.root) not in parser.sections():
                parser[str(self.root)] = {}

            parser[str(self.root)] = {k: getattr(self, k, v)
                                      for k, v in CONFIG_MAP.items()}

            parser_write(parser)
            Path(self.root / '.workspace').touch(0o644)

    @classmethod
    def load(cls, path: Path):
        """Load an OpenSwitch development workspace.

        Attempts to load the stored workspace at PATH. If the path is not in a
        workspace root, an InvalidWorkspaceException is raised. If the path is
        in a valid workspace but no records of the workspace are stored, a
        ForeignWorkspaceException is raised.

        Args:
            path: Recursively searches for valid workspace root.

        Returns:
            Workspace: Loaded Workspace object.

        Raises:
            ForeignWorkspaceException: If workspace root exists but is not
                saved.
            InvalidWorkspaceException: If no valid workspace exists.
        """
        root = _workspace_root(path)
        parser = parser_read()

        if str(root) not in parser.sections():
            raise ForeignWorkspaceException(
                'There is no record of this workspace in my database.'
            )

        # Read config values from parser
        config = {k: parser[str(root)].get(k, v)
                  for k, v in CONFIG_MAP.items()}

        return cls(root, temp=False, **config)


pass_context = click.make_pass_decorator(Workspace)


class ForeignWorkspaceException(Exception):
    """Raised for a workspace not created by this tool."""


class InvalidWorkspaceException(Exception):
    """Raised for an invalid path."""


class InvalidBuildPathException(Exception):
    """Raised when a build is requested in a Path without a build recipe."""


def build_command(path: Path, debian='jessie', release='unstable',
                  tag=False) -> str:
    """Parses a directory and returns a proper build command.

    Args:
        path: Directory to search.
        debian: Debian distribution to build against.
        release: OPX release to build against.
        tag: Tag for release after building.

    Returns:
        str: Build command to run.
    """
    if Path(path / 'control').exists():
        cmd = 'equivs-build {}/control'.format(path)

    elif Path(path / 'debian' / 'control').exists():

        if Path(path / 'debian' / 'rules').exists():
            # Create chroot for building if not unstable
            cmd = f"sudo /pbuilder_update.sh '{release}'; "

            # Index local packages
            cmd += 'cd /mnt; apt-ftparchive packages . >Packages 2>/dev/null; '

            dist = debian if release == 'unstable' else f'{debian}_{release}'

            # Run git-buildpackage
            cmd += (f'cd {path};'
                    f' gbp buildpackage'
                    f' --git-dist={dist}'
                    f' --git-pbuilder'
                    f' --git-ignore-branch'
                    f' --git-ignore-new')
            if tag:
                cmd += ' --git-tag'
        else:
            # Simple packaging for opx-core, so far
            cmd = 'dpkg-deb -b opx-core .'.format(path)

    else:
        raise InvalidBuildPathException('No build recipe found for this path.')

    return cmd


def cleanup_removed_containers(parser: ConfigParser):
    """Delete removed containers from persistent configuration.

    Args:
        parser: Parser to scan for missing containers.
    """
    client = docker.from_env()
    for s in parser.sections():
        if parser[s].get('cid', '') != '':
            cid = parser[s].get('cid')
            try:
                client.containers.get(cid)
            except docker.errors.NotFound:
                L.warning('Removing missing container {} from {}'
                          .format(cid[:10], s))
                del parser[s]['cid']


def cleanup_deleted_workspaces(parser: ConfigParser):
    """Remove deleted workspaces from persistent configuration.

    Args:
        parser: Parser to scan for missing workspaces.
    """
    delete = [s for s in parser.sections()
              if not Path(s + '/.workspace').exists() and s != 'DEFAULT']
    for d in delete:
        del parser[d]


def parser_read(location: Path = None) -> ConfigParser:
    """Read program configuration and return parser.

    Args:
        location: Path to check for. Checks the default program configuration
            location if None is submitted.

    Returns:
        ConfigParser: Loaded from directory.
    """
    configfile = location or Path(click.get_app_dir('opx')) / 'config'
    configfile.parent.mkdir(parents=True, exist_ok=True)
    parser = ConfigParser()
    parser.read(str(configfile))
    return parser


def parser_write(parser: ConfigParser):
    """Write program configuration to default location..

    Args:
        parser: Parser to save.
    """
    with Path(click.get_app_dir('opx') + '/config').open('w') as f:
        parser.write(f)


def _create_container(client, image: str, mnt_dir: Path,
                      temp=False) -> Container:
    """Returns created container with MNT_DIR mounted at /mnt."""
    L.debug('[container] Creating new container!')
    L.debug('[container] Mounting {} to /mnt'.format(mnt_dir))

    # collect volumes to mount
    volumes = {
        str(mnt_dir.resolve()): {'bind': '/mnt', 'mode': 'rw'},
    }

    gitconfig = Path.home() / '.gitconfig'
    if gitconfig.exists():
        volumes.update({
            str(gitconfig): {'bind': '/home/opx/.gitconfig', 'mode': 'ro'},
        })

    if platform.system() == 'Darwin':
        volumes.update({
            str(Path('/private/etc/localtime').resolve()): {
                'bind': '/etc/localtime', 'mode': 'ro'
            },
        })
    elif platform.system() == 'Linux':
        volumes.update({
            str(Path('/etc/localtime').resolve()): {
                'bind': '/etc/localtime', 'mode': 'ro'
            },
        })

    return client.containers.create(
        auto_remove=False,
        command='bash',
        detach=False,
        environment={
            'LOCAL_UID': os.getuid(),
            'LOCAL_GID': os.getgid(),
        },
        hostname=image.split(':')[-1].replace('.', '_'),
        image=image,
        labels={
            'user': os.getenv('USER'),
        },
        name='{}{}_{}_{}'.format(
            'temp_' if temp else '',
            os.getenv('USER'),
            *mnt_dir.resolve().parts[-2:]
        ),
        privileged=True,
        stdin_open=True,
        tty=sys.stdin.isatty() and sys.stdout.isatty(),
        volumes=volumes,
    )


def _pull_if_necessary(client: docker.DockerClient, image: str):
    """Pull image if last pull was >7 days ago."""
    parser = parser_read()
    now = datetime.datetime.now()

    last_pull = parser['DEFAULT'].getfloat('last_pull', now.timestamp())
    if last_pull == now.timestamp():
        pull = True
    else:
        last_pull_time = datetime.datetime.fromtimestamp(last_pull)
        pull = last_pull_time <= now - datetime.timedelta(days=7)

    if pull:
        L.info('More than a week since last pull, pulling {}...'.format(image))

        try:
            client.images.pull(image)
        except docker.errors.NotFound:
            L.error("Couldn't pull {}.".format(image))
            sys.exit(1)

        parser['DEFAULT']['last_pull'] = str(now.timestamp())
        parser_write(parser)


def _workspace_root(path: Path) -> Path:
    """Search PATH and parents for the existence of a .workspace file."""
    if not path.exists():
        raise InvalidWorkspaceException('Path does not exist.')
    elif Path(path / '.workspace').exists() or Path(path / '.repo').is_dir():
        L.debug('[workspace] Found workspace in {}!'.format(path))
        return path
    elif path == Path(Path().resolve().root):
        L.debug('[workspace] No workspace found...')
        raise InvalidWorkspaceException('Not in a workspace.')

    # recurse
    return _workspace_root(path.parent)
