# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM theteamultroid/ultroid:main

# set timezone
ENV TZ=Asia/Kolkata

ARG REPO=https://github.com/TeamUltroid/Ultroid.git
ARG DIR=/root/TeamUltroid

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# cloning the repo and installing requirements.
RUN if [ $BRANCH ]; then git clone -b $BRANCH $REPO $DIR; else git clone $REPO $DIR; fi
RUN pip3 install --no-cache-dir -r $DIR/requirements.txt && pip3 install av --no-binary av

# Railway's banned dependency
RUN if [ ! $RAILWAY_STATIC_URL ]; then pip3 install --no-cache-dir yt-dlp; fi

# Okteto CLI
RUN if [ $OKTETO_TOKEN ]; then curl https://get.okteto.com -sSfL | sh; fi

# changing workdir
WORKDIR $DIR

# start the bot.
CMD ["bash", "startup"]
