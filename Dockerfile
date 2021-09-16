# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM theteamultroid/ultroid:dev

# set timezone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    # cloning the repo and other misc task
    && git clone -b dev https://github.com/TeamUltroid/Ultroid.git /root/TeamUltroid/ \
    && pip3 uninstall av -y && pip3 install --no-binary av

# changing workdir
WORKDIR /root/TeamUltroid/

# start the bot
CMD ["bash", "resources/startup/startup.sh"]
