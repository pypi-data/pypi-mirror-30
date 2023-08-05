import time
import datetime


def daystr_to_timestamp(daystr, offset=0):
    if daystr is None:
        timestamp = time.time()
    else:
        target = datetime.datetime.strptime(daystr, "%Y-%m-%d") + datetime.timedelta(days=offset)
        timestamp = time.mktime(target.timetuple())
    return int(timestamp)


def timestamp_to_daystr(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    timestamp = daystr_to_timestamp("2018-03-03", offset=1)
    print(timestamp)

    daystr = timestamp_to_daystr(timestamp)
    print(daystr)