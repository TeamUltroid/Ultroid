# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from telethon.tl.custom import Button
from telethon.tl.types import InputWebDocument

from . import async_searcher, in_pattern


@in_pattern("gh", owner=True, button={"GɪᴛHᴜʙ ғᴇᴇᴅs": "gh"})
async def gh_feeds(ult):
    try:
        username = ult.text.split(maxsplit=1)[1]
    except IndexError:
        return await ult.answer(
            [],
            switch_pm="Enter Github Username to see feeds...",
            switch_pm_param="start",
        )
    if not username.endswith("."):
        return await ult.answer(
            [], switch_pm="End your query with . to search...", switch_pm_param="start"
        )
    username = username[:-1]
    data = await async_searcher(
        f"https://api.github.com/users/{username}/events", re_json=True
    )
    if not isinstance(data, list):
        msg = "".join(f"{ak}: `{data[ak]}" + "`\n" for ak in list(data.keys()))
        return await ult.answer(
            [
                await ult.builder.article(
                    title=data["message"], text=msg, link_preview=False
                )
            ],
            cache_time=300,
            switch_pm="Error!!!",
            switch_pm_param="start",
        )
    res = []
    res_ids = []
    for cont in data[:50]:
        text = f"<b><a href='https://github.com/{username}'>@{username}</a></b>"
        title = f"@{username}"
        extra = None
        if cont["type"] == "PushEvent":
            text += " pushed in"
            title += " pushed in"
            dt = cont["payload"]["commits"][-1]
            url = "https://github.com/" + dt["url"].split("/repos/")[-1]
            extra = f"\n-> <b>message:</b> <code>{dt['message']}</code>"
        elif cont["type"] == "IssueCommentEvent":
            title += " commented at"
            text += " commented at"
            url = cont["payload"]["comment"]["html_url"]
        elif cont["type"] == "CreateEvent":
            title += " created"
            text += " created"
            url = "https://github.com/" + cont["repo"]["name"]
        elif cont["type"] == "PullRequestEvent":
            if (
                cont["payload"]["pull_request"].get("user", {}).get("login")
                != username.lower()
            ):
                continue
            url = cont["payload"]["pull_request"]["html_url"]
            text += " created a pull request in"
            title += " created a pull request in"
        elif cont["type"] == "ForkEvent":
            text += " forked"
            title += " forked"
            url = cont["payload"]["forkee"]["html_url"]
        else:
            continue
        repo = cont["repo"]["name"]
        repo_url = f"https://github.com/{repo}"
        title += f" {repo}"
        text += f" <b><a href='{repo_url}'>{repo}</a></b>"
        if extra:
            text += extra
        thumb = InputWebDocument(
            cont["actor"]["avatar_url"], 0, "image/jpeg", [])
        article = await ult.builder.article(
            title=title,
            text=text,
            url=repo_url,
            parse_mode="html",
            link_preview=False,
            thumb=thumb,
            buttons=[
                Button.url("View", url),
                Button.switch_inline(
                    "Search again", query=ult.text, same_peer=True),
            ],
        )
        if article.id not in res_ids:
            res_ids.append(article.id)
            res.append(article)
    msg = f"Showing {len(res)} feeds!" if res else "Nothing Found"
    await ult.answer(res, cache_time=5000, switch_pm=msg, switch_pm_param="start")
