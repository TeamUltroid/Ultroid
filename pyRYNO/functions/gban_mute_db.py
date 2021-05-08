# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pyRYNO import udB


def str_to_list(text):
    return text.split(" ")


def list_to_str(list):
    str = ""
    for x in list:
        str += f"{x} "
    return str.strip()


def gbanned_user():
    gbun = udB.get("GBAN")
    if gbun is None or gbun == "":
        return [""]
    else:
        return str_to_list(gbun)


def is_gbanned(id):
    id = str(id)
    if not id.isdigit():
        return False
    gbun = gbanned_user()
    if str(id) in gbun:
        return True
    else:
        return False


def gban(id):
    id = str(id)
    if not id.isdigit():
        return False
    try:
        gbun = gbanned_user()
        gbun.append(id)
        udB.set("GBAN", list_to_str(gbun))
        return True
    except:
        return False


def ungban(id):
    id = str(id)
    if not id.isdigit():
        return False
    try:
        gbun = gbanned_user()
        gbun.remove(id)
        udB.set("GBAN", list_to_str(gbun))
        return True
    except Exception as e:
        return False


def gmuted_user():
    gmute = udB.get("GMUTE")
    if gmute is None or gmute == "":
        return [""]
    else:
        return str_to_list(gmute)


def is_gmuted(id):
    id = str(id)
    if not id.isdigit():
        return False
    gmute = gmuted_user()
    if str(id) in gmute:
        return True
    else:
        return False


def gmute(id):
    id = str(id)
    if not id.isdigit():
        return False
    try:
        gmute = gmuted_user()
        gmute.append(id)
        udB.set("GMUTE", list_to_str(gmute))
        return True
    except:
        return False


def ungmute(id):
    id = str(id)
    if not id.isdigit():
        return False
    try:
        gmute = gmuted_user()
        gmute.remove(id)
        udB.set("GMUTE", list_to_str(gmute))
        return True
    except Exception as e:
        return False
