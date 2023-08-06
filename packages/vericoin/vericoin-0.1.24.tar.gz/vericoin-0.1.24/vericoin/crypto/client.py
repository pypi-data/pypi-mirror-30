from ratelimit import *
from vericoin.util import *
from vericoin.crypto.core import *
import pandas as pd


class Crypto:

    def __init__(self):
        self.api = RestApi()

    @rate_limited(1)
    def get_ohlcv_min(self, target, count=1, market="KRW", coin="BTC", exchange="Korbit"):
        """
        target날짜부터 이전 time의 coin OHLCV를 가져온다.              
        :param target: 조회 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param count: 조사 개수          
        :param market: 시장
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, volume) dataframe       
        """
        if count > 2000:
            print("'count' should be less than or equal to 2000.")
            print("'count' is automatically set to 2000.")
            count = 2000

        resp = self.api.histominute(toTs=dt2ts(str2dt(target)), fsym=coin, tsym=market, limit=count - 1, e=exchange)
        if resp['Response'] != 'Success':
            return resp['Message']
        else:
            # [-limit:] is used for API minor bug
            #   - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            # dictionary to dataframe
            df = pd.DataFrame.from_records(resp['Data'][-count:]).loc[:, :'volumefrom'].rename(columns={'volumefrom': 'volume'})
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = df.time.apply(ts2str)
            return df

    @rate_limited(1)
    def get_ohlcv_day(self, target, count=1, market="KRW", coin="BTC", exchange="Korbit"):
        """
        target날짜부터 이전 time의 coin OHLCV를 가져온다.              
        :param target: 조회 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param count: 조사 개수       
        :param market: 시장
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, volume) dataframe       
        """
        toTs = dt2ts(str2dt(target) + datetime.timedelta(hours=9))
        resp = self.api.histoday(toTs=toTs, fsym=coin, tsym=market, limit=count - 1, e=exchange)
        if resp['Response'] != 'Success':
            return resp['Message']
        else:
            # [-limit:] is used for API minor bug
            #   - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            # dictionary to dataframe
            df = pd.DataFrame.from_records(resp['Data'][-count:]).loc[:, :'volumefrom'].rename(
                columns={'volumefrom': 'volume'})
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = df.time.apply(ts2str)
            return df

if __name__ == "__main__":
    c = Crypto()
    # resp = c.get_ohlcv_min(target="2018-04-09 23:00:00", count=10, market="USDT", exchange='Binance')
    # print(resp)

    days = c.get_ohlcv_day(target='2018-01-01', count=3)
    print(days)