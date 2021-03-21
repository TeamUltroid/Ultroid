
from . import *
from gingerit.gingerit import GingerIt
from telethon import events
from googletrans import Translator
tr = Translator()




@ultroid_cmd(pattern="autocorrect")
async def acc(e):
    if Redis("AUTOCORRECT")!="True":
        udB.set("AUTOCORRECT", "True")
        await eor(e, "AUTOCORRECT Feature On")
    else:
        udB.delete("AUTOCORRECT")
        await eor(e, "AUTOCORRECT Feature Off")


@ultroid_bot.on(events.NewMessage(outgoing=True))
async def gramme(event):
    if Redis("AUTOCORRECT")!="True":
        return
     t = event.text
     if t.startswith((HNDLR, ".","?","#","_","*","'","@","[","(","+")):
        return
     if t.endswith(("..")):
        return
     tt = tr.translate(t)
     if tt.src != "en":
         return
     xx = GingerIt()
     x = xx.parse(t)
     res = (x['result'])
     await event.edit(res)
