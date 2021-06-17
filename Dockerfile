# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM programmingerror/ultroid:b0.1

WORKDIR /root/TeamUltroid/

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip3 install -U pip

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt
RUN npm install -g npm@7.16.0 -g
RUN npm install
RUN npm run build

CMD ["bash","resources/startup/startup.sh"]
