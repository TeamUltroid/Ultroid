# RYNO - UserBot
A stable pluggable Telegram userbot, based on Telethon.

<p align="center">
  <img src="./resources/extras/logo_rdm.png" alt="RYNO">
</p>

[![Stars](https://img.shields.io/github/stars/RYNO-X/RYNO?style=flat-square&color=green)](https://github.com/RYNO-X/RYNO/stargazers)
[![Forks](https://img.shields.io/github/forks/RYNO-X/RYNO?style=flat-square&color=green)](https://github.com/RYNO-X/RYNO/fork)
[![Python Version](https://img.shields.io/badge/Python-v3.9-blue)](https://www.python.org/)
[![Contributors](https://img.shields.io/github/contributors/RYNO-X/RYNO?style=flat-square&color=green)](https://github.com/RYNO-X/RYNO/graphs/contributors)
[![License](https://img.shields.io/badge/License-AGPL-blue)](https://github.com/RYNO-X/RYNO/blob/main/LICENSE)
[![Size](https://img.shields.io/github/repo-size/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/RYNO-X/RYNO/)

<details>
<summary>More Info</summary>
<br>
  <b>Documentation</b> - <a href="https://ultroid.tech">ultroid.tech</a>  <br />
</details>

# Deploy 
- [Heroku](https://github.com/RYNO-X/RYNO#Deploy-to-Heroku)
- [Local Machine](https://github.com/RYNO-X/RYNO#deploy-Locally)

## Deploy to Heroku
- Get your `API_ID` and `API_HASH` from [here](https://my.telegram.org/)    
- Get your `SESSION` from [here](https://repl.it/@TeamUltroid/UltroidStringSession#main.py).   
and click the below button!  <br />  

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Deploy Locally
- Get your `API_ID` and `API_HASH` from [here](https://my.telegram.org/)
- Get your `REDIS_URI` and `REDIS_PASSWORD` from [here](https://redislabs.com), tutorial [here](./resources/extras/redistut.md).
- Clone the repository: <br />
`git clone https://github.com/RYNO-X/RYNO.git`
- Go to the cloned folder: <br />
`cd RYNO`
- Create a virtual env:   <br />
`virtualenv -p /usr/bin/python3 venv`   
`. ./venv/bin/activate`
- Install the requirements:   <br />
`pip install -r requirements.txt`   
- Generate your `SESSION`:   
`bash sessiongen`
or
`bash -c "$(curl -fsSL https://del.dog/ultroid)"`
- Fill your details in a `.env` file, as given in [`.env.sample`](https://github.com/RYNO-X/RYNO/blob/main/.env.sample).    
(You can either edit and rename the file or make a new file.)
- Run the bot:   
`bash resources/startup/startup.sh`

Made with 💕 by @HUNTER_YUVRAJ 

# Credits
* [Lonami](https://github.com/LonamiWebs/) for [Telethon](https://github.com/LonamiWebs/Telethon)
👀
