# Ultroid ~ UserBot
# Copyright (C) 2023-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
**Get Weather Data using OpenWeatherMap API**
❍  Commands Available -

• `{i}weather` <city name>
    Shows the Weather of Cities

• `{i}air` <city name>
    Shows the Air Condition of Cities
"""

import datetime
import time
import asyncio
from datetime import timedelta
from json import JSONDecodeError

import aiohttp
import pytz

from . import LOGS, async_searcher, get_string, udB, ultroid_cmd


async def get_timezone(offset_seconds, use_utc=False):
    offset = timedelta(seconds=offset_seconds)
    total_seconds = int(offset.total_seconds())
    hours = abs(total_seconds) // 3600
    sign = "+" if total_seconds >= 0 else "-"
    timezone = "UTC" if use_utc else "GMT"
    if use_utc:
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            now = datetime.datetime.now(tz)
            if now.utcoffset() == offset:
                return f"{m} ({timezone}{sign}{hours:02d})"
    else:
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            if m.startswith("Australia/"):
                now = datetime.datetime.now(tz)
                if now.utcoffset() == offset:
                    return f"{m} ({timezone}{sign}{hours:02d})"
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            now = datetime.datetime.now(tz)
            if now.utcoffset() == offset:
                return f"{m} ({timezone}{sign}{hours:02d})"
        return "Timezone not found"

async def getWindinfo(speed: str, degree: str) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ix = round(degree / (360.00 / len(dirs)))
    kmph = str(float(speed) * 3.6) + " km/h"
    return f"[{dirs[ix % len(dirs)]}] {kmph}"

async def get_air_pollution_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_key}"
    timeout = aiohttp.ClientTimeout(total=12)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                data = await response.json()
    except (asyncio.TimeoutError, TimeoutError):
        LOGS.exception("OpenWeather air pollution request timed out.")
        return None, "Air quality lookup timed out. Please try again in a moment."
    except aiohttp.ClientError:
        LOGS.exception("OpenWeather air pollution request failed.")
        return None, "Unable to reach the air quality service right now. Try again soon."
    except (aiohttp.ContentTypeError, JSONDecodeError, ValueError):
        LOGS.exception("Invalid air pollution response payload.")
        return None, "Air quality service returned invalid data. Please try again."

    try:
        air_pollution = data["list"][0]
    except (KeyError, IndexError, TypeError):
        LOGS.exception("Air pollution response missing expected fields: %s", data)
        return None, "No air quality data found for that location. Try city,country format."
    return air_pollution, None


async def get_geocode_data(input_str: str):
    if input_str.lower() == "perth":
        geo_url = "https://geocode.xyz/perth%20au?json=1"
    else:
        geo_url = f"https://geocode.xyz/{input_str}?json=1"
    try:
        geo_data = await async_searcher(geo_url, re_json=True, timeout=12)
    except (asyncio.TimeoutError, TimeoutError):
        LOGS.exception("Geocoding request timed out for location: %s", input_str)
        return None, "Geocoding timed out. Try city,country format."
    except aiohttp.ClientError:
        LOGS.exception("Geocoding request failed for location: %s", input_str)
        return None, "Unable to reach geocoding service. Try again soon."
    except (aiohttp.ContentTypeError, JSONDecodeError, ValueError, TypeError):
        LOGS.exception("Geocoding response is not valid JSON for location: %s", input_str)
        return None, "Could not read geocoding response. Try city,country format."

    try:
        latitude = geo_data["latt"]
        longitude = geo_data["longt"]
        city = geo_data["standard"]["city"]
        prov = geo_data["standard"]["prov"]
    except (KeyError, TypeError):
        LOGS.exception("Geocoding response missing expected fields: %s", geo_data)
        return None, "Location not found. Try city,country format (example: London,GB)."
    return {"latitude": latitude, "longitude": longitude, "city": city, "prov": prov}, None


@ultroid_cmd(pattern="weather ?(.*)")
async def weather(event):
    if event.fwd_from:
        return
    msg = await event.eor(get_string("com_1"))
    x = udB.get_key("OPENWEATHER_API")
    if x is None:
        await event.eor(
            "No API found. Get One from [Here](https://api.openweathermap.org)\nAnd Add it in OPENWEATHER_API Redis Key",
            time=8,
        )
        return
    input_str = event.pattern_match.group(1)
    if not input_str:
        await event.eor("No location was given. Try city,country format.", time=5)
        return
    elif input_str == "butler":
        await event.eor("Search butler,au for Australia.", time=5)
        return
    sample_url = f"https://api.openweathermap.org/data/2.5/weather?q={input_str}&APPID={x}&units=metric"
    try:
        response_api = await async_searcher(sample_url, re_json=True)
        if str(response_api.get("cod")) == "200":
            country_time_zone = int(response_api["timezone"])
            tz = f"{await get_timezone(country_time_zone)}"
            sun_rise_time = int(response_api["sys"]["sunrise"]) + country_time_zone
            sun_set_time = int(response_api["sys"]["sunset"]) + country_time_zone
            await msg.edit(
                f"{response_api['name']}, {response_api['sys']['country']}\n\n"
                f"╭────────────────•\n"
                f"╰➢ **𝖶𝖾𝖺𝗍𝗁𝖾𝗋:** {response_api['weather'][0]['description']}\n"
                f"╰➢ **𝖳𝗂𝗆𝖾𝗓𝗈𝗇𝖾:** {tz}\n"
                f"╰➢ **𝖲𝗎𝗇𝗋𝗂𝗌𝖾:** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_rise_time))}\n"
                f"╰➢ **𝖲𝗎𝗇𝗌𝖾𝗍:** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_set_time))}\n"
                f"╰➢ **𝖶𝗂𝗇𝖽:** {await getWindinfo(response_api['wind']['speed'], response_api['wind']['deg'])}\n"
                f"╰➢ **𝖳𝖾𝗆𝗉𝖾𝗋𝖺𝗍𝗎𝗋𝖾:** {response_api['main']['temp']}°C\n"
                f"╰➢ **𝖥𝖾𝖾𝗅𝗌 𝗅𝗂𝗄𝖾:** {response_api['main']['feels_like']}°C\n"
                f"╰➢ **𝖬𝗂𝗇𝗂𝗆𝗎𝗆:** {response_api['main']['temp_min']}°C\n"
                f"╰➢ **𝖬𝖺𝗑𝗂𝗆𝗎𝗆:** {response_api['main']['temp_max']}°C\n"
                f"╰➢ **𝖯𝗋𝖾𝗌𝗌𝗎𝗋𝖾:** {response_api['main']['pressure']} hPa\n"
                f"╰➢ **𝖧𝗎𝗆𝗂𝖽𝗂𝗍𝗒:** {response_api['main']['humidity']}%\n"
                f"╰➢ **𝖵𝗂𝗌𝗂𝖻𝗂𝗅𝗂𝗍𝗒:** {response_api['visibility']} m\n"
                f"╰➢ **𝖢𝗅𝗈𝗎𝖽𝗌:** {response_api['clouds']['all']}%\n"
                f"╰────────────────•\n\n"
            )
        else:
            await msg.edit(response_api.get("message", "Location not found. Try city,country format."))
    except Exception:
        LOGS.exception("Weather lookup failed for input: %s", input_str)
        await event.eor(
            "Unable to fetch weather right now. Try city,country format.",
            time=5,
        )


@ultroid_cmd(pattern="air ?(.*)")
async def air_pollution(event):
    if event.fwd_from:
        return
    msg = await event.eor(get_string("com_1"))
    x = udB.get_key("OPENWEATHER_API")
    if x is None:
        await event.eor(
            "No API found. Get One from [Here](https://api.openweathermap.org)\nAnd Add it in OPENWEATHER_API Redis Key",
            time=8,
        )
        return
    input_str = event.pattern_match.group(1)
    if not input_str:
        await event.eor("No location was given. Try city,country format.", time=5)
        return
    geocode_data, geocode_error = await get_geocode_data(input_str)
    if geocode_error:
        await event.eor(geocode_error, time=5)
        return
    air_pollution_data, air_error = await get_air_pollution_data(
        geocode_data["latitude"], geocode_data["longitude"], x
    )
    if air_error:
        await event.eor(air_error, time=5)
        return
    try:
        await msg.edit(
            f"{geocode_data['city']}, {geocode_data['prov']}\n\n"
            f"╭────────────────•\n"
            f"╰➢ **𝖠𝖰𝖨:** {air_pollution_data['main']['aqi']}\n"
            f"╰➢ **𝖢𝖺𝗋𝖻𝗈𝗇 𝖬𝗈𝗇𝗈𝗑𝗂𝖽𝖾:** {air_pollution_data['components']['co']}µg/m³\n"
            f"╰➢ **𝖭𝗂𝗍𝗋𝗈𝗀𝖾𝗇 𝖬𝗈𝗇𝗈𝗑𝗂𝖽𝖾:** {air_pollution_data['components']['no']}µg/m³\n"
            f"╰➢ **𝖭𝗂𝗍𝗋𝗈𝗀𝖾𝗇 𝖣𝗂𝗈𝗑𝗂𝖽𝖾:** {air_pollution_data['components']['no2']}µg/m³\n"
            f"╰➢ **𝖮𝗓𝗈𝗇𝖾:** {air_pollution_data['components']['o3']}µg/m³\n"
            f"╰➢ **𝖲𝗎𝗅𝗉𝗁𝗎𝗋 𝖣𝗂𝗈𝗑𝗂𝖽𝖾:** {air_pollution_data['components']['so2']}µg/m³\n"
            f"╰➢ **𝖠𝗆𝗆𝗈𝗇𝗂𝖺:** {air_pollution_data['components']['nh3']}µg/m³\n"
            f"╰➢ **𝖥𝗂𝗇𝖾 𝖯𝖺𝗋𝗍𝗂𝖼𝗅𝖾𝗌 (PM₂.₅):** {air_pollution_data['components']['pm2_5']}\n"
            f"╰➢ **𝖢𝗈𝖺𝗋𝗌𝖾 𝖯𝖺𝗋𝗍𝗂𝖼𝗅𝖾𝗌 (PM₁₀):** {air_pollution_data['components']['pm10']}\n"
            f"╰────────────────•\n\n"
        )
    except (KeyError, TypeError):
        LOGS.exception("Air pollution data missing display fields: %s", air_pollution_data)
        await event.eor("Air quality data is incomplete for this location. Try city,country format.", time=5)
