# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def get_source_channels():  # Returns List
    return udB.get_key("CH_SOURCE") or []


def get_no_source_channels():  # Returns List
    channels = udB.get_key("CH_SOURCE") or []
    return len(channels)


def is_source_channel_added(id_):
    channels = get_source_channels()
    return id_ in channels


def add_source_channel(id_):  # Take int or str with numbers only , Returns Boolean
    channels = get_source_channels()
    if id_ not in channels:
        channels.append(id_)
        udB.set_key("CH_SOURCE", channels)
    return True


def rem_source_channel(id_):
    channels = get_source_channels()
    if id_ in channels:
        channels.remove(id_)
        udB.set_key("CH_SOURCE", channels)
    return True


#########################


def get_destinations():  # Returns List
    return udB.get_key("CH_DESTINATION") or []


def get_no_destinations():  # Returns List
    channels = udB.get_key("CH_DESTINATION") or []
    return len(channels)


def is_destination_added(id_):
    channels = get_destinations()
    return id_ in channels


def add_destination(id_):  # Take int or str with numbers only , Returns Boolean
    channels = get_destinations()
    if id_ not in channels:
        channels.append(id_)
        udB.set_key("CH_DESTINATION", channels)
    return True


def rem_destination(id_):
    channels = get_destinations()
    if id_ in channels:
        channels.remove(id_)
        udB.set_key("CH_DESTINATION", channels)
    return True
