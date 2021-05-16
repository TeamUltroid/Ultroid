/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer, deunionize, Markup } from 'telegraf';
import { addToQueue, getQueue } from '../tgcalls';
import { getCurrentSong } from '../tgcalls';
import { getDuration } from '../utils';
import { logger as log } from '../bot';
import escapeHtml from '@youtwitface/escape-html';

export const playHandler = Composer.command('play', async (ctx) => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return await ctx.reply('I can only play in groups.');
    }

    const [ commandEntity ] = ctx.message.entities!;
    const text = ctx.message.text.slice(commandEntity.length + 1) || deunionize(ctx.message.reply_to_message)?.text;

    if (!text) {
        return await ctx.reply('You need to specify a YouTube URL / Search Keyword.');
    }

    const index = await addToQueue(chat, text, {
        id: ctx.from.id,
        f_name: ctx.from.first_name
    });
    const song = getCurrentSong(chat.id);

    switch (index) {
        case -1:
            await ctx.reply("Failed to download song ...")
            break;
        case 0:
            if (song) {
                const { id, title, duration } = song.song;
                ctx.replyWithPhoto(`https://img.youtube.com/vi/${id}/hqdefault.jpg`, {
                    caption: `<b>Playing : </b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(title)}</a>\n` +
                        `<b>Duration: </b>${getDuration(duration)}\n` +
                        `<b>Requested by :</b> <a href="tg://user?id=${song.by.id}">${song.by.f_name}</a>`,
                    parse_mode: 'HTML',
                    ...Markup.inlineKeyboard([
                        [
                            Markup.button.callback('Pause', `pause:${id}`),
                            Markup.button.callback('Skip', `skip:${id}`)
                        ],
                        [
                            Markup.button.callback('Exit', `exitVc`),
                        ]
                    ])
                })
            }
            break;
        default:
            const queue = getQueue(chat.id);
            if (queue) {
                let queueId = queue.length - 1
                const { info, from } = queue[queueId];
                await ctx.replyWithHTML(`<b>Queued :</b> <a href="https://www.youtube.com/watch?v=${info.id}">${escapeHtml(info.title)}</a> (${getDuration(info.duration)})\n` +
                    `<b>At position ${index}.</b>\n` +
                    `<b>Requested By :</b> <a href="tg://user?id=${from.id}">${from.f_name}</a>`, {
                    disable_web_page_preview: true,
                });
            } else {
                await log("Queue not found in " + chat.title)
            }
    }

});
