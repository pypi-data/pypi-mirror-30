# Copyright 2015-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os
try:
    from shlex import quote as shell_escape
except ImportError:
    from pipes import quote as shell_escape
import subprocess


def get_arch_bits(arch):
    if arch == "x32":
        # x32 is an exception: the userspace is 32-bit, but it expects to be
        # running on a 64-bit kernel.
        return 64
    else:
        env = dict(os.environ)
        env.pop("DEB_HOST_ARCH_BITS", None)
        bits = subprocess.check_output(
            ["dpkg-architecture", "-a%s" % arch, "-qDEB_HOST_ARCH_BITS"],
            env=env).rstrip("\n")
        if bits == "32":
            return 32
        elif bits == "64":
            return 64
        else:
            raise RuntimeError(
                "Don't know how to deal with architecture %s "
                "(DEB_HOST_ARCH_BITS=%s)" % (arch, bits))


def set_personality(args, arch, series=None):
    bits = get_arch_bits(arch)
    assert bits in (32, 64)
    if bits == 32:
        setarch_cmd = ["linux32"]
    else:
        setarch_cmd = ["linux64"]

    if series in ("hardy", "lucid", "maverick", "natty", "oneiric", "precise"):
        setarch_cmd.append("--uname-2.6")

    return setarch_cmd + args
