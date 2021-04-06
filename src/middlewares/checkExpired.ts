/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Context, MiddlewareFn } from 'telegraf';
import { getCurrentSong } from '../tgcalls';
import { logger as log } from '../bot';
import escapeHtml from '@youtwitface/escape-html';

const checkExpired: MiddlewareFn<Context> = async (ctx, next) => {
    if (ctx.callbackQuery) {
        if ('data' in ctx.callbackQuery) {
            let chat = ctx.callbackQuery.message?.chat;
            if (!chat) { // USELESS CHECKING to Satisfy TS
                return await ctx.answerCbQuery("Invalid Request");
            }
            let [_, id] = ctx.callbackQuery.data.split(":");
            let current = getCurrentSong(chat.id);

            if (current && (current.song.id !== id)) {
                await ctx.answerCbQuery("This Button is Expired ...");
                try {
                    return setTimeout(async () => await ctx.deleteMessage(), 2500);
                } catch (err) {
                    return await log(
                        `<b>Error in</b> <code>${chat.id}</code>\n` +
                        `${escapeHtml(err.toString())}`
                    );
                }
            } else {
                return next();
            }
        }
    } else {
        return next();
    }
}

export default checkExpired;