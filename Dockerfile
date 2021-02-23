# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM python:3.9.2
RUN chmod +x /usr/local/bin/*
RUN wget https://raw.githubusercontent.com/TeamUltroid/Ultroid/beta/resources/startup/deploy.sh
RUN sh deploy.sh
WORKDIR /root/TeamUltroid/
CMD ["bash", "resources/startup/startup.sh"]
