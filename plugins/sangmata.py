from telethon.errors.rpcerrorlist import YouBlockedUserError

from .. import get_string, ultroid_cmd


@ultroid_cmd(
    pattern="sg( (.*)|$)",
)
async def lastname(steal):
    mat = steal.pattern_match.group(1).strip()
    message = await steal.get_reply_message()
    if mat:
        try:
            user_id = await steal.client.parse_id(mat)
        except ValueError:
            user_id = mat
    elif message:
        user_id = message.sender_id
    else:
        return await steal.eor("`Use this command with reply or give Username/id...`")

    chat = "@SangMata_beta_bot"
    lol = await steal.eor(get_string("com_1"))
    async with steal.client.conversation(chat, timeout=10) as conv:
        try:
            await conv.send_message(str(user_id))
            response = await conv.get_response()
            if "no data available" in str(response.text).lower():
                return await lol.edit("`No records found for this user..`")
            elif str(user_id) in str(response.message):
                await lol.edit(response.text)
        except YouBlockedUserError:
            await lol.edit(f"Please unblock {chat} and try again..")
        except Exception:
            await lol.edit(f"`Error: {chat} is not responding..`")
        finally:
            await conv.mark_read()
