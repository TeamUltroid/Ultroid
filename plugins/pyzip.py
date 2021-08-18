# Idea|Credit : @Mellowizxd. (#piro)
# Made by @e3ris

"""
>> Reply .pyzip to any file
>> Any arguments (if given) will be Password.
"""

import os

try:
    import pyminizip
except Exception:
    os.system("pip install pyminizip")
    import pyminizip

from . import *

err = "Reply to a File bish"

@ultroid_cmd(pattern="pyzip ?(.*)")
async def pyZip(e):
    if e.fwd_from:
        return
    reply = await e.get_reply_message()
    if not (reply and reply.media):
        return await eod(e, err)
    pass_ = e.pattern_match.group(1)
    eris = await eor(e, ">> __downloading..__")
    dl_ = await e.client.download_media(reply)
    await eris.edit(">> __compressing..__")
    nem_ = reply.file.name
    zip_ = f"{nem_}.zip" if nem_ else "ult_pyZip.zip"
    password = pass_ if pass_ else "pyZip"
    cap_ = f"**File Name :** - {zip_} \n"\
    f"**Password to Unzip :** - `{password}`"
    
    pyminizip.compress(
        dl_, None, zip_, password, 5)
    await eris.edit(">> __uploading__")
    try:
        await e.client.send_file(
            e.chat_id, zip_, caption=cap_)
        await eris.delete()
    except Exception as ex:
        return await eris.edit(f"#Error: {ex}")
    finally:
        os.remove(zip_)
        os.remove(dl_)