from deb_pkg_tools.control import deb822_from_string, parse_control_fields

from opx import debian

CONTROL = """
Source: opx-common-utils
Section: net
Priority: optional
Maintainer: Dell EMC <ops-dev@lists.openswitch.net>
Build-Depends:
 debhelper (>= 9), dh-autoreconf, libopx-logging-dev  (>= 2.1.0), libxml2-dev
Standards-Version: 3.9.3
Vcs-Browser: https://github.com/open-switch/opx-common-utils
Vcs-Git: https://github.com/open-switch/opx-common-utils.git

Package: libopx-common1
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Description: This package contains general utilities for the Openswitch project.

Package: libopx-common-dev
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends},
 libopx-common1 (= ${binary:Version}), libopx-logging-dev (>= 2.1.0)
Description: This package contains general utilities for the Openswitch project.
"""


def test_resolve_dependencies():
    repo = 'opx-common-utils'
    control = parse_control_fields(deb822_from_string(CONTROL))
    packages = debian.remote_packages(
        'http://deb.openswitch.net/dists/unstable/opx/binary-amd64/Packages.gz',
    )
    deps = debian.resolve_dependencies(repo, control, packages)
    assert deps == ['opx-logging', 'opx-common-utils']
