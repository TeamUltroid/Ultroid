#PORTED FOR RYNO BY @HUNTER_YUVRAJ
#for card
from faker import Faker as dc
from userbot.utils import admin_cmd as hehe
from userbot import bot as cobra
#for cc
from userbot import bot 
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot.utils import admin_cmd 
from telethon import functions, types, events
from telethon.tl.functions.messages import DeleteHistoryRequest



"""
✘ Commands Available -

• `{i}bin <your bin>`
    To check your bin.

• `{i}card`
    Get a working bin

"""


@bot.on(admin_cmd("bin ?(.*)"))
async def bin(check):
    if check.fwd_from:
        return
    cc = check.pattern_match.group(1)
    chat = "@Carol5_bot"
    cmd = f"/bin {cc}"
    await check.edit("```Searching Ur Bin```")
    async with bot.conversation(chat) as conv:
          try:
              msg = await conv.send_message(cmd)
              response = await conv.get_response()
              
            
              await bot.send_read_acknowledge(conv.chat_id)
          except YouBlockedUserError:
              await check.edit("```Please unblock @Carol5_bot and try again```")
              return
          
          await bot.send_message(check.chat_id, response)
    await bot(functions.messages.DeleteHistoryRequest(peer=chat, max_id=0))
                                 
    await check.delete()


@cobra.on(hehe("card"))
async def _cobra(dark):
    cyber = dc()
    killer = cyber.name()
    kali = cyber.address()
    ryno = cyber.credit_card_full()
    await dark.edit(f"ℕ𝕒𝕞𝕖:-\n`{killer}`\n\n𝔸𝕕𝕕𝕣𝕖𝕤𝕤:-\n`{kali}`\n\nℂ𝕒𝕣𝕕:-\n`{ryno}`")
    
    
    HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})