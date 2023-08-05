import gzip
import logging

from pathlib import Path

import requests

from deb_pkg_tools.control import deb822_from_string, parse_control_fields

L = logging.getLogger('opx')

DUMB_BUILD_ORDER = [
    'opx-core',
    'opx-logging',
    'opx-common-utils',
    'opx-cps',
    'opx-base-model',
    'opx-db-sql',
    'opx-sai-api',
    'opx-sai-vm',
    'opx-nas-common',
    'opx-nas-linux',
    'opx-nas-ndi-api',
    'opx-nas-ndi',
    'opx-nas-acl',
    'opx-nas-interface',
    'opx-nas-l2',
    'opx-nas-l3',
    'opx-nas-qos',
    'opx-nas-daemon',
    'opx-platform-config',
    'opx-sdi-sys',
    'opx-pas',
    'opx-tmpctl',
    'opx-tools',
    'opx-alarm',
]


def remote_packages(url: str):
    """Returns a dict containing the latest version of each package.

    Args:
        url: Points to a Packages.gz file

    Returns:
        dict[str]dict: a unique collection of packages
    """
    packages_dict = {}

    response = requests.get(url)

    for pkg_str in gzip.decompress(response.content).decode().split('\n\n'):
        pkg = parse_control_fields(deb822_from_string(pkg_str))
        if pkg.get('Package') and pkg.get('Package') not in packages_dict:
            packages_dict[pkg.get('Package')] = pkg

    return packages_dict


def resolve_dependencies(repo: str, control, packages):
    """Transform repo Build-Depends into source packages.

    Args:
        repo: Name of package we want dependencies for
        control (dict): Returned from parse_control_fields
        packages (dict[str]dict): Dict of dicts returned from
           parse_control_fields, with the package name as the key

    Returns:
        list[str]: Source packages to build sorted by DUMB_BUILD_ORDER
    """
    # TODO: Recursively fetch build dependencies
    rv = []
    for d in control['Build-Depends'].names:
        if d in packages:
            rv.append(packages[d].get('Source'))

    # TODO: Properly sort build dependencies
    rv.sort(key=lambda x: DUMB_BUILD_ORDER.index(x))

    L.debug('Need to build in this order: {}'.format(rv))

    rv.append(repo)
    return rv


def opx_build_dependencies(repo: str):
    """Returns a list of opx build dependencies for a repository.

    Args:
        repo: Repository to create a build order for

    Returns:
        list[str]: An order of repositories to build
    """
    if repo == 'all':
        return DUMB_BUILD_ORDER

    if not Path('{}/debian/control'.format(repo)).exists():
        return [repo]

    controlfile = Path('{}/debian/control'.format(repo))
    control = parse_control_fields(deb822_from_string(controlfile.read_text()))

    # TODO: Cache this file in config directory
    packages = remote_packages(
        'http://deb.openswitch.net/dists/unstable/opx/binary-amd64/Packages.gz',
    )

    return resolve_dependencies(repo, control, packages)
