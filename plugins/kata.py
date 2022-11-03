# Ported By @Riizzvbss
"""
✘ Perintah Tersedia -

•`{i}smgt`

•`{i}ywc`

•`{i}jamet`

•`{i}pp`

•`{i}dp`

•`{i}sed`

•`{i}so`

•`{i}nb`

•`{i}met`

•`{i}war`

•`{i}wartai`

•`{i}kismin`

•`{i}ded`

•`{i}sokab`

•`{i}gembel`

•`{i}cuih`

•`{i}dih`

•`{i}gcs`

•`{i}skb`

•`{i}virtual`
    Cobain aja sendiri.
"""

import string
from time import sleep
from . import (
    eor,
    ultroid_cmd,
)

@ultroid_cmd(pattern="emil$")
async def _(event):
    xx = await event.eor("Aku")
    sleep(3)
    await xx.edit("Cuma Mau Bilang")
    sleep(2)
    await xx.edit("Kalo Aku ...")
    sleep(1)
    await xx.edit("Aku Sayang Kamu [Emilia](https://t.me/adeliarenata1jowo)")


# Create by myself @localheart


@ultroid_cmd(pattern="smgt$")
async def _(event):
    xx = await event.eor("Apapun Yang Terjadi")
    sleep(3)
    await xx.edit("Tetaplah Menyerah")
    sleep(1)
    await xx.edit("Dan Jangan Pernah Bangkit")


# Create by myself @localheart


@ultroid_cmd(pattern=r"ywc$")
async def _(event):
    await event.client.send_message(
        event.chat_id, "Ok Sama Sama", reply_to=event.reply_to_msg_id
    )
    await event.delete()


@ultroid_cmd(pattern="jamet$")
async def _(event):
    xx = await event.eor("WOII")
    sleep(1.5)
    await xx.edit("JAMET")
    sleep(1.5)
    await xx.edit("CUMA MAU BILANG")
    sleep(1.5)
    await xx.edit("GAUSAH SO ASIK")
    sleep(1.5)
    await xx.edit("EMANG KENAL?")
    sleep(1.5)
    await xx.edit("GAUSAH REPLY")
    sleep(1.5)
    await xx.edit("KITA BUKAN KAWAN")
    sleep(1.5)
    await xx.edit("GASUKA PC ANJING")
    sleep(1.5)
    await xx.edit("BOCAH KAMPUNG")
    sleep(1.5)
    await xx.edit("MENTAL TEMPE")
    sleep(1.5)
    await xx.edit("LEMBEK NGENTOT🔥")


@ultroid_cmd(pattern="pp$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "PASANG PP DULU GOBLOK,BIAR ORANG-ORANG PADA TAU BETAPA HINA NYA MUKA LU 😆",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="dp$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "MUKA LU HINA, GAUSAH SOK KERAS YA ANJENGG!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()

    
@ultroid_cmd(pattern="sed$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "×͜× ʀɪᴢᴍɪʟ ᴜꜱᴇʀʙᴏᴛ ᴀᴄᴛɪᴠᴇᴅ ×͜×",
        reply_to=event.reply_to_msg_id,
    )
    

@ultroid_cmd(pattern="so$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "GAUSAH SOKAB SAMA GUA GOBLOK, LU BABU GA LEVEL!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="nb$")
async def _(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.eor(
            event, "Perintah ini Dilarang digunakan di Group ini"
        )
    await event.client.send_message(
        event.chat_id,
        "MAEN BOT MULU ALAY NGENTOTT, KESANNYA NORAK GOBLOK!!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="met$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "NAMANYA JUGA JAMET CAPER SANA SINI BUAT CARI NAMA",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="war$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "WAR WAR PALAK BAPAK KAU WAR, SOK KERAS BANGET GOBLOK, DI TONGKRONGAN JADI BABU, DI TELE SOK JAGOAN...",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="wartai$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "WAR WAR TAI ANJING, KETRIGGER MINTA SHARELOK LU KIRA MAU COD-AN GOBLOK, BACOTAN LU AJA KGA ADA KERAS KERASNYA GOBLOK",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="kismin$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "CUIHHHH, MAKAN AJA MASIH NGEMIS LO GOBLOK, JANGAN SO NINGGI YA KONTOL GA KEREN LU KEK GITU GOBLOK!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="ded$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "MATI AJA LU GOBLOK, GAGUNA LU HIDUP DI BUMI",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="sokab$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "SOKAB BET LU GOBLOK, KAGA ADA ISTILAH NYA BAWAHAN TEMENAN AMA BOS!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="gembel$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "MUKA BAPAK LU KEK KELAPA SAWIT ANJING, GA USAH NGATAIN ORANG, MUKA LU AJA KEK GEMBEL TEXAS GOBLOK!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="cuih$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "GAK KEREN LO KEK BEGITU GOBLOK, KELUARGA LU BAWA SINI GUA LUDAHIN SATU-SATU. CUIHH!!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="dih$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "DIHHH NAJISS ANAK HARAM LO GOBLOK, JANGAN BELAGU DIMARI KAGA KEREN LU KEK BGITU TOLOL!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern=r"gcs$")
async def _(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.eor(
            event, "Perintah ini Dilarang digunakan di Group ini"
        )
    await event.client.send_message(
        event.chat_id,
        "GC SAMPAH KAYA GINI, BUBARIN AJA GOBLOK!!",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="skb$")
async def _(event):
    await event.client.send_message(
        event.chat_id,
        "EMANG KITA KENAL? KAGA GOBLOK SOKAB BANGET LU GOBLOK",
        reply_to=event.reply_to_msg_id,
    )
    await event.delete()


@ultroid_cmd(pattern="virtual$")
async def _(event):
    xx = await event.eor("OOOO")
    sleep(1.5)
    await xx.edit("INI YANG VIRTUAL")
    sleep(1.5)
    await xx.edit("YANG KATANYA SAYANG BANGET")
    sleep(1.5)
    await xx.edit("TAPI TETEP AJA DI TINGGAL")
    sleep(1.5)
    await xx.edit("NI INGET")
    sleep(1.5)
    await xx.edit("TANGANNYA AJA GA BISA DI PEGANG")
    sleep(1.5)
    await xx.edit("APALAGI OMONGANNYA")
    sleep(1.5)
    await xx.edit("BHAHAHAHA")
    sleep(1.5)
    await xx.edit("KASIAN MANA MASIH MUDA")
    
    
