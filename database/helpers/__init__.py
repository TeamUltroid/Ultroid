from random import choice

from database import udB

from .base import KeyManager

DEVLIST = [
    719195224,  # @xditya
    1322549723,  # @danish_00
    1903729401,  # @its_buddhhu
    1303895686,  # @Sipak_OP
    611816596,  # @Arnab431
]


def get_random_color():
    return choice(
        [
            "DarkCyan",
            "DeepSkyBlue",
            "DarkTurquoise",
            "Cyan",
            "LightSkyBlue",
            "Turquoise",
            "MediumVioletRed",
            "Aquamarine",
            "Lightcyan",
            "Azure",
            "Moccasin",
            "PowderBlue",
        ]
    )
