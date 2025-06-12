# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.


def _ask_input():
    # Ask for Input even on Vps and other platforms.
    def new_input(*args, **kwargs):
        raise EOFError("args=" + str(args) + ", kwargs=" + str(kwargs))

    __builtins__["input"] = new_input
