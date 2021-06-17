/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer, Markup } from 'telegraf';
import { pause, getCurrentSong } from '../tgcalls';
import { getDuration } from '../utils';
import escapeHtml from '@youtwitface/escape-html';
import checkExpired from '../middlewares/checkExpired';

export const pauseCBHandler = Composer.action(/^pause:[a-zA-Z0-9.\-_]+$/, checkExpired, async (ctx) => {
    const chat = ctx.callbackQuery.message?.chat;

    let data: string = '';
    if ('data' in ctx.callbackQuery) data = ctx.callbackQuery.data;

    if (!chat) {
        await ctx.answerCbQuery("Invalid Request");
        return false;
    }

    const current = getCurrentSong(chat.id);
    const paused = pause(chat.id);
    if (!current) {
        await ctx.answerCbQuery("There's nothing playing here.");
        return setTimeout(async () => await ctx.deleteMessage(), 1000);
    }

    const { id, title, duration } = current.song;
    const { id: id_by, f_name } = current.by;
    if (paused) {
        await ctx.editMessageCaption(`<b>Paused :</b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(title)}</a>\n` +
            `<b>Duration :</b> ${getDuration(duration)}\n` +
            `<b>Paused by :</b> <a href="tg://user?id=${ctx.from?.id}">${ctx.from?.first_name}</a>\n` +
            `<b>Requested by :</b> <a href="tg://user?id=${id_by}">${f_name}</a>`, {
            parse_mode: 'HTML',
            ...Markup.inlineKeyboard([
                [
                    Markup.button.callback('Resume', `pause:${id}`),
                    Markup.button.callback('Skip', `skip${id}`)
                ],
                [
                    Markup.button.callback('Exit', `exitVc`),
                ]
            ])
        });
        return await ctx.answerCbQuery("Paused ...");
    } else {
        await ctx.editMessageCaption(`<b>Playing :</b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(title)}</a>\n` +
            `<b>Duration :</b> ${getDuration(duration)}\n` +
            `<b>Resumed by :</b> <a href="tg://user?id=${ctx.from?.id}">${ctx.from?.first_name}</a>\n` +
            `<b>Requested by :</b> <a href="tg://user?id=${id_by}">${f_name}</a>`, {
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
        });
        return await ctx.answerCbQuery("Resumed ...");
    }
})
