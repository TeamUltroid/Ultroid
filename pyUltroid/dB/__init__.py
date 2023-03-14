from .. import run_as_module

if not run_as_module:
    from ..exceptions import RunningAsFunctionLibError

    raise RunningAsFunctionLibError(
        "You are running 'pyUltroid' as a functions lib, not as run module. You can't access this folder.."
    )

from .. import *

DEVLIST = [
    719195224,  # @xditya
    1322549723,  # @danish_00
    1903729401,  # @its_buddhhu
    1303895686,  # @Sipak_OP
    611816596,  # @Arnab431
    1318486004,  # @sppidy
    803243487,  # @hellboi_atul
    1620434318,  # @kalijogo
    5615921474,  # @itachipremium
]

ULTROID_IMAGES = [
    f"https://graph.org/file/{_}.jpg"
    for _ in [
        "ec250c66268b62ee4ade6",
        "3c25230ae30d246194eba",
        "b01715a61b9e876c0d45d",
        "4ceaf720a96a24527ecff",
        "a96223b574f29f3f0d184",
        "6e081d339a01cc6190393",
    ]
]

stickers = [
]
