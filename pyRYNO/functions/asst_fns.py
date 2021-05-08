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


def is_added(id):  # Take int or str with numbers only , Returns Boolean
    if not str(id).isdigit():
        return False
    users = get_all_users()
    if str(id) in users:
        return True
    else:
        return False


def add_user(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        users = get_all_users()
        users.append(id)
        udB.set("BOT_USERS", list_to_str(users))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmbot/add_user : {e}")
        return False


def del_user(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        users = get_all_users()
        users.remove(id)
        udB.set("BOT_USERS", list_to_str(users))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmbot/del_user : {e}")
        return False


def get_all_users():  # Returns List
    users = udB.get("BOT_USERS")
    if users is None or users == "":
        return [""]
    else:
        return str_to_list(users)


def is_blacklisted(id):  # Take int or str with numbers only , Returns Boolean
    if not str(id).isdigit():
        return False
    users = get_all_bl_users()
    if str(id) in users:
        return True
    else:
        return False


def blacklist_user(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        users = get_all_bl_users()
        users.append(id)
        udB.set("BOT_BLS", list_to_str(users))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmbot/blacklist_user : {e}")
        return False


def rem_blacklist(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    if not id.isdigit():
        return False
    try:
        users = get_all_bl_users()
        users.remove(id)
        udB.set("BOT_BLS", list_to_str(users))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/pmbot/rem_blacklist : {e}")
        return False


def get_all_bl_users():  # Returns List
    users = udB.get("BOT_BLS")
    if users is None or users == "":
        return [""]
    else:
        return str_to_list(users)
