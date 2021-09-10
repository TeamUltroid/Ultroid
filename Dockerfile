# Ultroid - UserBot
# Copyright (C) 2021 Gladiator-007
# This file is a part of < https://github.com/Gladiator-007/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/Gladiator-007/Ultroid/blob/main/LICENSE/>.

FROM programmingerror/ultroid:b0.1

# set timezone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# clone the repo and change workdir
RUN git clone https://github.com/Gladiator-007/Ultroid.git /root/Gladiator-007/
WORKDIR /root/Gladiator-007/

# install main requirements.
COPY requirements.txt /deploy/
RUN pip3 install --no-cache-dir -r /deploy/requirements.txt

# install addons requirements
RUN wget -O /deploy/addons.txt https://git.io/JWdOk
RUN pip3 install --no-cache-dir -r /deploy/addons.txt

# start the bot
CMD ["bash", "resources/startup/startup.sh"]
