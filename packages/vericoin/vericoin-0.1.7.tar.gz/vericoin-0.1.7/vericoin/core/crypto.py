from ._base import *


class CryptoDaily:
    @staticmethod
    @HttpMethod.get
    def get_price_list(timestamp, limit, market, exchange, coin):
        """
        거래소 (exchange)에서 day부터 limit 개수의 coin OHLCV를 가져온다.          
        - See. https://www.cryptocompare.com/api/#-api-data-histoday-
        :param timestamp: 조사할 날짜의 timestamp
        :param limit: 조회할 데이터의 수 
        :param market: 결제 화폐
        :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex  
        :param coin: 코인 이름 약어
        :return: Dictionary 형태의 OHLCV 데이터
                 예) https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=KRW&limit=10&e=Korbit
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
    def get_price(market, exchange, coin):
        """
        거래소 (exchange)에서 최근 거래된 coin 가격을 가져온다.                  
        - See. https://www.cryptocompare.com/api/#-api-data-price-
        :param day: 조사할 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03
        :param market: 결제 화폐
        :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex: 
        :param coin: 코인 이름 약어
        :return: 코인의 종가 가격
        """
        url = "https://min-api.cryptocompare.com/data/price"
        data = {
            "fsym": coin,
            "tsyms": market,
            "e": exchange
        }
        return HttpParam(url=url, data=data)
