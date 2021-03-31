# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM ultroidteam/ultroid:0.0.3
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i ./google-chrome-stable_current_amd64.deb; apt -fqqy install && \
    rm ./google-chrome-stable_current_amd64.deb
RUN wget -O chromedriver.zip http://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip  && \
    unzip chromedriver.zip chromedriver -d /usr/bin/ && \
    rm chromedriver.zip
RUN curl --silent --location https://deb.nodesource.com/setup_15.x | bash -
RUN apt-get install -y nodejs sudo
RUN git clone -b beta https://github.com/TeamUltroid/Ultroid.git /root/TeamUltroid/
WORKDIR /root/TeamUltroid/
RUN pip install py-Ultroid==14.8b0
RUN pip install -U Telethon
RUN pip install gingerit
RUN pip install git+https://github.com/buddhhu/search-engine-parser.git
RUN git clone https://github.com/buddhhu/vcjsbot
RUN mv -v vcjsbot/src .
RUN mv vcjsbot/package.json .
RUN mv vcjsbot/tsconfig.json .
RUN npm install -g npm@7.7.0
RUN npm install
RUN npm run build
