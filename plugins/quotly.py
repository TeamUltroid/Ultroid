import contextlib
import os

from core.remote import rm

from database.helpers import get_random_color

from .. import get_string, ultroid_cmd


@ultroid_cmd(pattern="q( (.*)|$)", manager=True, allow_pm=True)
async def q_cmd(event):
    match = event.pattern_match.group(1).strip()
    if not event.is_reply:
        return await event.eor("`Reply to Message..`")
    msg = await event.eor(get_string("com_1"))
    reply = await event.get_reply_message()
    replied_to, reply_ = None, None
    if match:
        spli_ = match.split(maxsplit=1)
        if (spli_[0] in ["r", "reply"]) or (
            spli_[0].isdigit() and int(spli_[0]) in range(1, 21)
        ):
            if spli_[0].isdigit():
                if not event.client._bot:
                    reply_ = await event.client.get_messages(
                        event.chat_id,
                        min_id=event.reply_to_msg_id - 1,
                        reverse=True,
                        limit=int(spli_[0]),
                    )
                else:
                    id_ = reply.id
                    reply_ = []
                    for msg_ in range(id_, id_ + int(spli_[0])):
                        msh = await event.client.get_messages(event.chat_id, ids=msg_)
                        if msh:
                            reply_.append(msh)
            else:
                replied_to = await reply.get_reply_message()
            try:
                match = spli_[1]
            except IndexError:
                match = None
    user = None
    if not reply_:
        reply_ = reply
    if match:
        match = match.split(maxsplit=1)
    if match:
        if match[0].startswith("@") or match[0].isdigit():
            with contextlib.suppress(ValueError):
                match_ = await event.client.parse_id(match[0])
                user = await event.client.get_entity(match_)
            match = match[1] if len(match) == 2 else None
        else:
            match = match[0]
    if match == "random":
        match = get_random_color()
    try:
        with rm.get("quotly", helper=True, dispose=True) as quotly:
            file = await quotly.create_quotly(
                reply_, bg=match, reply=replied_to, sender=user
            )
    except Exception as er:
        return await msg.edit(str(er))
    message = await reply.reply("Quotly by Ultroid", file=file)
    os.remove(file)
    await msg.delete()
    return message
