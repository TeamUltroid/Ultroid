/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { Composer } from 'telegraf';
import { skip } from '../tgcalls';
import checkExpired from '../middlewares/checkExpired';
import { leaveVc } from '../tgcalls';

export const skipCBHandler = Composer.action(/^skip:[a-zA-Z0-9.\-_]+$/, checkExpired, async ctx => {
    const chat = ctx.callbackQuery.message?.chat;

    if (!chat) {
        await ctx.answerCbQuery("Invalid Request");
        return
    }

    if (chat.type !== 'supergroup') {
        return;
    }

    const skipped = skip(chat.id);

    if (skipped) {
        await ctx.answerCbQuery("Skipped ...");
        setTimeout(async () => await ctx.deleteMessage(), 1000);
    } else {
        await ctx.answerCbQuery("There's no song playing..");
        setTimeout(async () => await ctx.deleteMessage(), 1000);
        leaveVc(chat.id);
    }
})

export const skipCommand = Composer.command('skip', async ctx => {
    const { chat } = ctx.message;

    if (chat.type !== 'supergroup') {
        return;
    }

    const skipped = skip(chat.id);
    ctx.reply(skipped ? 'Skipped.' : "There's no song playing.");

    if (!skipped) {
        leaveVc(chat.id);
    }
})
