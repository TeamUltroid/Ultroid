# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM programmingerror/ultroid:b0.1

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt install jq netcat -y
RUN apt autoremove

RUN git clone -b dev https://github.com/TeamUltroid/Ultroid.git /root/TeamUltroid/

WORKDIR /root/TeamUltroid/

RUN pip uninstall search-engine-parser -y

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 uninstall tgcrypto -y
CMD bash resources/startup/startup.sh
