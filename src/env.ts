import { cleanEnv, str } from 'envalid';
import dotenv from 'dotenv';

dotenv.config();

export default cleanEnv(process.env, {
    BOT_TOKEN: str(),
    WEBSOCKET_URL: str(),
    REDIS_URI: str(),
    REDIS_PASSWORD: str(),
    LOG_CHANNEL: str()
});
