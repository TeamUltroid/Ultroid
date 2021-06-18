/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer, Markup } from 'telegraf';
import { addFileToQueue, getQueue } from '../tgcalls';
import { getCurrentSong } from '../tgcalls';
import { getDuration } from '../utils';
import { logger as log } from '../bot';
import escapeHtml from '@youtwitface/escape-html';

export const filePlayHandler = Composer.command('playFile', async (ctx) => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return await ctx.reply('I can only play in groups.');
    }
    if (ctx.message.reply_to_message && JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio) {
        await ctx.reply('Starting <b>FilePlay</b> [beta]', {parse_mode: 'HTML'});
    } else {
        return await ctx.reply("Its Not An Audio File...");
    }

    const file = JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio;
    const fileLink = (await ctx.telegram.getFileLink(file.file_id)).href;

    if (!fileLink) {
        return await ctx.reply('You need to reply to a audio file not an Voice or Message!');
    }

    const index = await addFileToQueue(
        chat, fileLink, 
        {
            id: ctx.from.id,
            f_name: ctx.from.first_name
        },
        JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio.duration,
        JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio.file_name,
    );
    const song = getCurrentSong(chat.id);

    switch (index) {
        case -1:
            await ctx.reply("Failed to download song ...")
            break;
        case 0:
            if (song) {
                const { id } = song.song;
                ctx.replyWithPhoto("https://9to5google.com/wp-content/uploads/sites/4/2018/09/youtube_logo_dark.jpg?quality=82&strip=all", {
                    caption: `<b>Playing : </b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio.file_name)}</a>\n` +
                        `<b>Duration: </b>${getDuration(JSON.parse(JSON.stringify(ctx.message.reply_to_message)).audio.duration)}\n` +
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
