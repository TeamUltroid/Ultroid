# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import sys
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from . import get_string

UPSTREAM_REPO_URL = "https://github.com/TeamUltroid/Ultroid"
requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "On %d/%m/%y at %H:%M:%S"
    for c in repo.iter_commits(diff):
        ch_log += f"**#{c.count()}** : {c.committed_datetime.strftime(d_form)} : [{c.summary}]({UPSTREAM_REPO_URL.rstrip('/')}/commit/{c}) by `{c.author}`\n"
    return ch_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


@ultroid_cmd(
    pattern="update ?(.*)",
)
async def upstream(ups):
    pagal = await eor(ups, get_string("upd_1"))
    conf = ups.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    try:
        txt = get_string("upd_2")
        repo = Repo()
    except NoSuchPathError as error:
        await eod(pagal, f"{txt}\n`directory {error} is not found`", time=10)
        repo.__del__()
        return
    except GitCommandError as error:
        await eod(pagal, f"{txt}\n`Early failure! {error}`", time=10)
        repo.__del__()
        return
    except InvalidGitRepositoryError as error:
        if conf != "now":
            await eod(
                pagal,
                f"**Unfortunately, the directory {error} does not seem to be a git repository.Or Maybe it just needs a sync verification with {GIT_REPO_NAME} But we can fix that by force updating the userbot using** `.update now.`",
                time=30,
            )
            return
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    #    if ac_br != "main":
    #        await eod(
    #            pagal,
    #            f"**[UPDATER]:**` You are on ({ac_br})\n Please change to the main branch.`",
    #        )
    #        repo.__del__()
    #        return
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if "now" not in conf:
        if changelog:
            changelog_str = get_string("upd_3").format(
                ac_br, UPSTREAM_REPO_URL, ac_br, changelog
            )
            if len(changelog_str) > 4096:
                await eor(pagal, get_string("upd_4"))
                file = open("output.txt", "w+")
                file.write(changelog_str)
                file.close()
                await ups.client.send_file(
                    ups.chat_id,
                    "output.txt",
                    caption=get_string("upd_5").format(hndlr),
                    reply_to=ups.id,
                )
                remove("output.txt")
            else:
                return await eod(
                    pagal, get_string("upd_6").format(changelog_str, hndlr)
                )
        else:
            await eod(
                pagal,
                get_string("upd_7").format(ac_br, UPSTREAM_REPO_URL, ac_br),
                time=10,
            )
            repo.__del__()
            return
    if Var.HEROKU_API is not None:
        import heroku3

        heroku = heroku3.from_key(Var.HEROKU_API)
        heroku_app = None
        heroku_applications = heroku.apps()
        if not Var.HEROKU_APP_NAME:
            await eod(
                pagal,
                "`Please set up the `HEROKU_APP_NAME` variable to be able to update userbot.`",
                time=10,
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await eod(
                pagal,
                f"{txt}\n`Invalid Heroku credentials for updating userbot dyno.`",
                time=10,
            )
            repo.__del__()
            return
        await eor(
            pagal, "`Userbot dyno build in progress, please wait for it to complete.`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + Var.HEROKU_API + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eod(pagal, f"{txt}\n`Here is the error log:\n{error}`", time=10)
            repo.__del__()
            return
        await eod(pagal, "`Successfully Updated!\nRestarting, please wait...`", time=60)
    else:
        # Classic Updater, pretty straightforward.
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eod(
            pagal,
            "`Successfully Updated!\nBot is restarting... Wait for a second!`",
        )
        # Spin a new instance of bot
        args = [sys.executable, "./resources/startup/deploy.sh"]
        execle(sys.executable, *args, environ)
        return
