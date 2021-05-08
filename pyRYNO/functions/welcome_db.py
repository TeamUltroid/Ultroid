from .. import udB


def add_welcome(chat, msg, media):
    x = {"welcome": msg, "media": media}
    return udB.set(f"{chat}_100", str(x))


def get_welcome(chat):
    wl = udB.get(f"{chat}_100")
    if wl:
        x = eval(wl)
        return x
    else:
        return


def delete_welcome(chat):
    return udB.delete(f"{chat}_100")
