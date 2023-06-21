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
    id = f"{chat} allhistory {user_id}"
    lol = await steal.eor(get_string("com_1"))
    try:
        async with steal.client.conversation(chat) as conv:
            try:
                msg = await conv.send_message(id)
                response = await conv.get_response()
            except YouBlockedUserError:
                return await lol.edit(f"Please unblock {chat} and try again")
            if response.text.startswith("No data available"):
                await lol.edit("No records found for this user")
                await steal.client.delete_messages(conv.chat_id, [msg.id, response.id])
            elif user_id in response.text:
                await lol.edit(response.message)
            else:
                await lol.edit(response.message)
            await steal.client.delete_messages(
                conv.chat_id,
                [msg.id, response.id],
            )
    except Exception:
        await lol.edit(f"Error: {chat} is not responding!.")
