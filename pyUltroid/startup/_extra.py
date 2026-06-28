# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

# https://bugs.python.org/issue26789
# 'open' not defined has been fixed in Python 3.10.

import builtins


def _fix_logging(handler):
    """Make ``FileHandler.open`` UTF-8 on legacy Python (< 3.10)."""
    handler._builtin_open = open

    def _new_open(self):
        open_func = self._builtin_open
        return open_func(self.baseFilename, self.mode, encoding="utf-8")

    handler._open = _new_open


def _ask_input():
    """Block any ``input()`` call so the bot can run unattended on VPS/CI.

    The previous implementation poked at ``__builtins__`` as a dict, which
    only works when the calling module is ``__main__``. In submodules
    ``__builtins__`` is the module itself, so the patch silently failed.
    """

    def new_input(*args, **kwargs):
        raise EOFError(f"args={args}, kwargs={kwargs}")

    builtins.input = new_input
