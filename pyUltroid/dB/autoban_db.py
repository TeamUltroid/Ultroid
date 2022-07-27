from .. import udB


def get_all_channels() -> dict:
    """List all chats where channels are banned."""
    return udB.get_key("AUTOBAN_CHANNELS") or {}


def is_autoban_enabled(chat_id: int) -> bool:
    """Check whether channels are banned in a specific chat or not."""
    return chat_id in get_all_channels()


def add_channel(chat_id: int) -> bool:
    """Enable channel ban in a given chat."""
    if not is_autoban_enabled(int(chat_id)):
        channels = get_all_channels()
        channels[int(chat_id)] = []
        return udB.set_key("AUTOBAN_CHANNELS", channels)


def del_channel(chat_id: int) -> bool:
    """Disable channel ban in a given chat."""
    if is_autoban_enabled(chat_id):
        channels = get_all_channels()
        channels.pop(int(chat_id))
        return udB.set_key("AUTOBAN_CHANNELS", channels)


def get_whitelisted_channels(chat_id: int) -> list:
    """Get list of whitelisted channels in a given chat."""
    return get_all_channels()[chat_id] if is_autoban_enabled(chat_id) else []


def is_whitelisted(chat_id: int, channel_id: int) -> bool:
    """Check whether given channel is whitelisted in given chat or not."""
    return channel_id in get_whitelisted_channels(chat_id)


def add_to_whitelist(chat_id: int, channel_id: int) -> bool:
    """Add a channel in whitelist in a chat."""
    if is_autoban_enabled(chat_id):
        if not is_whitelisted(chat_id, channel_id):
            channels = get_all_channels()
            channels[int(chat_id)].append(int(channel_id))
            return udB.set_key("AUTOBAN_CHANNELS", channels)


def del_from_whitelist(chat_id: int, channel_id: int) -> bool:
    """Remove a channel from whitelist in a chat."""
    if is_autoban_enabled(chat_id):
        if is_whitelisted(chat_id, channel_id):
            channels = get_all_channels()
            channels[int(chat_id)].remove(int(channel_id))
            return udB.set_key("AUTOBAN_CHANNELS", channels)
