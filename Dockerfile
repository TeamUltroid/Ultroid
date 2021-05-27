# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM programmingerror/ultroid:v0.0.2

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get autoremove --purge

RUN git clone -b dev https://github.com/TeamUltroid/Ultroid.git /root/TeamUltroid/

WORKDIR /root/TeamUltroid/

RUN pip3 install -r requirements.txt
RUN npm install -g npm@7.12.1 -g
RUN npm install
RUN npm run build

# CMD ["python", "-m", "pyUltroid"]
