from . import *


@vc_asst("joinvc")
async def join_(event):
    await vc_joiner(event, event.chat_id)
