########################################################################
# File name: verify.py
# This file is part of: cuteborg
#
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
import asyncio
import enum
import subprocess


class ContentDiff(enum.Enum):
    EQUAL = 0
    SIZE_CHANGED = 1
    CHECKSUM_CHANGED = 2


class MetadataDiff(enum.Enum):
    TIMES = 0
    UNIX_PERMISSIONS = 1
    ACLS = 2
    XATTRS = 3
    TYPE = 4


class _RsyncFileFlag(enum.Enum):
    FILE_MISSING_LOCALLY = ">"
    FILE_MISSING_IN_ARCHIVE = "<"
    IS_HARDLINK = "h"
    CONTENT_UNCHANGED = "."
    _MESSAGE = "*"


@asyncio.coroutine
def diff_rsync(a, b, *, checksum=True):
    """
    Calculate the difference between two filesystem subtrees.

    :param a: rsync source path
    :param b: rsync target path

    This is calculated using rsync in dry-run mode with ``--itemize-changes``
    to obtain the information.

    If `checksum` is true, the files are compared using their checksums. This
    is considerably slower, but protects against silent data corruption. If you
    do not trust borg, use `checksum`.
    """

    args = [
        "rsync",
        "-raHAPSEX",  # my preferred recipe
        "--dry-run",  # we don’t want to actually do anything to the files
        "--itemize-changes",  # but we want to know what *would* be done
        "--delete",  # ensure that missing files are reported
    ]

    if checksum:
        args.append("--checksum")

    proc = asyncio.create_subprocess_exec(
        *args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
    )

    try:
        finished = False
        first = True
        while True:
            try:
                line = yield from proc.stdout.readline()
            except asyncio.streams.IncompleteReadError as exc:
                line = exc.partial
                finished = True

            if first:
                continue



            if finished:
                break
    except asyncio.CancelledError:
        pass

    if proc.returncode is None:
        try:
            proc.terminate()
        except ProcessLookupError:
            pass

    yield from proc.wait()
