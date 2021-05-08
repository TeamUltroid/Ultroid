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


def are_all_nums(list):  # Takes List , Returns Boolean
    flag = True
    for item in list:
        if not item.isdigit():
            flag = False
            break
    return flag


def get_vcsudos():  # Returns List
    sudos = udB.get("VC_SUDOS")
    if sudos is None or sudos == "":
        return [""]
    else:
        return str_to_list(sudos)


def is_vcsudo(id):  # Take int or str with numbers only , Returns Boolean
    if not str(id).isdigit():
        return False
    sudos = get_vcsudos()
    if str(id) in sudos:
        return True
    else:
        return False


def add_vcsudo(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        sudos = get_vcsudos()
        sudos.append(id)
        udB.set("VC_SUDOS", list_to_str(sudos))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/sudos/add_sudo : {e}")
        return False


def del_vcsudo(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        sudos = get_vcsudos()
        sudos.remove(id)
        udB.set("VC_SUDOS", list_to_str(sudos))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/sudos/del_sudo : {e}")
        return False
