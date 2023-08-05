import time
import datetime


def str2dt(daystr):
    """
    string을 datetime 객체로 변환한다.
    :param daystr: "년-월-일" 형태의 문자열
    :return: datetime
    """
    return datetime.datetime.strptime(daystr, "%Y-%m-%d")


def dt2ts(dt):
    """
    datetime 객체를 timestamp 값으로 변환한다.
    :param dt: datetime 객체
    :return: timestamp
    """
    return int(time.mktime(dt.timetuple()))


def ts2str(timestamp):
    """
    timestamp 값을 문자열로 변환한다.
    :param timestamp: timestamp
    :return: string
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    dt = str2dt("2018-03-24")
    ts = dt2ts(dt)
    st = ts2str(ts)
    print(st)




