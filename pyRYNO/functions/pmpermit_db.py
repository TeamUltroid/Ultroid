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


def get_approved():  # Returns List
    pmperm = udB.get("PMPERMIT")
    if pmperm is None or pmperm == "":
        return [""]
    else:
        return str_to_list(pmperm)


def is_approved(id):  # Take int or str with numbers only , Returns Boolean
    if not str(id).isdigit():
        return False
    pmperm = get_approved()
    if str(id) in pmperm:
        return True
    else:
        return False


def approve_user(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        pmperm = get_approved()
        pmperm.append(id)
        udB.set("PMPERMIT", list_to_str(pmperm))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmpermit_db/approve_user : {e}")
        return False


def disapprove_user(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        pmperm = get_approved()
        pmperm.remove(id)
        udB.set("PMPERMIT", list_to_str(pmperm))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmpermit_db/disapprove_user : {e}")
        return False
