from vericoin.core._base import *
from vericoin._util import *
import pandas as pd

class CryptoDaily:
    @staticmethod
    def get_coins(self):
        pass

    @staticmethod
    def get_ohlcv(since, until=None, coin="BTC"):
        """
        since부터 until까지의 coin OHLCV를 가져온다.              
        :param since: 조회 시작 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param until: 조사 끝  날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03          
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, volume) dataframe, 가격은 USD       
        """

        # Crypto 서버의 Daily 정보는 과거 부터 하루 전 데이터를 제공한다.
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if until is None:
            dt_to = yesterday
        else:
            dt_to = min(str2dt(until), yesterday)
        dt_from = min(str2dt(since), yesterday)

        # Crypto 서버가 요구하는 데이터 포맷으로 변경
        stamp = dt2ts(dt_to)
        limit = (dt_to - dt_from).days + 1

        resp = _CryptoEngine.histoday(timestamp=stamp, limit=limit, coin=coin)
        if resp['Response'] != 'Success':
            return None
        else:
            # [-limit:] is used for API minor bug
            #   - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            # dictionary to dataframe
            df = pd.DataFrame.from_records(resp['Data'][-limit:]).loc[:, :'volumefrom'].rename(columns={'volumefrom': 'volume'})
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = df.time.apply(ts2str)
            return df

    @staticmethod
    def get_price(coin="BTC"):
        """
        거래소 (exchange)에서 최근 거래된 coin 가격을 가져온다.                          
        :param day: 조사할 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03         
        :param coin: 코인 이름 약어
        :return: 코인의 종가 USD 가격
        """
        resp = _CryptoEngine.price(coin=coin)
        return resp["USD"]


class _CryptoEngine:
    """
    API 홈페이지 (https://min-api.cryptocompare.com/)에 정의된 데이터 구조 정의
    """
    @staticmethod
    @HttpMethod.get
    def histoday(timestamp, limit, market="USD", exchange="CCCAGG", coin="BTC"):
        """
        - See. https://www.cryptocompare.com/api/#-api-data-histoday- 
        """
        url = "https://min-api.cryptocompare.com/data/histoday"
        data = {
            "fsym": coin,
            "tsym": market,
            "limit": limit - 1,
            "e": exchange,
            "toTs": timestamp
        }
        return HttpParam(url=url, data=data)

    @staticmethod
    @HttpMethod.get
    def price(market="USD", exchange="CCCAGG", coin="BTC"):
        """
        - See. https://www.cryptocompare.com/api/#-api-data-price- 
        """
        url = "https://min-api.cryptocompare.com/data/price"
        data = {
            "fsym": coin,
            "tsyms": market,
            "e": exchange
        }
        return HttpParam(url=url, data=data)


if __name__ == "__main__":
    resp = CryptoDaily.get_ohlcv(since="2018-03-23")
    print(resp)

    print(CryptoDaily.get_price())