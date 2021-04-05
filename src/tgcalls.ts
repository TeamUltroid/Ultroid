import { Chat } from 'typegram';
import { exec as _exec, spawn } from 'child_process';
import { JoinVoiceCallParams,JoinVoiceCallResponse } from 'tgcalls/lib/types';
import { Stream, TGCalls } from 'tgcalls';
import env from './env';
import WebSocket from 'ws';
import { Readable } from 'stream';
import { bot } from './bot';
import { Markup } from 'telegraf';
import { getDuration } from './utils';
import escapeHtml from '@youtwitface/escape-html';

interface DownloadedSong {
    stream: Readable;
    info: {
        id: string;
        title: string;
        duration: number;
    };
}

interface Queue {
    url: string;
    info: DownloadedSong['info'];
    from: {
        id: string | number;
        f_name: string;
    };
}

interface CurrentSong {
    song: DownloadedSong['info'],
    by: Queue['from']
}

interface CachedConnection {
    connection: TGCalls<{ chat: Chat.SupergroupChat }>;
    stream: Stream;
    queue: Queue[];
    currentSong: CurrentSong | null;
    joinResolve?: (value: JoinVoiceCallResponse) => void;
    joinedPayload?: JoinVoiceCallParams<{ chat: Chat.SupergroupChat; }>
}

const ws = new WebSocket(env.WEBSOCKET_URL);
const cache = new Map<number, CachedConnection>();

const ffmpegOptions = "-preset ultrafast -c copy -acodec pcm_s16le -f s16le -ac 1 -ar 65000 pipe:1";

ws.on('message', response => {
    const { _, data } = JSON.parse(response.toString());

    switch (_) {
        case 'get_join': {
            const connection = cache.get(data.chat_id);
            if (connection) {
                connection.joinResolve?.(data);
            }
            break;
        }
        default:
            break;
    }
});

const downloadSong = async (url: string): Promise<DownloadedSong> => {
    return new Promise((resolve, reject) => {
        const ytdlChunks: string[] = [];
        const ytdl = spawn('youtube-dl', ['-x', '--print-json', '-g', `${url}`]);

        ytdl.stderr.on('data', data => console.error(data.toString()));

        ytdl.stdout.on('data', data => {
            ytdlChunks.push(data.toString());
        });

        ytdl.on('exit', code => {
            if (code !== 0) {
                return reject();
            }

            const ytdlData = ytdlChunks.join('');
            const [inputUrl, _videoInfo] = ytdlData.split('\n');
            const videoInfo = JSON.parse(_videoInfo);

            const ffmpeg = spawn('ffmpeg', ['-y', '-nostdin', '-i', inputUrl, ...ffmpegOptions.split(' ')]);

            resolve({
                stream: ffmpeg.stdout,
                info: {
                    id: videoInfo.id,
                    title: videoInfo.title,
                    duration: videoInfo.duration,
                },
            });
        });
    });
};


export const getSongInfo = async (url: string): Promise<DownloadedSong['info']> => {
    return new Promise((resolve, reject) => {
        const ytdlChunks: string[] = [];
        const ytdl = spawn('youtube-dl', ['-x', '--print-json', '-g', `ytsearch:"${url}"`]);

        ytdl.stderr.on('data', data => console.error(data.toString()));

        ytdl.stdout.on('data', data => {
            ytdlChunks.push(data.toString());
        });

        ytdl.on('exit', code => {
            if (code !== 0) {
                return reject();
            }

            const ytdlData = ytdlChunks.join('');
            const [inputUrl, _videoInfo] = ytdlData.split('\n');
            const videoInfo = JSON.parse(_videoInfo);

            resolve({
                id: videoInfo.id,
                title: videoInfo.title,
                duration: videoInfo.duration,
            });
        });
    });
};

const createConnection = async (chat: Chat.SupergroupChat): Promise<void> => {
    if (cache.has(chat.id)) {
        return;
    }

    const connection = new TGCalls({ chat });
    const stream = new Stream();
    const queue: {
        url: string,
        info: DownloadedSong['info'],
        from: {
            id: string | number,
            f_name: string
        }
    }[] = [];

    const cachedConnection: CachedConnection = {
        connection,
        stream,
        queue,
        currentSong: null,
    };

    connection.joinVoiceCall = payload => {
        cachedConnection.joinedPayload = payload;
        return new Promise(resolve => {
            cachedConnection.joinResolve = resolve;

            const data = {
                _: 'join',
                data: {
                    ufrag: payload.ufrag,
                    pwd: payload.pwd,
                    hash: payload.hash,
                    setup: payload.setup,
                    fingerprint: payload.fingerprint,
                    source: payload.source,
                    chat: payload.params.chat,
                },
            };
            ws.send(JSON.stringify(data));
        });
    };

    cache.set(chat.id, cachedConnection);
    await connection.start(stream.createTrack());

    stream.on('finish', async () => {
        if (queue.length > 0) {
            const { url, from } = queue.shift()!;
            try {
                const song = await downloadSong(url);
                const { title, id, duration } = song.info
                stream.setReadable(song.stream);
                cachedConnection.currentSong = {
                    song: song.info,
                    by: from
                };

                await bot.telegram.sendPhoto(chat.id, `https://img.youtube.com/vi/${id}/hqdefault.jpg`, {
                    caption: `<b>Playing : </b> <a href="https://www.youtube.com/watch?v=${id}">${escapeHtml(title)}</a>\n` +
                        `<b>Duration : </b>${getDuration(duration)}\n` +
                        `<b>Requested by :</b> <a href="tg://user?id=${from.id}">${from.f_name}</a>`,
                    parse_mode: 'HTML',
                    ...Markup.inlineKeyboard([
                        [
                            Markup.button.callback('Pause', `pause:${id}`),
                            Markup.button.callback('Skip', `skip:${id}`)
                        ]
                    ])
                })
            } catch (error) {
                console.error(error);
                stream.emit('finish');
            }
        } else {
            try {
                leaveVc(chat.id);
            } catch (err) {
                console.error(err);
            }
            cachedConnection.currentSong = null;
        }
    });
    stream.on('leave', async () => {
        let payload = cachedConnection.joinedPayload;
        if (!payload) return;
        const data = {
            _: 'join',
            data: {
                ufrag: payload.ufrag,
                pwd: payload.pwd,
                hash: payload.hash,
                setup: payload.setup,
                fingerprint: payload.fingerprint,
                source: payload.source,
                chat: payload.params.chat,
            },
        };
        ws.send(JSON.stringify(data));
    });
};

export const leaveVc = (chatId: number) => {
    if (cache.has(chatId)) {
        const { stream } = cache.get(chatId)!;
        stream.emit('leave');
        return true;
    }
    return false;
}

export const addToQueue = async (chat: Chat.SupergroupChat, url: string, by: Queue['from']): Promise<number | null> => {
    if (!cache.has(chat.id)) {
        await createConnection(chat);
        return addToQueue(chat, url, by);
    }

    const connection = cache.get(chat.id)!;
    const { stream, queue } = connection;

    let songInfo: DownloadedSong['info'];
    if (stream.finished) {
        try {
            const song = await downloadSong(url);
            stream.setReadable(song.stream);
            connection.currentSong = {
                song: song.info,
                by: by
            };
            songInfo = song.info;
            cache.set(chat.id, connection);
        } catch (error) {
            console.error(error);
            return -1;
        }
        return 0;
    } else {
        songInfo = await getSongInfo(url);
    }
    return queue.push({
        url: url,
        from: by,
        info: songInfo
    });
};

export const getCurrentSong = (chatId: number): CurrentSong | null => {
    if (cache.has(chatId)) {
        const { currentSong } = cache.get(chatId)!;
        return currentSong;
    }

    return null;
};

export const getQueue = (chatId: number): Queue[] | null => {
    if (cache.has(chatId)) {
        const { queue } = cache.get(chatId)!;
        return Array.from(queue);
    }
    return null;
};

export const removeQueue = (chatId: number, id: number): boolean => {
    if (cache.has(chatId)) {
        const { queue } = cache.get(chatId)!;
        if (id > queue.length) return false;
        if (queue.splice(id, 1)) return true;
    }
    return false;
}

export const pause = (chatId: number): boolean | null => {
    if (cache.has(chatId)) {
        const { stream } = cache.get(chatId)!;
        stream.pause();
        return stream.paused;
    }

    return null;
};

export const skip = (chatId: number): boolean => {
    if (cache.has(chatId)) {
        const { stream } = cache.get(chatId)!;
        stream.finish();
        stream.emit('finish');
        return true;
    }

    return false;
};
