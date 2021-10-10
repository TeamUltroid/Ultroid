<p align="center">
  <img src="./resources/extras/logo_readme.jpg" alt="TeamUltroid Logo">
</p>
<h1 align="center">
  <b>Ultroid - UserBot</b>
</h1>

<b>A stable pluggable Telegram userbot + Voice & Video Call music bot, based on Telethon.</b>   

[![Stars](https://img.shields.io/github/stars/TeamUltroid/Ultroid?style=flat-square&color=yellow)](https://github.com/TeamUltroid/Ultroid/stargazers)
[![Forks](https://img.shields.io/github/forks/TeamUltroid/Ultroid?style=flat-square&color=orange)](https://github.com/TeamUltroid/Ultroid/fork)
[![Size](https://img.shields.io/github/repo-size/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/TeamUltroid/Ultroid/)   
[![Python](https://img.shields.io/badge/Python-v3.9.7-blue)](https://www.python.org/)
[![CodeFactor](https://www.codefactor.io/repository/github/teamultroid/ultroid/badge/main)](https://www.codefactor.io/repository/github/teamultroid/ultroid/overview/main)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TeamUltroid/Ultroid/graphs/commit-activity)
[![Docker Pulls](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)
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
[![Documentation](https://img.shields.io/badge/Documentation-Ultroid-blue)](http://ultroid.tech/)

# Tutorial 
- Full Tutorial - [![Full Tutorial](https://img.shields.io/badge/Watch%20Now-blue)](https://www.youtube.com/watch?v=9wF7k9qA0Q4)

- Tutorial to get Redis URL and password - [here.](./resources/extras/redistut.md)
---

## Deploy to Heroku
Get the [Necessary Variables](#Necessary-Variables) and then click the button below!  

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?button-url=https%3A%2F%2Fgithub.com%2FNew-dev0%2FArchived&template=https%3A%2F%2Fgithub.com%2FNew-dev0%2FArchived)

## Deploy Locally
- [Traditional Method](#local-deploy---traditional-method)
- [Easy Method](#local-deploy---easy-method)
- [Latest Method](#local-deploy---latest-method)


### Local Deploy - Latest Method
This is the latest and most fastest method currently.<br>
First, go to [This Project](https://github.com/BLUE-DEVIL1134/UltroidCli) and install the latest release from the Github Releases.<br>
Then, do as it's given in the `README.md` to add the executable to your system path.

Further, take a look at the [`docs`](https://blue-devil1134.github.io/UltroidCli/) to get more information.


### Local Deploy - Easy Method
- Linux - `bash -c "$(curl -fsSL https://git.io/JY9UM)"`
- Windows - `cd desktop ; wget https://git.io/JY9UM -o locals.py ; python locals.py`
- Termux - `sh -c "$(curl -fsSL https://git.io/JY9UM)"`

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
`pip(3) install -U -r re*/st*/optional-requirements.txt`
`pip(3) install -U -r requirements.txt`
- Generate your `SESSION`:
  - For Linux users:
    `bash sessiongen`
     or
    `bash -c "$(curl -fsSL https://git.io/JY9JI)"`
  - For Termux users:
    `sh -c "$(curl -fsSL https://git.io/JqgsR)"`
  - For Windows Users:
    `cd desktop ; wget https://git.io/JY9JI -o ultroid.py ; python ultroid.py`
- Fill your details in a `.env` file, as given in [`.env.sample`](https://github.com/TeamUltroid/Ultroid/blob/main/.env.sample).
(You can either edit and rename the file or make a new file named `.env`.)
- Run the bot:
  - Linux Users:
   `bash resources/startup/startup.sh`
  - Windows Users:
    `python(3) -m pyUltroid`

## Necessary Variables
- `SESSION` - SessionString for your accounts login session. Get it from [here](#Session-String)
- `REDIS_URI` - Redis endpoint URL, from [redislabs](http://redislabs.com/), tutorial [here.](./resources/extras/redistut.md)
- `REDIS_PASSWORD` - Redis endpoint Password, from [redislabs](http://redislabs.com/), tutorial [here.](./resources/extras/redistut.md)

## Session String
Different ways to get your `SESSION`:
* [![Run on Repl.it](https://replit.com/badge/github/TeamUltroid/Ultroid)](https://replit.com/@TeamUltroid/UltroidStringSession)
* Linux : `bash -c "$(curl -fsSL https://git.io/JY9JI)"`
* PowerShell : `cd desktop ; wget https://git.io/JY9JI ; python ultroid.py`
* Termux : `sh -c "$(curl -fsSL https://da.gd/termux-tel)"`
* TelegramBot : [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)

Made with 💕 by [@TeamUltroid](https://t.me/TeamUltroid). <br />

# License
Ultroid is licensed under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) v3 or later.

[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)

# Credits
* [![TeamUltroid-Devs](https://img.shields.io/static/v1?label=Teamultroid&message=devs&color=critical)](https://t.me/UltroidDevs)
* [Lonami](https://github.com/LonamiWebs/) for [Telethon.](https://github.com/LonamiWebs/Telethon)
* [MarshalX](https://github.com/MarshalX) for [PyTgCalls.](https://github.com/MarshalX/tgcalls)

