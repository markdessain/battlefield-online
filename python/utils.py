import datetime
import calendar


def dt2ts(dt):
    """Converts a datetime object to UTC timestamp
    naive datetime will be considered UTC.
    """
    return calendar.timegm(dt.utctimetuple())


def round_to_nearest_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)


def round_to_nearest_day(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)
