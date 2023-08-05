# Copyright 2013-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os

from lpbuildd.debian import (
    DebianBuildManager,
    DebianBuildState,
    )


RETCODE_SUCCESS = 0
RETCODE_FAILURE_INSTALL = 200
RETCODE_FAILURE_BUILD = 201


class LiveFilesystemBuildState(DebianBuildState):
    BUILD_LIVEFS = "BUILD_LIVEFS"


class LiveFilesystemBuildManager(DebianBuildManager):
    """Build a live filesystem."""

    backend_name = "lxd"
    initial_build_state = LiveFilesystemBuildState.BUILD_LIVEFS

    def initiate(self, files, chroot, extra_args):
        """Initiate a build with a given set of files and chroot."""
        self.subarch = extra_args.get("subarch")
        self.project = extra_args["project"]
        self.subproject = extra_args.get("subproject")
        self.pocket = extra_args["pocket"]
        self.datestamp = extra_args.get("datestamp")
        self.image_format = extra_args.get("image_format")
        self.locale = extra_args.get("locale")
        self.extra_ppas = extra_args.get("extra_ppas", [])
        self.channel = extra_args.get("channel")
        self.debug = extra_args.get("debug", False)

        super(LiveFilesystemBuildManager, self).initiate(
            files, chroot, extra_args)

    def doRunBuild(self):
        """Run the process to build the live filesystem."""
        args = []
        if self.subarch:
            args.extend(["--subarch", self.subarch])
        args.extend(["--project", self.project])
        if self.subproject:
            args.extend(["--subproject", self.subproject])
        if self.datestamp:
            args.extend(["--datestamp", self.datestamp])
        if self.image_format:
            args.extend(["--image-format", self.image_format])
        if self.pocket == "proposed":
            args.append("--proposed")
        if self.locale:
            args.extend(["--locale", self.locale])
        for ppa in self.extra_ppas:
            args.extend(["--extra-ppa", ppa])
        if self.channel:
            args.extend(["--channel", self.channel])
        if self.debug:
            args.append("--debug")
        self.runTargetSubProcess("buildlivefs", *args)

    def iterate_BUILD_LIVEFS(self, retcode):
        """Finished building the live filesystem."""
        if retcode == RETCODE_SUCCESS:
            self.gatherResults()
            print("Returning build status: OK")
        elif (retcode >= RETCODE_FAILURE_INSTALL and
              retcode <= RETCODE_FAILURE_BUILD):
            if not self.alreadyfailed:
                self._slave.buildFail()
                print("Returning build status: Build failed.")
            self.alreadyfailed = True
        else:
            if not self.alreadyfailed:
                self._slave.builderFail()
                print("Returning build status: Builder failed.")
            self.alreadyfailed = True
        self.doReapProcesses(self._state)

    def iterateReap_BUILD_LIVEFS(self, retcode):
        """Finished reaping after building the live filesystem."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def gatherResults(self):
        """Gather the results of the build and add them to the file cache."""
        for entry in sorted(self.backend.listdir("/build")):
            path = os.path.join("/build", entry)
            if (entry.startswith("livecd.") and
                    not self.backend.islink(path)):
                self.addWaitingFileFromBackend(path)
