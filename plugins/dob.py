from datetime import datetime as dt

from . import async_searcher, get_string, ultroid_bot, ultroid_cmd, LOGS


@ultroid_cmd(
    pattern=r"dob( (.*)|$)",
)
async def hbd(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor(get_string("spcltool_6"))
    if event.reply_to_msg_id:
        kk = await event.get_reply_message()
        nam = await kk.get_sender()
        name = nam.first_name
    else:
        name = ultroid_bot.me.first_name
    abhi = dt.now()
    kk = match.split("/")
    p = kk[0]
    r = kk[1]
    s = kk[2]
    day = int(p)
    month = r
    try:
        jn = dt.strptime(match, "%d/%m/%Y")
    except BaseException:
        return await event.eor(get_string("spcltool_6"))
    zinda = abhi - jn
    barsh = (zinda.total_seconds()) / (365.242 * 24 * 3600)
    saal = int(barsh)
    mash = (barsh - saal) * 12
    mahina = int(mash)
    divas = (mash - mahina) * (365.242 / 12)
    din = int(divas)
    samay = (divas - din) * 24
    ghanta = int(samay)
    pehl = (samay - ghanta) * 60
    mi = int(pehl)
    sec = (pehl - mi) * 60
    slive = int(sec)
    y = int(s) + saal + 1
    m = int(r)
    brth = dt(y, m, day)
    cm = dt(abhi.year, brth.month, brth.day)
    ish = (cm - abhi.today()).days + 1
    dan = ish
    hp = ""
    if dan == 0:
        hp = "`Happy BirthDay To U🎉🎊`"
    elif dan < 0:
        okk = 365 + ish
        hp = f"{okk} Days Left 🥳"
    elif dan > 0:
        hp = f"{ish} Days Left 🥳"
    if month == "01":
        sign = "Capricorn" if (day < 20) else "Aquarius"
    elif month == "02":
        sign = "Aquarius" if (day < 19) else "Pisces"
    elif month == "03":
        sign = "Pisces" if (day < 21) else "Aries"
    elif month == "04":
        sign = "Aries" if (day < 20) else "Taurus"
    elif month == "05":
        sign = "Taurus" if (day < 21) else "Gemini"
    elif month == "06":
        sign = "Gemini" if (day < 21) else "Cancer"
    elif month == "07":
        sign = "Cancer" if (day < 23) else "Leo"
    elif month == "08":
        sign = "Leo" if (day < 23) else "Virgo"
    elif month == "09":
        sign = "Virgo" if (day < 23) else "Libra"
    elif month == "10":
        sign = "Libra" if (day < 23) else "Scorpio"
    elif month == "11":
        sign = "Scorpio" if (day < 22) else "Sagittarius"
    elif month == "12":
        sign = "Sagittarius" if (day < 22) else "Capricorn"
    else:
        sign = ""
    message = f"""
**Name** -: {name}
**D.O.B** -:  {match}
**Lived** -:  {saal}yr, {mahina}m, {din}d, {ghanta}hr, {mi}min, {slive}sec

**Birthday** -: {hp}
**Zodiac** -: {sign}"""
    try:
        json = await async_searcher(
            f"https://aztro.sameerkumar.website/?sign={sign}&day=today",
            method="POST",
            re_json=True,
        )
        dd = json.get("current_date")
        ds = json.get("description")
        lt = json.get("lucky_time")
        md = json.get("mood")
        cl = json.get("color")
        ln = json.get("lucky_number")
        message += f"""\n**Horoscope On {dd} -**

`{ds}`
**Lucky Time** :-      {lt}
**Lucky Number** :-    {ln}
**Lucky Color** :-     {cl}
**Mood** :-            {md}
    """
    except Exception as er:
        LOGS.exception(er)
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        message,
        reply_to=event.reply_to_msg_id,
    )
