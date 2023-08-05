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

# Saved Workspace attributes
CONFIG_MAP = {
    'dist': 'unstable',
    'cid': '',
}


@attr.s()
class Workspace(object):
    """An OpenSwitch development workspace.

    If marked as TEMP, save() is a no-op.
    """
    # The root directory of the workspace; where .workspace will be created.
    root = attr.ib(validator=attr.validators.instance_of(Path))

    # The Docker label, and consequently the Debian distribution, to use
    # for assembling installers, pulling dependencies, and more.
    dist = attr.ib(default='unstable',
                   validator=attr.validators.instance_of(str))

    # The container id for the workspace, will be '' if no container is alive.
    cid = attr.ib(default='',
                  validator=attr.validators.instance_of(str))

    # A temporary workspace has no .workspace file and can not be saved.
    temp = attr.ib(default=True,
                   validator=attr.validators.instance_of(bool))

    def run(self, remove: bool = True, dist='unstable', cmd: str = None):
        """Run a command inside a docker container.

        If no command is specified, an interactive shell is launched.
        """
        client = docker.from_env()

        image = 'opxhub/build:{}'.format(dist)
        _pull_if_necessary(client, image)

        if self.cid:
            container = client.containers.get(self.cid)
        else:
            container = _create_container(client, image, self.root, self.temp)
            self.dist = dist
            self.cid = container.id
            self.save()

        # Argument dist differs from running container
        if not any(dist in t for t in container.image.tags):
            L.info('A container with a different distribution ({old}) is '
                   'currently running.\nPress [y] to confirm the change.'
                   .format(old=self.dist,))
            if click.getchar() == 'y':
                L.info('Recreating container {}...'.format(image))
                container.stop()
                container.remove()
                container = _create_container(client, image, self.root, self.temp)
                self.dist = dist
                self.cid = container.id
                self.save()

        L.debug('[container] Using container {}'.format(container.name))
        if cmd:
            L.debug('[command  ] {cmd}'.format(cmd=cmd))

        try:
            container.start()
        except docker.errors.APIError as e:
            L.error('Failed to start container.')
            L.error(e.explanation)
            L.debug('Removing created container {}.'.format(container.name))
            container.remove()
            sys.exit(1)

        # let entrypoint run and user get created
        time.sleep(0.1)

        if cmd:
            cmd = 'sudo -u opx bash --login -c "{cmd}"'.format(cmd=cmd)
        else:
            cmd = 'sudo -u opx bash'

        dockerpty.exec_command(client.api, container.id, command=cmd)

        if self.temp or remove:
            L.debug('[container] Stopping container {}'.format(container.name))
            container.stop()
            L.debug('[container] Removing container {}'.format(container.name))
            container.remove()
            self.cid = ''
            self.save()

    def buildpackage(
            self, pkg: str, rm=False, dist='unstable', sort=False, tag=False,
            debian_dist='jessie',
    ):
        if not Path(pkg).exists():
            L.error('{} does not exists.'.format(pkg))
            sys.exit(1)

        L.debug('[build    ] Attempting to build {} for {} {}.'.format(
            pkg,
            debian_dist,
            dist,
        ))

        try:
            cmd = build_command(Path(pkg), debian_dist, tag)
        except InvalidBuildPathException as e:
            L.error(e)
            sys.exit(1)

        self.run(remove=rm, dist=dist, cmd=cmd)

        if sort:
            try:
                # python3.4 does not have exist_ok=True in Path.mkdir
                Path(self.root / 'pkg' / pkg).mkdir(parents=True)
            except FileExistsError:
                pass

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
            L.debug('[build    ] Found {}!'.format(d.name))
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
        workspace root, an InvalidWorkspaceException is raised. If the path is in a
        valid workspace but no records of the workspace are stored, a
        ForeignWorkspaceException is raised.
        """
        root = _workspace_root(path)
        parser = parser_read()

        if str(root) not in parser.sections():
            raise ForeignWorkspaceException('There is no record of this workspace.')

        # Read config values from parser
        config = {k: parser[str(root)].get(k, v)
                  for k, v in CONFIG_MAP.items()}

        return cls(root, temp=False, **config)


pass_context = click.make_pass_decorator(Workspace)


class ForeignWorkspaceException(Exception):
    """Raised when a Workspace is requested for a workspace not created by this tool."""


class InvalidWorkspaceException(Exception):
    """Raised when a Workspace is requested for an invalid path."""


class InvalidBuildPathException(Exception):
    """Raised when a build is requested in a Path without a build recipe."""


def build_command(path: Path, debian='jessie', tag=False) -> str:
    if Path(path / 'control').exists():
        cmd = 'equivs-build {}/control'.format(path)

    elif Path(path / 'debian' / 'control').exists():

        if Path(path/ 'debian' / 'changelog').exists():
            # First, index local packages
            cmd = 'cd /mnt; apt-ftparchive packages . >Packages 2>/dev/null; '
            # Second, run git-buildpackage
            cmd += 'cd {}; gbp buildpackage'.format(path)
            cmd += ' --git-dist={} --git-pbuilder'.format(debian)
            cmd += ' --git-ignore-branch --git-ignore-new'
            if tag:
                cmd += ' --git-tag'

        else:
            # Simple packaging for opx-core, so far
            cmd = 'equivs-build {}/DEBIAN/control'.format(path)

    else:
        raise InvalidBuildPathException('No build recipe found for this path.')

    return cmd


def cleanup_removed_containers(parser: ConfigParser):
    """Delete removed containers from persistent configuration."""
    client = docker.from_env()
    for s in parser.sections():
        if parser[s].get('cid', '') != '':
            cid = parser[s].get('cid')
            try:
                client.containers.get(cid)
            except docker.errors.NotFound:
                L.warning('Removing missing container {} from {}'.format(cid[:10], s))
                del parser[s]['cid']


def cleanup_deleted_workspaces(parser: ConfigParser):
    """Remove deleted workspaces from persistent configuration."""
    delete = [s for s in parser.sections()
              if not Path(s + '/.workspace').exists() and s != 'DEFAULT']
    for d in delete:
        del parser[d]


def parser_read(location: Path = None) -> ConfigParser:
    configfile = location or Path(click.get_app_dir('opx')) / 'config'
    try:
        # python3.4 does not have exist_ok=True in Path.mkdir
        configfile.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    parser = ConfigParser()
    parser.read(str(configfile))
    return parser


def parser_write(parser: ConfigParser):
    with Path(click.get_app_dir('opx') + '/config').open('w') as f:
        parser.write(f)


def _create_container(client, image: str, mnt_dir: Path, temp=False) -> Container:
    """Returns created container with MNT_DIR mounted at /mnt."""
    L.debug('[container] Creating new container!')
    L.debug('[container] Mounting {} to /mnt'.format(mnt_dir))

    # collect volumes to mount
    volumes = {
        str(mnt_dir.resolve()): {'bind': '/mnt', 'mode': 'rw'},
    }

    # python3.4 does not have Path.home
    gitconfig = Path(os.path.expanduser('~')) / '.gitconfig'
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


def _pull_if_necessary(client, image):
    """Pull image if last pull was >24 hours ago."""
    parser = parser_read()
    tag = image.split(':')[1]
    now = datetime.datetime.now()

    last_pull = parser['DEFAULT'].getfloat('last_pull_{}'.format(tag), now.timestamp())
    if last_pull == now.timestamp():
        pull = True
    else:
        last_pull_time = datetime.datetime.fromtimestamp(last_pull)
        pull = last_pull_time <= now - datetime.timedelta(hours=24)

    if pull:
        L.info('More than 24 hours since last pull, pulling {}...'.format(image))

        try:
            client.images.pull(image)
        except docker.errors.NotFound:
            L.error("Couldn't pull {}.".format(image))
            sys.exit(1)

        parser['DEFAULT']['last_pull_{}'.format(tag)] = str(now.timestamp())
        # del parser['DEFAULT']['last_pull_{}'.format(tag)]
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
