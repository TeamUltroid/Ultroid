# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.


from .. import *

CMD_HELP = {}
# ----------------------------------------------#


class _SudoManager:
    def __init__(self):
        self.db = None
        self.owner = None
        self._owner_sudos = []

    def _init_db(self):
        if not self.db:
            from .. import udB

            self.db = udB
        return self.db

    def get_sudos(self):
        db = self._init_db()
        SUDOS = db.get_key("SUDOS")
        return SUDOS or []

    @property
    def should_allow_sudo(self):
        db = self._init_db()
        return db.get_key("SUDO")

    def owner_and_sudos(self):
        if not self.owner:
            db = self._init_db()
            self.owner = db.get_key("OWNER_ID")
        return [self.owner, *self.get_sudos()]

    @property
    def fullsudos(self):
        db = self._init_db()
        fsudos = db.get("FULLSUDO")
        if not self.owner:
            self.owner = db.get_key("OWNER_ID")
        if not fsudos:
            return [self.owner]
        fsudos = fsudos.split()
        fsudos.append(self.owner)
        return [int(_) for _ in fsudos]

    def is_sudo(self, id_):
        return bool(id_ in self.get_sudos())


SUDO_M = _SudoManager()
owner_and_sudos = SUDO_M.owner_and_sudos
sudoers = SUDO_M.get_sudos
is_sudo = SUDO_M.is_sudo

# ------------------------------------------------ #


def append_or_update(load, func, name, arggs):
    if isinstance(load, list):
        return load.append(func)
    if isinstance(load, dict):
        if load.get(name):
            return load[name].append((func, arggs))
        return load.update({name: [(func, arggs)]})
