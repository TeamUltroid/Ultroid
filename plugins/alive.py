from platform import python_version
from random import choice

from core.git import repo
from core.version import version
from telethon.errors import BotMethodInvalidError, ChatSendMediaForbiddenError
from telethon.version import __version__

from .. import *

buttons = [
    [
        Button.url(
            get_string("bot_3"),
            "https://github.com/TeamUltroid/Ultroid"),
        Button.url(get_string("bot_4"), "t.me/UltroidSupportChat"),
    ]
]

# Will move to strings
alive_txt = """
The Ultroid Userbot

  ◍ Version - {}
  ◍ Telethon - {}
"""

in_alive = "{}\n\n🌀 <b>Ultroid Version -><b> <code>{}</code>\n🌀 <b>Python -></b> <code>{}</code>\n🌀 <b>Uptime -></b> <code>{}</code>\n🌀 <b>Branch -></b>[ {} ]\n\n• <b>Join @TeamUltroid</b>"


@callback("alive")
async def alive(event):
    text = alive_txt.format(version, __version__)
    await event.answer(text, alert=True)


@ultroid_cmd(
    pattern="alive( (.*)|$)",
)
async def alive_func(ult):
    match = ult.pattern_match.group(1).strip()
    inline = None
    if match in ["inline", "i"]:
        try:
            res = await ult.client.inline_query(asst.me.username, "alive")
            return await res[0].click(ult.chat_id)
        except BotMethodInvalidError:
            pass
        except BaseException as er:
            LOGS.exception(er)
        inline = True
    OWNER_NAME = ultroid_bot.me.first_name

    pic = udB.get_key("ALIVE_PIC")
    if isinstance(pic, list):
        pic = choice(pic)
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
    y = repo.active_branch()
    xx = repo.get_remote_url()
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    if inline:
        kk = f"<a href={rep}>{y}</a>"
        parse = "html"
        als = in_alive.format(
            header,
            f"{version} [{HOSTED_ON}]",
            python_version(),
            uptime,
            kk,
        )

        if _e := udB.get_key("ALIVE_EMOJI"):
            als = als.replace("🌀", _e)
    else:
        parse = "md"
        als = (get_string("alive_1")).format(
            header,
            OWNER_NAME,
            f"{version} [{HOSTED_ON}]",
            uptime,
            python_version(),
            __version__,
            kk,
        )

        if a := udB.get_key("ALIVE_EMOJI"):
            als = als.replace("✵", a)
    if pic:
        try:
            await ult.reply(
                als,
                file=pic,
                parse_mode=parse,
                link_preview=False,
                buttons=buttons if inline else None,
            )
            return await ult.try_delete()
        except ChatSendMediaForbiddenError:
            pass
        except BaseException as er:
            LOGS.exception(er)
            try:
                await ult.reply(file=pic)
                await ult.reply(
                    als,
                    parse_mode=parse,
                    buttons=buttons if inline else None,
                    link_preview=False,
                )
                return await ult.try_delete()
            except BaseException as er:
                LOGS.exception(er)
    await ult.eor(
        als,
        parse_mode=parse,
        link_preview=False,
        buttons=buttons if inline else None,
    )
