import { bot } from '../bot';

import Auth from './auth';
import Logger from './logger';

export const initMiddleWares = (): void => {
    bot.use(Logger);
    bot.use(Auth);
}