/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer } from 'telegraf';
import { getQueue, leaveVc, getCurrentSong, closeConnection } from '../tgcalls';
import escapeHtml from '@youtwitface/escape-html';
import { getDuration } from '../utils';

export const queueHandler = Composer.command('queue', async ctx => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return;
    }

    const queue = getQueue(chat.id);
    const message =
        queue && queue.length > 0
            ? queue.map((data, index) => {
                const { info, from } = data;
                return `<b>${index + 1} -</b> <a href="https://www.youtube.com/watch?v=${info.id}">${escapeHtml(info.title)}</a> (${getDuration(info.duration)})\n<b>Requested By :</b> <a href="tg://user?id=${from.id}">${from.f_name}</a>\n`
            }).join('\n')
            : 'The queue is empty.';

    await ctx.replyWithHTML(message, { disable_web_page_preview: true });

    const song = getCurrentSong(chat.id);
    if (song === null && queue?.length == 0) {
        closeConnection();
        leaveVc(chat.id);
    }
});
