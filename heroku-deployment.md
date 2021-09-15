<div align="center">
<h1>Ultroid Manually Deploy via Heroku X Github Actions</h1>
<h3>This page will tell you how to deploy Ultroid to heroku through Github Actions</h3>
</div>


> Do not overuse it, or your account might be banned by Heroku.
> Dont abuse github actions...lets stay under the radar..



### 👉Pre Requisites
1️⃣ [Heroku Account](https://heroku.com) --- **mostly importantly needed for heroku api key and deployment**

2️⃣ [Telegram Account](https://telegram.org) --- **mostly importantly needed for the bot to work** 

3️⃣ [Some Patience](https://www.google.com/search?q=how+to+be+more+patient)

#### Steps

🎈1. **Fork this Repo**

🎈2. **Go to Repository `Settings` -> `Secrets`**
    ![Secrets](assets/step-1.png)

🎈3. **After filling the Required vars .... go to Actions and then tap on Run the Workflow**
    ![Actions](assets/step-2.png)

🎉4. **now wait it for it to deployed to heroku and Check app logs and Turn on Workers If OFF** **if everything is OK then send /help to the bot or try other cmds**...




## Environment Variables

### 🔴Required Environmental Variables... MUST BE GIVEN.... This Required ENV var is for Heroku Deployment only

| Variable | Value | Example | Required | Description |
| :---: | :---: | :---: | :---: | :---: |
| HEROKU_EMAIL | Heroku email | abc@abc.com | True | Just Give the email you used for Heroku Account|
| HEROKU_API_KEY | Heroku API key | xxxxxxx-xxxx-xxxx-xxxx-xxxxxx | True | Get it from [Heroku](https://dashboard.heroku.com/account/applications/authorizations/new) |
| HEROKU_APP_NAME | Heroku app name | Name Must be unique | True | Heroku app name that needs to be Updated or Created (Should be in lowercase) |
| API_ID | Telegram API_ID | Your TG account's API_ID | True | Get this value from [TELEGRAM](https://my.telegram.org/apps). |
| API_HASH | Telegram API_HASH | Your TG account's API_HASH | True | Get this value from [TELEGRAM](https://my.telegram.org/apps). |
| REDIS_URI | Redis Endpoint URL | redis-xxxxxxxxxxxxxxxxxxxxxxxxx.cloud.redislabs.com:xxxxx | True | Get this value from [REDIS LABS](https://redislabs.com). |
| REDIS_PASSWORD | Redis Endpoint Password | xxxxx | True | Get this value from [REDIS LABS](https://redislabs.com) |
| SESSION  | String Session of your Telegram Account | https://appname.herokuapp.com  | True | Get this from [Repl Run](https://repl.it/@TeamUltroid/UltroidStringSession#main.py) **(The bot will NOT work without a session string!!)** |
