# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM python:3.9.2-slim-buster
COPY resources/startup/deploy.sh .
RUN chmod +x deploy.sh && sh deploy.sh
WORKDIR /root/TeamUltroid/
CMD ["bash", "resources/startup/startup.sh"]
