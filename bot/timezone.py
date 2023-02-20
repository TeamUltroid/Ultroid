import os
import time

from core import LOGS
from pytz import timezone


def set_timezone(TZ):
    try:
        timezone(TZ)
        os.environ["TZ"] = TZ
        # Unix Only
        time.tzset()
    except AttributeError as er:
        LOGS.error(er)
    except BaseException as er:
        LOGS.critical(
            f"{er.__class__.__name__}: Incorrect Timezone ,\nCheck Available Timezone From Here https://graph.org/Ultroid-06-18-2\nSo Time is Default UTC"
        )
        os.environ["TZ"] = "UTC"
        time.tzset()
