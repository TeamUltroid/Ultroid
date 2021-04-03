from . import *

async def add_welcome(x, chat, msg):
    try:
        udB.set(f"WELCOME_{chat}", msg)
        await eod(x, f"Done. Welcome message set to ```{msg}```")
    except:
        pass


def get_welcome(chat):
    return udB.get(f"WELCOME_{chat}")

async def delete_welcome(event):
    try:
        udB.delete(f"WELCOME_{event.chat_id}")
        return await eod(event, f"Done. Welcome message successfully deleted!\nPrevious message was\n```{prv}```", time=20)
    except:
        pass