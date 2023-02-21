# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}covid country name`
    Gets the Covid-19 Status of a given Country.
"""

from covid import Covid

from . import ultroid_cmd


@ultroid_cmd(pattern="covid")
async def coronish(event):
    covid = Covid()
    okie = event.text.split(maxsplit=1)
    try:
        country = okie[1]
    except IndexError:
        await event.eor("Give a country name to Search for it's Covid Cases!")
        return
    try:
        cases = covid.get_status_by_country_name((country).lower())
        act = cases["active"]
        conf = cases["confirmed"]
        dec = cases["deaths"]
        rec = cases["recovered"]
        await event.eor(
            f"**Country:** **{country.capitalize()}**\n**Active:** {act}\n**Confirmed:** {conf}\n**Recovered:** {rec}\n**Deceased:** {dec}",
        )
    except ValueError:
        await event.eor(f"It seems that Country {country} is invalid!")
