# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def str_to_list(text):  # Returns List
    return text.split(" ")


def list_to_str(list):  # Returns String
    str = ""
    for x in list:
        str += f"{x} "
    return str.strip()


def get_muted():  # Returns List
    pmperm = udB.get("MUTE")
    if pmperm is None or pmperm == "":
        return [""]
    else:
        return str_to_list(pmperm)


def is_muted(id):  # Take int or str with numbers only , Returns Boolean
    pmperm = get_muted()
    if str(id) in pmperm:
        return True
    else:
        return False


def mute(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    try:
        pmperm = get_muted()
        pmperm.append(id)
        udB.set("MUTE", list_to_str(pmperm))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmpermit_db/approve_user : {e}")
        return False


def unmute(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    try:
        pmperm = get_muted()
        pmperm.remove(id)
        udB.set("MUTE", list_to_str(pmperm))
        return True
    except Exception as e:
        return False
