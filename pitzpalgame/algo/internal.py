from datetime import datetime, timedelta, timezone
from enum import Enum


class State(Enum):
    MOVE_UNKNOWN = 0
    MOVE_VALIDATION = 1
    MOVE_START = 2
    MOVE_PROGRESS = 3
    MOVE_CAPTURE = 4
    MOVE_END = 5
    MOVE_ERROR = 6
    MOVE_ROUNDUP = 7
    MOVE_GAMEOVER = 8


def is_time_expire(timestamp_str, expire_sec):
    # 1. Parse the string back into a datetime object
    # %Y-%m-%dT%H:%M:%SZ matches your specific format
    past_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

    # 2. Ensure it is UTC-aware to match the current time comparison
    past_time = past_time.replace(tzinfo=timezone.utc)

    # 3. Get the current time in UTC
    now = datetime.now(timezone.utc)

    # 4. Calculate the difference
    difference = now - past_time

    # 5. Check if difference is greater than
    return difference > timedelta(seconds=expire_sec)
