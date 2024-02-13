# Ultroid ~ UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
# original plugin from Uniborg.
# credits to original creator|s.
# ported to ultroid by [eris.]

from . import get_help

__doc__ = get_help("help_weather")

import asyncio
import io
import time

from . import *
from . import async_searcher


@ultroid_cmd(pattern="weather ?(.*)")
async def _(event):
    if event.fwd_from:
        return
    reply = await eor(event, get_string("com_1"))
    sample_url = (
        "https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric"
    )
    x = udB.get_key("OPENWEATHER_API")
    if x is None:
        error = f"No API found. Get One from [Here](https://api.openweathermap.org) \n"
        error += "And Add it in `OPENWEATHER_API` Redis Key"
        await reply.edit(error)
        return
    input_str = event.pattern_match.group(1)
    if not input_str:
        await reply.edit("`No Location was Given..`")
        return
    elif input_str == "butler":
        await reply.edit("search `butler,au` for australila")
        asyncio.sleep(2)

    async def evaluate_response(response):
        response_api = await response.json()
        if response_api["cod"] == 200:
            country_time_zone = int(response_api["timezone"])
            sun_rise_time = int(response_api["sys"]["sunrise"]) + country_time_zone
            sun_set_time = int(response_api["sys"]["sunset"]) + country_time_zone
            return (
                f"**Weather for {input_str}**\n"
                f"__Country__ : **{response_api['sys']['country']}**\n\n"
                f"• **Temperature :** {response_api['main']['temp']}°С\n"
                f"    •  __minimium__ : {response_api['main']['temp_min']}°С\n"
                f"    •  __maximum__ : {response_api['main']['temp_max']}°С\n"
                f"    •  __feels like__ : {response_api['main']['feels_like']}°C\n\n"
                f"• **Humidity :** {response_api['main']['humidity']}%\n"
                f"• **Wind Speed :** {response_api['wind']['speed']}m/s\n"
                f"• **Clouds :** {response_api['clouds']['all']} hpa\n"
                f"• **Pressure :** {response_api['main']['pressure']}mb\n"
                f"• **Visibility :** {response_api['visibility']}m\n\n"
                f"• **Sunrise :** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_rise_time))}\n"
                f"• **Sunset :** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_set_time))}"
            )
        else:
            return response_api["message"]

    try:
        response_data = await async_searcher(
            sample_url.format(input_str, x), evaluate=evaluate_response
        )
        await reply.edit(response_data)
    except Exception as e:
        LOGS.exception(f"Error: {str(e)}")
        error_message = f"An unexpected error occurred: {str(e)}"
        await reply.edit(error_message)
