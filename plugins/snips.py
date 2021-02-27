# This Source Code Form is subject to the terms of the Mozilla Public

# License, v. 2.0. If a copy of the MPL was not distributed with this

# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Snips

Available Commands:

.snips

.snipl

.snipd"""

from telethon import events, utils

from telethon.tl import types

from ultroid.plugins.sql_helper.snips_sql import get_snips, add_snip, remove_snip, get_all_snips

from ultroid.utils import admin_cmd

from ultroid import CMD_HELP

TYPE_TEXT = 0

TYPE_PHOTO = 1

TYPE_DOCUMENT = 2

@borg.on(events.NewMessage(pattern=r'\#(\S+)', outgoing=True))

async def on_snip(event):

    name = event.pattern_match.group(1)

    snip = get_snips(name)

    if snip:

        if snip.snip_type == TYPE_PHOTO:

            media = types.InputPhoto(

                int(snip.media_id),

                int(snip.media_access_hash),

                snip.media_file_reference

            )

        elif snip.snip_type == TYPE_DOCUMENT:

            media = types.InputDocument(

                int(snip.media_id),

                int(snip.media_access_hash),

                snip.media_file_reference

            )

        else:

            media = None

        message_id = event.message.id

        if event.reply_to_msg_id:

            message_id = event.reply_to_msg_id

        await borg.send_message(

            event.chat_id,

            snip.reply,

            reply_to=message_id,

            file=media

        )

        await event.delete()

@borg.on(admin_cmd(pattern="snips (.*)"))

async def on_snip_save(event):

    name = event.pattern_match.group(1)

    msg = await event.get_reply_message()

    if msg:

        snip = {'type': TYPE_TEXT, 'text': msg.message or ''}

        if msg.media:

            media = None

            if isinstance(msg.media, types.MessageMediaPhoto):

                media = utils.get_input_photo(msg.media.photo)

                snip['type'] = TYPE_PHOTO

            elif isinstance(msg.media, types.MessageMediaDocument):

                media = utils.get_input_document(msg.media.document)

                snip['type'] = TYPE_DOCUMENT

            if media:

                snip['id'] = media.id

                snip['hash'] = media.access_hash

                snip['fr'] = media.file_reference

        add_snip(name, snip['text'], snip['type'], snip.get('id'), snip.get('hash'), snip.get('fr'))

        await event.edit("snip {name} saved successfully. Get it with #{name}".format(name=name))

    else:

        await event.edit("Reply to a message with snips keyword to save the snip")

@borg.on(admin_cmd(pattern="snipl"))

async def on_snip_list(event):

    all_snips = get_all_snips()

    OUT_STR = "Available Snips:\n"

    if len(all_snips) > 0:

        for a_snip in all_snips:

            OUT_STR += f"👉 #{a_snip.snip} \n"

    else:

        OUT_STR = "No Snips. Start Saving using .snips"

    if len(OUT_STR) > Config.MAX_MESSAGE_SIZE_LIMIT:

        with io.BytesIO(str.encode(OUT_STR)) as out_file:

            out_file.name = "snips.text"

            await borg.send_file(

                event.chat_id,

                out_file,

                force_document=True,

                allow_cache=False,

                caption="Available Snips",

                reply_to=event

            )

            await event.delete()

    else:

        await event.edit(OUT_STR)

@borg.on(admin_cmd(pattern="snipd (\S+)"))

async def on_snip_delete(event):

    name = event.pattern_match.group(1)

    remove_snip(name)

    await event.edit("snip #{} deleted successfully".format(name))

    

CMD_HELP.update({

    "snip":

    "\

#<snipname>\

\nUsage: Gets the specified note.\

\n\n.snips: reply to a message with .snips <notename>\

\nUsage: Saves the replied message as a note with the notename. (Works with pics, docs, and stickers too!)\

\n\n.snipl\

\nUsage: Gets all saved notes in a chat.\

\n\n.snipd <notename>\

\nUsage: Deletes the specified note.\

"

})
