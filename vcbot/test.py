from . import *


@asst.on(events.NewMessage(pattern="^/play"))
async def player(event):
    gc = mp.group_call
    if not gc.is_connected:
        await mp.start_call(event.chat_id)
    gc.input_filename = "VCSONG_-1001237141420_11_16_39.raw"
