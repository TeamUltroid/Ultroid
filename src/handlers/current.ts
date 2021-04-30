/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer, Markup } from 'telegraf';
import { getCurrentSong } from '../tgcalls';
import { getDuration } from '../utils';
import escapeHtml from '@youtwitface/escape-html';

export const songHandler = Composer.command('current', async ctx => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return;
    }

    const song = getCurrentSong(chat.id);

    if (song === null) {
        await ctx.reply('There is no song playing.');
        return;
    }

    const { id, title, duration } = song.song;
    const { id: from_id, f_name } = song.by;
    return await ctx.replyWithPhoto(`https://img.youtube.com/vi/${id}/hqdefault.jpg`, {
        caption: `<b>Playing : </b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(title)}</a>\n` +
            `<b>Duration: </b>${getDuration(duration)}\n` +
            `<b>Requested by :</b> <a href="tg://user?id=${from_id}">${f_name}</a>`,
        parse_mode: 'HTML',
        ...Markup.inlineKeyboard([
            [
                Markup.button.callback('Pause', `pause:${id}`),
                Markup.button.callback('Skip', `skip:${id}`),
            ],
            [
                Markup.button.callback('Exit', `exitVc`),
            ]
        ])
    })
});
