import io
from . import ultroid_cmd, get_string, async_searcher


@ultroid_cmd(pattern="meaning( (.*)|$)", manager=True)
async def meaning(event):
    wrd = event.pattern_match.group(1).strip()
    if not wrd:
        return await event.eor(get_string("wrd_4"))
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{wrd}"
    out = await async_searcher(url, re_json=True)
    try:
        return await event.eor(f'**{out["title"]}**')
    except (KeyError, TypeError):
        pass
    defi = out[0]["meanings"][0]["definitions"][0]
    ex = defi["example"] if defi.get("example") else "None"
    text = get_string("wrd_1").format(wrd, defi["definition"], ex)
    if defi.get("synonyms"):
        text += (
            f"\n\n• **{get_string('wrd_5')} :**"
            + "".join(f" {a}," for a in defi["synonyms"])[:-1][:10]
        )
    if defi.get("antonyms"):
        text += (
            f"\n\n**{get_string('wrd_6')} :**"
            + "".join(f" {a}," for a in defi["antonyms"])[:-1][:10]
        )
    if len(text) > 4096:
        with io.BytesIO(str.encode(text)) as fle:
            fle.name = f"{wrd}-meanings.txt"
            await event.reply(
                file=fle,
                force_document=True,
                caption=f"Meanings of {wrd}",
            )
            await event.delete()
    else:
        await event.eor(text)


@ultroid_cmd(
    pattern="(syno|anto)nym",
)
async def mean(event):
    task = event.pattern_match.group(1) + "nyms"
    try:
        wrd = event.text.split(maxsplit=1)[1]
    except IndexError:
        return await event.eor("Give Something to search..")
    try:
        ok = await get_synonyms_or_antonyms(wrd, task)
        x = get_string("wrd_2" if task == "synonyms" else "wrd_3").format(wrd)
        for c, i in enumerate(ok, start=1):
            x += f"**{c}.** `{i}`\n"
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-{task}.txt"
                await event.client.send_file(
                    event.chat_id,
                    fle,
                    force_document=True,
                    allow_cache=False,
                    caption=f"{task} of {wrd}",
                    reply_to=event.reply_to_msg_id,
                )
                await event.delete()
        else:
            await event.eor(x)
    except Exception as e:
        await event.eor(
            get_string("wrd_7" if task == "synonyms" else "wrd_8").format(e)
        )



async def get_synonyms_or_antonyms(word, type_of_words):
    if type_of_words not in ["synonyms", "antonyms"]:
        return "Dude! Please give a corrent type of words you want."
    s = await async_searcher(
        f"https://tuna.thesaurus.com/pageData/{word}", re_json=True
    )
    li_1 = [
        y
        for x in [
            s["data"]["definitionData"]["definitions"][0][type_of_words],
            s["data"]["definitionData"]["definitions"][1][type_of_words],
        ]
        for y in x
    ]
    return [y["term"] for y in li_1]
