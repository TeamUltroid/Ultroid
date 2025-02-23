# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}tw <tweet text>`
    Tweet the text.

• `{i}twr <tweet id/link>`
    Get tweet details with reply/quote/comment count.

• `{i}twuser <username>`
    Get user details of the Twitter account.

• `{i}twl <tweet link>`
    Upload the tweet media to telegram.

"""

import os
from twikit import Client
from . import LOGS, eor, get_string, udB, ultroid_cmd

# Store client globally
twitter_client = None

# Get path to cookies file
COOKIES_FILE = "resources/auth/twitter_cookies.json"

async def get_client():
    global twitter_client
    if twitter_client:
        return twitter_client
        
    if not all(udB.get_key(key) for key in ["TWITTER_USERNAME", "TWITTER_EMAIL", "TWITTER_PASSWORD"]):
        raise Exception("Set TWITTER_USERNAME, TWITTER_EMAIL and TWITTER_PASSWORD in vars first!")
    
    # Create auth directory if it doesn't exist
    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        
    client = Client()
    await client.login(
        auth_info_1=udB.get_key("TWITTER_USERNAME"),
        auth_info_2=udB.get_key("TWITTER_EMAIL"), 
        password=udB.get_key("TWITTER_PASSWORD"),
        cookies_file=COOKIES_FILE
    )
    twitter_client = client
    return client



@ultroid_cmd(pattern="tw( (.*)|$)")
async def tweet_cmd(event):
    """Post a tweet"""
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.eor("🚫 `Give some text to tweet!`")

    msg = await event.eor("🕊 `Tweeting...`")
    try:
        client = await get_client()
        tweet = await client.create_tweet(text=text)
        await msg.edit(f"✨ **Successfully Posted!**\n\n🔗 https://x.com/{tweet.user.screen_name}/status/{tweet.id}")
    except Exception as e:
        await msg.edit(f"❌ **Error:**\n`{str(e)}`")


@ultroid_cmd(pattern="twdetail( (.*)|$)")
async def twitter_details(event):
    """Get tweet details"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Give tweet ID/link to get details!`")

    msg = await event.eor("🔍 `Getting tweet details...`")
    try:
        client = await get_client()
        from urllib.parse import urlparse
        parsed_url = urlparse(match)
        if parsed_url.hostname in ["twitter.com", "x.com"]:
            tweet_id = parsed_url.path.split("/")[-1].split("?")[0]
        else:
            tweet_id = match

        tweet = await client.get_tweet_by_id(tweet_id)
        text = "🐦 **Tweet Details**\n\n"
        text += f"📝 **Content:** `{tweet.text}`\n\n"
        if hasattr(tweet, "metrics"):
            text += f"❤️ **Likes:** `{tweet.metrics.likes}`\n"
            text += f"🔄 **Retweets:** `{tweet.metrics.retweets}`\n"
            text += f"💬 **Replies:** `{tweet.metrics.replies}`\n"
            text += f"👁 **Views:** `{tweet.metrics.views}`\n"
        
        await msg.edit(text)
    except Exception as e:
        await msg.edit(f"❌ **Error:**\n`{str(e)}`")


@ultroid_cmd(pattern="twuser( (.*)|$)")
async def twitter_user(event):
    """Get user details"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Give username to get details!`")

    msg = await event.eor("🔍 `Getting user details...`")
    try:
        client = await get_client()
        user = await client.get_user_by_screen_name(match)
        text = "👤 **Twitter User Details**\n\n"
        text += f"📛 **Name:** `{user.name}`\n"
        text += f"🔖 **Username:** `@{user.screen_name}`\n"
        text += f"📝 **Bio:** `{user.description}`\n\n"
        text += f"👥 **Followers:** `{user.followers_count}`\n"
        text += f"👣 **Following:** `{user.following_count}`\n"
        text += f"🐦 **Total Tweets:** `{user.statuses_count}`\n"
        text += f"📍 **Location:** `{user.location or 'Not Set'}`\n"
        text += f"✅ **Verified:** `{user.verified}`\n"
        
        if user.profile_image_url:
            image_url = user.profile_image_url.replace("_normal.", ".")
            await event.client.send_file(
                event.chat_id,
                file=image_url,
                caption=text,
                force_document=False
            )
            await msg.delete()
        else:
            await msg.edit(text)
            
    except Exception as e:
        await msg.edit(f"❌ **Error:**\n`{str(e)}`")


@ultroid_cmd(pattern="twl( (.*)|$)")
async def twitter_media(event):
    """Download tweet media"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Give tweet link to download media!`")

    msg = await event.eor("📥 `Downloading media...`")
    try:
        client = await get_client()
        if "twitter.com" in match or "x.com" in match:
            tweet_id = match.split("/")[-1].split("?")[0]
        else:
            tweet_id = match

        tweet = await client.get_tweet_by_id(tweet_id)
        
        if not hasattr(tweet, "media"):
            return await msg.edit("😕 `No media found in tweet!`")

        # Prepare caption with tweet text
        caption = f"🐦 **Tweet by @{tweet.user.screen_name}**\n\n"
        caption += f"{tweet.text}\n\n"
        if hasattr(tweet, "metrics"):
            caption += f"❤️ `{tweet.metrics.likes}` 🔄 `{tweet.metrics.retweets}` 💬 `{tweet.metrics.replies}`"

        media_count = 0
        for media in tweet.media:
            if media.type == "photo":
                await event.client.send_file(
                    event.chat_id, 
                    media.url,
                    caption=caption if media_count == 0 else None  # Only add caption to first media
                )
                media_count += 1
            elif media.type == "video":
                if hasattr(media, "video_info") and isinstance(media.video_info, dict):
                    variants = media.video_info.get("variants", [])
                    mp4_variants = [
                        v for v in variants 
                        if v.get("content_type") == "video/mp4" and "bitrate" in v
                    ]
                    if mp4_variants:
                        best_video = max(mp4_variants, key=lambda x: x["bitrate"])
                        video_caption = caption if media_count == 0 else ""  # Only add tweet text to first media
                        if video_caption:
                            video_caption += f"\n🎥 Video Quality: {best_video['bitrate']/1000:.0f}kbps"
                        else:
                            video_caption = f"🎥 Video Quality: {best_video['bitrate']/1000:.0f}kbps"
                            
                        await event.client.send_file(
                            event.chat_id,
                            best_video["url"],
                            caption=video_caption
                        )
                        media_count += 1

        if media_count > 0:
            await msg.edit(f"✅ Successfully downloaded {media_count} media items!")
            await msg.delete()
        else:
            await msg.edit("😕 `No media could be downloaded!`")
    except Exception as e:
        await msg.edit(f"❌ **Error:**\n`{str(e)}`")
