# @riizzvbss
"""
✘ Perintah Tersedia -

• `{i}ass`
   Salam Lengkap

• `{i}as`
   Assalamu'alaikum

• `{i}ws`
   Jawab Salam
   
• `{i}ks`
   Kenalan Salam
   
• `{i}jws`
   Istighfar Salam
   
• `{i}3x`
    Bisa Kali

• `{i}kg`
    Keren lu gitu
"""

from time import sleep
from . import (
    eor,
    ultroid_cmd,
)


@ultroid_cmd(pattern="ass$")
async def _(event):
    await event.eor("**Assalamu'alaikum Warohmatulohi Wabarokatu**")


@ultroid_cmd(pattern="as$")
async def _(event):
    await event.eor("**Assalamu'alaikum**")
    
@ultroid_cmd(pattern="ws$")
async def _(event):
    await event.eor("**Wa'alaikumussalam**")

    
@ultroid_cmd(pattern="ks$")
async def _(event):
    xx = await event.eor(f"**Hy kaa 🥺**")
    sleep(2)
    await xx.edit("**Assalamualaikum...**")


@ultroid_cmd(pattern="jws$")
async def _(event):
    xx = await event.eor(event,f"**Astaghfirullah, Jawab salam dong**")
    sleep(2)
    await xx.edit("**Assalamu'alaikum**")


@ultroid_cmd(pattern="3x$")
async def _(event):
    xx = await event.eor(f"**Bismillah, 3x**")
    sleep(2)
    await xx.edit("**Assalamu'alaikum Bisa Kali**")
    
@ultroid_cmd(pattern="kg$")
async def _(event):
    xx = await event.eor(f"**Lu Ngapah Begitu ?**")
    sleep(2)
    await xx.edit("**Keren Lu Begitu ?**")
