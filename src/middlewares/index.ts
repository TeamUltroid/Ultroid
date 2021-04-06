/**
* Ultroid - UserBot
* Copyright (C) 2020 TeamUltroid
*
* This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
* PLease read the GNU Affero General Public License in
* <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
**/

import { bot } from '../bot';

import Auth from './auth';
import Logger from './logger';

export const initMiddleWares = (): void => {
    bot.use(Logger);
    bot.use(Auth);
}