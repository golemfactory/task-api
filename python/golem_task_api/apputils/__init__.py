import datetime


def datetime_utc():
    return datetime.datetime.now(tz=datetime.timezone.utc)
