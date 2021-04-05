# Ultroid - UserBot
A stable pluggable Telegram userbot, based on Telethon.

<p align="center">
  <img src="./resources/extras/logo_readme.jpg" alt="TeamUltroid Logo">
</p>
<h1 align="center">
  <b>Ultroid - UserBot</b>
</h1>

[![Stars](https://img.shields.io/github/stars/TeamUltroid/Ultroid?style=flat-square&color=yellow)](https://github.com/TeamUltroid/Ultroid/stargazers)
[![Forks](https://img.shields.io/github/forks/TeamUltroid/Ultroid?style=flat-square&color=orange)](https://github.com/TeamUltroid/Ultroid/fork)
[![Size](https://img.shields.io/github/repo-size/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/TeamUltroid/Ultroid/)
[![Python](https://img.shields.io/badge/Python-v3.9-blue)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TeamUltroid/Ultroid/graphs/commit-activity)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/TeamUltroid/Ultroid)
[![Contributors](https://img.shields.io/github/contributors/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/TeamUltroid/Ultroid/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![License](https://img.shields.io/badge/License-AGPL-blue)](https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE)
[![Sparkline](https://stars.medv.io/Teamultroid/Ultroid.svg)](https://stars.medv.io/TeamUltroid/Ultroid)

----

# Deploy
- [Heroku](#Deploy-to-Heroku)
- [Local Machine](#Deploy-Locally)

# Documentation 
The documentation can be found [here.](https://ultroid.org/)

# Tutorial 
- Full Tutorial - [![Full Tutorial](https://img.shields.io/badge/Watch%20Now-blue)](https://www.youtube.com/watch?v=9wF7k9qA0Q4)

- Tutorial to get Redis URL and password - [here.](./resources/extras/redistut.md)
---

## Deploy to Heroku
Get the [Necessary Variables](#Necessary-Variables) and then click the button below!  

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Deploy Locally
- [Traditional Method](#local-deploy---traditional-method)
- [Easy Method](#local-deploy---easy-method)

### Local Deploy - Easy Method
- Linux - `bash -c "$(curl -fsSL https://git.io/JY9UM)"`
- Windows - `cd desktop ; wget https://del.dog/raw/ultroid-termux -o locals.py ; python locals.py`
- Termux - `sh -c "$(curl -fsSL https://del.dog/raw/ultroid-termux)"`

### Local Deploy - Traditional Method
- Get your [Necessary Variables](#Necessary-Variables)
- Clone the repository: <br />
`git clone https://github.com/TeamUltroid/Ultroid.git`
- Go to the cloned folder: <br />
`cd Ultroid`
- Create a virtual env:   <br />
`virtualenv -p /usr/bin/python3 venv`
`. ./venv/bin/activate`
- Install the requirements:   <br />
`pip(3) install -U -r requirements.txt`
- Generate your `SESSION`:
  - For Linux users:
    `bash sessiongen`
     or
    `bash -c "$(curl -fsSL https://del.dog/ultroid)"`
  - For Termux users:
    `sh -c "$(curl -fsSL https://da.gd/termux-tel)"`
  - For Windows Users:
    `cd desktop ; wget https://del.dog/ultroid -o ultroid.py ; python ultroid.py`
- Fill your details in a `.env` file, as given in [`.env.sample`](https://github.com/TeamUltroid/Ultroid/blob/main/.env.sample).
(You can either edit and rename the file or make a new file named `.env`.)
- Run the bot:
  - Linux Users:
   `bash resources/startup/startup.sh`
  - Windows Users:
    `python(3) -m pyUltroid`

## Necessary Variables
- `API_ID` - Your API_ID from [my.telegram.org](https://my.telegram.org/)
- `API_HASH` - Your API_HASH from [my.telegram.org](https://my.telegram.org/)
- `SESSION` - SessionString for your accounts login session. Get it from [here](#Session-String)
- `BOT_TOKEN` - The token of your bot from [@BotFather](https://t.me/BotFather)
- `BOT_USERNAME` - The username of your bot from [@BotFather](https://t.me/BotFather)
- `LOG_CHANNEL` - A private group/channel id.
- `REDIS_URI` - Redis endpoint URL, from [redislabs](http://redislabs.com/), tutorial [here.](./resources/extras/redistut.md)
- `REDIS_PASSWORD ` - Redis endpoint Password, from [redislabs](http://redislabs.com/), tutorial [here.](./resources/extras/redistut.md)

## Session String
Different ways to get your `SESSION`:
* [![Run on Repl.it](https://replit.com/badge/github/TeamUltroid/Ultroid)](https://replit.com/@TeamUltroid/UltroidStringSession)
* Run `bash -c "$(curl -fsSL https://del.dog/ultroid)"`, if on a linux.
* Run `cd desktop ; wget https://git.io/JY9JI ; python ultroid.py` on PowerShell.

Made with 💕 by [@TeamUltroid](https://t.me/TeamUltroid). <br />

# Credits
* [Lonami](https://github.com/LonamiWebs/) for [Telethon](https://github.com/LonamiWebs/Telethon)

# License
Ultroid is licensed under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) v3 or later.

[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)
