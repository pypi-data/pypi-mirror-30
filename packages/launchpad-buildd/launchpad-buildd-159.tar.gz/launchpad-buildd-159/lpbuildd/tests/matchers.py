# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from testtools.matchers import (
    Equals,
    Matcher,
    MatchesDict,
    )


class HasWaitingFiles(Matcher):
    """Match files that have been added using `slave.addWaitingFile`."""

    def __init__(self, files):
        self.files = files

    @classmethod
    def byEquality(cls, files):
        return cls(
            {name: Equals(contents) for name, contents in files.items()})

    def match(self, slave):
        waiting_file_contents = {}
        for name in slave.waitingfiles:
            with open(slave.cachePath(slave.waitingfiles[name]), "rb") as f:
                waiting_file_contents[name] = f.read()
        return MatchesDict(self.files).match(waiting_file_contents)
