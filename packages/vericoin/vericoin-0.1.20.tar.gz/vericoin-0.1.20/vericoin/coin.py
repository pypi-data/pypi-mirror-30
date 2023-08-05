from ratelimit import *
from vericoin.core.crypto import CryptoDaily


@rate_limited(1)
def get_ohlcv(since, until=None, coin="BTC"):
    """
    since부터 until까지의 coin OHLCV를 가져온다.              
    :param since: 조회 시작 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
    :param until: 조사 끝  날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03      
    :param coin: 코인 이름 약어
    :return: [(날짜, open, high, low, close, volume)] dataframe, 가격은 USD             
    """
    return CryptoDaily.get_ohlcv(since, until, coin)


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
    resp = get_ohlcv(since='2017-01-01', until='2018-03-24')