# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM python:latest

# set timezone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD . /root/TeamUltroid

WORKDIR "/root/TeamUltroid"

RUN ./ultroid install

# start the bot.
CMD ["./ultroid", "start"]