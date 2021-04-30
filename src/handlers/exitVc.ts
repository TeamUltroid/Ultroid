/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer } from 'telegraf';
import { leaveVc } from '../tgcalls';

export const skipCBHandler = Composer.action('exitVc', async ctx => {
    const chat = ctx.callbackQuery.message?.chat;

    if (!chat) {
        await ctx.answerCbQuery("Invalid Request");
        return false;
    }

    if (chat.type !== 'supergroup') {
        await ctx.answerCbQuery("Invalid Request");
        return false;
    }

    leaveVc(chat.id);
    ctx.reply("Left Voice Chat.");
})

export const skipCommand = Composer.command('exitVc', async ctx => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return;
    }

    leaveVc(chat.id);
    ctx.reply("Left Voice Chat.");
})
