import { Telegraf } from 'telegraf';
import env from './env';

export const bot = new Telegraf(env.BOT_TOKEN);
export const logger = async (msg: string, parse: 'HTML' | 'Markdown' | 'MarkdownV2' = 'HTML') => await bot.telegram.sendMessage(env.LOG_CHANNEL, msg, { parse_mode: parse });
