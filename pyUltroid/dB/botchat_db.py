# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.


from .. import udB


def get_stuff():
    return udB.get_key("BOTCHAT") or {}


def add_stuff(msg_id, user_id):
    ok = get_stuff()
    ok.update({msg_id: user_id})
    return udB.set_key("BOTCHAT", ok)


def get_who(msg_id):
    ok = get_stuff()
    if ok.get(msg_id):
        return ok[msg_id]


def tag_add(msg, chat, user):
    ok = get_stuff()
    if not ok.get("TAG"):
        ok.update({"TAG": {msg: [chat, user]}})
    else:
        ok["TAG"].update({msg: [chat, user]})
    return udB.set_key("BOTCHAT", ok)


def who_tag(msg):
    ok = get_stuff()
    if ok.get("TAG") and ok["TAG"].get(msg):
        return ok["TAG"][msg]
    return False, False
