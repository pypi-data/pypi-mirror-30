import pandas as pd
from ratelimit import *
from vericoin._util import *
from vericoin.core.crypto import CryptoDaily


@rate_limited(1)
def get_ohlcv(since=None, limit=10, market="KRW", exchange="Korbit", coin="BTC"):
    """
        거래소 (exchange)에서 day부터 limit 개수의 coin OHLCV를 가져온다.          
        - See. https://www.cryptocompare.com/api/#-api-data-histoday-
        :param since: 조사할 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03 
        :param limit: 조회할 데이터의 수
        :param market: 결제 화폐
        :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex  
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, vlume) 리스트
        """
    response = CryptoDaily.get_ohlcv(since, limit, market, exchange, coin)

    # dictionary to dataframe
    df = pd.DataFrame.from_records(response).loc[:, :'volumefrom'].rename(columns = {'volumefrom':'volume'})
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    df['time'] = df.time.apply(ts2str)
    return df


@rate_limited(1)
def get_price(market="KRW", exchange="Korbit", coin="BTC"):
    """
    거래소 (exchange)에서 최근 거래된 coin 가격을 가져온다.                  
    - See. https://www.cryptocompare.com/api/#-api-data-price-    
    :param market: 결제 화폐
    :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex: 
    :param coin: 코인 이름 약어
    :return: 코인의 종가 가격
    """
    return CryptoDaily.get_price(market, exchange, coin)


if __name__ == "__main__":
    # resp = get_price(market="KRW", exchange="Bithumb")
    # print(resp)
    #
    # resp = get_price(market="KRW", exchange="Korbit")
    # print(resp)
    #
    # resp = get_price(market="USD", exchange="Bitfinex")
    # print(resp)

    resp = get_ohlcv(coin="BTC", since="2018-03-23", limit=10)
    print(resp)
