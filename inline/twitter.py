from random import choice
from telethon.tl.types import InputWebDocument  as wb
from . import in_pattern, async_searcher

# Thanks to OpenSource
_bearer_collected = [
    "AAAAAAAAAAAAAAAAAAAAALIKKgEAAAAA1DRuS%2BI7ZRKiagD6KHYmreaXomo%3DP5Vaje4UTtEkODg0fX7nCh5laSrchhtLxeyEqxXpv0w9ZKspLD",
    "AAAAAAAAAAAAAAAAAAAAAL5iUAEAAAAAmo6FYRjqdKlI3cNziIm%2BHUQB9Xs%3DS31pj0mxARMTOk2g9dvQ1yP9wknvY4FPBPUlE00smJcncw4dPR",
    "AAAAAAAAAAAAAAAAAAAAAN6sVgEAAAAAMMjMMWrwgGyv7YQOWN%2FSAsO5SGM%3Dg8MG9Jq93Rlllaok6eht7HvRCruN4Vpzp4NaVsZaaHHWSTzKI8",
]

_cache = {}

@in_pattern("twitter", owner=True, button={"Twitter User": "twitter theultroid"})
async def twitter_search(event):
    try:
        match = event.text.split(maxsplit=1)[1].lower()
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Query to Search", switch_pm_param="start"
        )
    try:
        return await event.answer(
            _cache[match],
            switch_pm="• Twitter Search •",
            switch_pm_param="start",
        )
    except KeyError:
        pass
    headers = {"Authorization": f"bearer {choice(_bearer_collected)}"}
    res = await async_searcher(
        f"https://api.twitter.com/1.1/users/search.json?q={match}",
        headers=headers,
        re_json=True,
    )
    reso = []
    for user in res:
        thumb = wb(user["profile_image_url_https"], 0, "image/jpeg", [])
        if user.get("profile_banner_url"):
            url = user["profile_banner_url"]
            text = f"[\xad]({url})• **Name :** `{user['name']}`\n"
        else:
            text = f"• **Name :** `{user['name']}`\n"
        text += f"• **Description :** `{user['description']}`\n"
        text += f"• **Username :** `@{user['screen_name']}`\n"
        text += f"• **Followers :** `{user['followers_count']}`    • **Following :** `{user['friends_count']}`\n"
        pro_ = "https://twitter.com/" + user["screen_name"]
        text += f"• **Link :** [Click Here]({pro_})\n_"
        reso.append(
            await event.builder.article(
                title=user["name"],
                description=user["description"],
                url=pro_,
                text=text,
                thumb=thumb,
            )
        )
    swi_ = f"🐦 Showing {len(reso)} Results!" if reso else "No User Found :("
    await event.answer(reso, switch_pm=swi_, switch_pm_param="start")
    _cache[match] = reso

