from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from new_bot.core import constants

@dataclass
class FormattedTime:
    year: int
    month: int
    day: int
    hour: str
    minute: str
    second: str
    period: str

class Time:
    @classmethod
    def get_time(cls) -> FormattedTime:
        tzinfo = timezone(timedelta(hours=constants.TIME_ZONE))
        now = datetime.now(tzinfo)
        hour = now.hour

        return FormattedTime(
            year = now.year,
            month = now.month,
            day = now.day,
            hour = f"{hour:02d}",
            minute = f"{now.minute:02d}",
            second = f"{now.second:02d}",
            period = "上午" if hour < 12 else "下午"
        )

