from . import *


@vc_asst("authg")
async def auth_group(event):
    chat = event.chat_id
    VC_SUDO_GRPS = udB.get("VC_AUTH_GROUPS")
    if VC_SUDO_GRPS:
        xnxx = VC_SUDO_GRPS.split(" ")
        if str(chat) in xnxx:
            return await event.reply("Already Authed This Chat!")
        VC_SUDO_GRPS += f" {str(chat)}"
        udB.set("VC_AUTH_GROUPS", str(VC_SUDO_GRPS))
        return await event.reply("Added to AUTH Groups successfully!")
    else:
        udB.set("VC_AUTH_GROUPS", str(chat))
        return await event.reply("Added to AUTH Groups successfully!")
