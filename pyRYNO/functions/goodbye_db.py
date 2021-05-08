from .. import udB


def add_goodbye(chat, msg, media):
    x = {"goodbye": msg, "media": media}
    return udB.set(f"{chat}_99", str(x))


def get_goodbye(chat):
    wl = udB.get(f"{chat}_99")
    if wl:
        x = eval(wl)
        return x
    else:
        return


def delete_goodbye(chat):
    return udB.delete(f"{chat}_99")
