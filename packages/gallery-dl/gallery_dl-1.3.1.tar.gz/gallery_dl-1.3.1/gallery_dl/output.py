# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import shutil
from . import config


def select():
    """Automatically select a suitable output class"""
    pdict = {
        "default": PipeOutput,
        "pipe": PipeOutput,
        "term": TerminalOutput,
        "terminal": TerminalOutput,
        "color": ColorOutput,
        "null": NullOutput,
    }
    omode = config.get(("output", "mode"), "auto").lower()
    if omode in pdict:
        return pdict[omode]()
    elif omode == "auto":
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            return ColorOutput() if ANSI else TerminalOutput()
        else:
            return PipeOutput()
    else:
        raise Exception("invalid output mode: " + omode)


def safeprint(txt, **kwargs):
    """Handle unicode errors and replace invalid characters"""
    try:
        print(txt, **kwargs)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding
        txt = txt.encode(enc, errors="replace").decode(enc)
        print(txt, **kwargs)


class NullOutput():

    def start(self, path):
        """Print a message indicating the start of a download"""

    def skip(self, path):
        """Print a message indicating that a download has been skipped"""

    def success(self, path, tries):
        """Print a message indicating the completion of a download"""

    def error(self, path, error, tries, max_tries):
        """Print a message indicating an error during download"""


class PipeOutput(NullOutput):

    def skip(self, path):
        print(CHAR_SKIP, path, sep="", flush=True)

    def success(self, path, tries):
        print(path, flush=True)


class TerminalOutput(NullOutput):

    def __init__(self):
        self.short = config.get(("output", "shorten"), True)
        if self.short:
            self.width = shutil.get_terminal_size().columns - OFFSET

    def start(self, path):
        safeprint(self.shorten("  " + path), end="", flush=True)

    def skip(self, path):
        safeprint(self.shorten(CHAR_SKIP + path))

    def success(self, path, tries):
        print("\r", end="")
        safeprint(self.shorten(CHAR_SUCCESS + path))

    def error(self, path, error, tries, max_tries):
        if tries <= 1 and path:
            print("\r", end="")
            safeprint(self.shorten(CHAR_ERROR + path))
        if max_tries > 1:
            error = "{} ({}/{})".format(error, tries, max_tries)
        print("\r[Error] ", end="")
        safeprint(error)

    def shorten(self, txt):
        """Reduce the length of 'txt' to the width of the terminal"""
        if self.short and len(txt) > self.width:
            hwidth = self.width // 2 - OFFSET
            return "".join((
                txt[:hwidth-1],
                CHAR_ELLIPSIES,
                txt[-hwidth-(self.width % 2):]
            ))
        return txt


class ColorOutput(TerminalOutput):

    def start(self, path):
        print(self.shorten(path), end="", flush=True)

    def skip(self, path):
        print("\033[2m", self.shorten(path), "\033[0m", sep="")

    def success(self, path, tries):
        print("\r\033[1;32m", self.shorten(path), "\033[0m", sep="")

    def error(self, path, error, tries, max_tries):
        if tries <= 1 and path:
            print("\r\033[1;31m", self.shorten(path), sep="")
        if max_tries > 1:
            error = "{} ({}/{})".format(error, tries, max_tries)
        print("\r\033[0;31m[Error]\033[0m", error)


if os.name == "nt":
    ANSI = os.environ.get("TERM") == "ANSI"
    OFFSET = 1
    CHAR_SKIP = "# "
    CHAR_ERROR = "! "
    CHAR_SUCCESS = "* "
    CHAR_ELLIPSIES = "..."
else:
    ANSI = True
    OFFSET = 0
    CHAR_SKIP = "# "
    CHAR_ERROR = "✖ "
    CHAR_SUCCESS = "✔ "
    CHAR_ELLIPSIES = "…"
