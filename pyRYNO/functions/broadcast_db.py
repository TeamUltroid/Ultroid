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


def get_channels():  # Returns List
    channels = udB.get("BROADCAST")
    if channels is None or channels == "":
        return [""]
    else:
        return str_to_list(channels)


def get_no_channels():  # Returns List
    channels = udB.get("BROADCAST")
    if channels is None or channels == "":
        return 0
    else:
        a = channels.split(" ")
    return len(a)


def is_channel_added(id):
    channels = get_channels()
    if str(id) in channels:
        return True
    else:
        return False


def add_channel(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    try:
        channels = get_channels()
        channels.append(id)
        udB.set("BROADCAST", list_to_str(channels))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/broadcast_db/add_channel : {e}")
        return False


def rem_channel(id):
    try:
        channels = get_channels()
        channels.remove(str(id))
        udB.set("BROADCAST", list_to_str(channels))
        return True
    except Exception as e:
        print(f"RYNO LOG : // functions/broadcast_db/rem_channel : {e}")
        return False
