"""
Utilities for handling dates and times
"""

from datetime import timedelta


def pluralstr(num: int) -> str:
    """
    Returns '' if num is one, otherwise returns 's'

    :param num: The number to generate a pluralizing string for
    :type num: int
    """

    return "" if num == 1 else "s"


def fmtdelta(delta: timedelta) -> str:
    """
    Given a  time delta, format it in the most general/significant unit

    For example, 9 days and 3 hours would return "9 days", while 0 days, 0
    hours, 36 minutes, and 12 seconds would return "36 minutes".

    :param delta: the timedelta to format as a string
    :type delta: datetime.timedelta
    """

    if delta.days > 0:
        return f"{delta.days} day{pluralstr(delta.days)}"
    elif delta.seconds > 60 * 60:  # Number of seconds per hour
        hours = delta.seconds // (60 * 60)
        return f"{hours} hour{pluralstr(hours)}"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{pluralstr(minutes)}"
    elif delta.seconds > 0:
        seconds = delta.seconds
        return f"{seconds} second{pluralstr(seconds)}"
    else:
        microseconds = delta.microseconds
        return f"{microseconds} microsecond{pluralstr(microseconds)}"
