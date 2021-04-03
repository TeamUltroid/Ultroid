import redis from 'redis';
import env from './env';

const host = env.REDIS_URI.split(":")[0];
const port = Number(env.REDIS_URI.split(":")[1]);

const client = redis.createClient({
    host: host,
    port: port,
    password: env.REDIS_PASSWORD
});

export default client;