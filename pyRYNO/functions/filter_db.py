# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def list_to_str(list):  # Returns String
    str = ""
    for x in list:
        str += f"{x} "
    return str.strip()


def str_to_list(text):  # Returns List
    return text.split(" ")


def ls(list):
    str = ""
    for x in list:
        str += f"{x} |||"
    return str.strip()


def get_all_stuff():  # Returns List
    fills = udB.get("FILTER")
    if fills is None or fills == "":
        return [""]
    else:
        return str_to_list(fills)


def get_reply(chat, word):
    masala = udB.get("FILTER")
    if not masala:
        return
    x = masala.split("|||")
    for i in x:
        x = i.split("$|")
        try:
            if str(x[0]) == str(chat) and str(x[1]).lower() == str(word).lower():
                return eval(x[2])
        except:
            pass
    return None


def list_filter(chat):
    fl = udB.get("FILTER")
    if not fl:
        return None
    rt = fl.split("|||")
    tata = ""
    tar = 0
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            tata += f"👉 `{er[1]}`\n"
            tar += 1
    if tar == 0:
        return None
    return tata


def get_filter(chat):
    fl = udB.get("FILTER")
    if not fl:
        return None
    rt = fl.split("|||")
    tata = ""
    tar = 0
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            tata += f"{er[1]} "
            tar += 1
    if tar == 0:
        return None
    return tata


def add_filter(chat, word, msg, media):
    try:
        dumb_masala = get_all_stuff()
        rr = str({"msg": msg, "media": media})
        the_thing = f"|||{chat}$|{word}$|{rr}"
        rt = udB.get("FILTER")
        if not rt:
            the_thing = f"{chat}$|{word}$|{rr}"
        dumb_masala.append(the_thing)
        udB.set("FILTER", list_to_str(dumb_masala))
        return True
    except Exception as e:
        print(e)
        return False


def rem_filter(chat, word):
    try:
        d = list_to_str(get_all_stuff())
        x = d.split("|||")
        reply = get_reply(chat, word)
        the_thing = f"{chat}$|{word}$|{reply} "
        the_thing2 = f"{chat}$|{word}$|{reply}"
        try:
            x.remove(the_thing)
            x.remove(the_thing2)
        except BaseException:
            pass
        if len(x) < 2:
            udB.set("FILTER", list_to_str(x))
        else:
            udB.set("FILTER", ls(x))
        return True
    except Exception as e:
        print(e)
        return False
