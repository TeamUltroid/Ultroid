# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM theteamultroid/ultroid:main

# set timezone
ENV TZ=Asia/Kolkata

ARG REPO=https://github.com/TeamUltroid/Ultroid.git

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    # cloning the repo and installing requirements.
    && if [ $BRANCH ]; then git clone -b $BRANCH $REPO /root/TeamUltroid/; else git clone $REPO /root/TeamUltroid/; fi \
    && pip3 install --no-cache-dir -r root/TeamUltroid/requirements.txt \
    && pip3 install av --no-binary av

# Railway's banned dependency
RUN if [ ! $RAILWAY_STATIC_URL ]; then pip3 install --no-cache-dir yt-dlp; fi

# Okteto CLI
RUN if [ $OKTETO_NAMESPACE ]; then curl https://get.okteto.com -sSfL | sh; fi

# changing workdir
WORKDIR /root/TeamUltroid/

# start the bot.
CMD ["bash", "startup"]
