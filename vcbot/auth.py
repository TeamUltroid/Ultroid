from . import *


@vc_asst("authg", from_users=[udB["OWNER"], *sudoers])
async def auth_group(event):
    chat = event.chat_id
    VC_SUDO_GRPS = udB.get("VC_AUTH_GROUPS")
    if VC_SUDO_GRPS:
        xnxx = VC_SUDO_GRPS.split(" ")
        if str(chat) in xnxx:
            return await event.reply("Already Authed This Chat!")
        VC_SUDO_GRPS += f" {str(chat)}"
        udB.set("VC_AUTH_GROUPS", str(VC_SUDO_GRPS))
    else:
        udB.set("VC_AUTH_GROUPS", str(chat))
    await event.reply("Added to AUTH Groups successfully!")


@vc_asst("remauth", from_users=[udB["OWNER"], *sudoers])
async def auth_group(event):
    chat = event.chat_id
    VC_SUDO_GRPS = udB.get("VC_AUTH_GROUPS")
    if not VC_SUDO_GRPS:
        return await eor(event, "Vc Auths Group's List is Empty...")
    spli = VC_SUDO_GRPS.split(" ")
    if str(chat) not in spli:
        return await eor(event, "Chat is Not Added to Vc Auths.!")
    spli = spli.remove(str(chat))
    if not spli:
        udB.delete("VC_AUTH_GROUPS")
    else:
        VC_SUDO_GRPS = "".join(f" {a}" for a in spli)[1:]
        udB.set("VC_AUTH_GROUPS", VC_SUDO_GRPS)
    await eor(event, "Removed from Vc AUTH Groups!")
