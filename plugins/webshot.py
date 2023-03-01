import os

from playwright.async_api import async_playwright
from utilities.tools import check_filename, is_url_ok

from .. import get_string, ultroid_cmd


@ultroid_cmd(pattern="webshot( (.*)|$)")
async def webss(event):
    xx = await event.eor(get_string("com_1"))
    args = event.pattern_match.group(1).strip().split(" ")
    if not args:
        return await xx.eor(get_string("wbs_1"), time=5)
    xurl = args[0]
    if not (await is_url_ok(xurl)):
        return await xx.eor(get_string("wbs_2"), time=5)
    path = check_filename("shot.png")
    async with async_playwright() as playwright:
        chrome = await playwright.chromium.launch()
        page = await chrome.new_page()
        await page.goto(xurl)
        if "--wait" in args:
            try:
                tim = int(args[args.index("--wait") + 1])
                await page.wait_for_timeout(tim)
            except (KeyError, ValueError):
                pass
        await page.screenshot(path=path, full_page=not "--short" in args)
    await xx.reply(
        get_string("wbs_3").format(xurl),
        file=path,
        link_preview=False,
        force_document=True,
    )
    os.remove(path)
    await xx.delete()
