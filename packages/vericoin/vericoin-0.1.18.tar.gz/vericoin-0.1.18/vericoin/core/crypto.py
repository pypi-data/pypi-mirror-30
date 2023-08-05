from vericoin.core._base import *
from vericoin._util import *


class CryptoDaily:
    @staticmethod
    def get_ohlcv(since=None, limit=10, market="KRW", exchange="Korbit", coin="BTC"):
        """
        거래소 (exchange)에서 day부터 limit 개수의 coin OHLCV를 가져온다.          
        - See. https://www.cryptocompare.com/api/#-api-data-histoday-
        :param since: 조사할 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param limit: 조회할 데이터의 수 
        :param market: 결제 화폐
        :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex  
        :param coin: 코인 이름 약어
        :return: Dictionary 형태의 OHLCV 데이터
                 예) https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=KRW&limit=10&e=Korbit
        """
        if since is None:
            timestamp = time.time()
        else:
            # 서버는 request 일자로부터 limit 개수의 이전 OHLCV를 반환하기 때문에
            # 사용자로부터 입력받은 Target 날짜와 offset을 서버 Format으로 변경한다.
            dt_to = str2dt(since) + datetime.timedelta(days=limit)
            today = datetime.datetime.now()
            # 잘못된 range를 입력할 경우, 값을 수정한다.
            # 예: 오늘이 03-25일인데 03-24일 부터 10개의 데이터를 요청할 경우, limit 값을 2로 변경
            if dt_to > today:
                limit = limit - (dt_to - today).days
                dt_to = today
            timestamp = dt2ts(dt_to)

        resp = _CryptoEngine.histoday(timestamp, limit, market, exchange, coin)
        if resp['Response'] != 'Success':
            return []
        else:
            # [-limit:] is used for API minor bug
            # - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            return resp['Data'][-limit:]

    @staticmethod
    def get_price(market="KRW", exchange="Korbit", coin="BTC"):
        """
        거래소 (exchange)에서 최근 거래된 coin 가격을 가져온다.                  
        - See. https://www.cryptocompare.com/api/#-api-data-price-
        :param day: 조사할 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03
        :param market: 결제 화폐
        :param exchange: 거래소 이름 예) Bithumb, Korbit, Bitfnex: 
        :param coin: 코인 이름 약어
        :return: 코인의 종가 가격
        """
        resp = _CryptoEngine.price(market, exchange, coin)
        return resp[market]

class _CryptoEngine:
    """
    API 홈페이지 (https://min-api.cryptocompare.com/)에 정의된 데이터 구조 정의
    """
    @staticmethod
    @HttpMethod.get
    def histoday(timestamp, limit, market, exchange, coin):
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
    def price(market, exchange, coin):
        url = "https://min-api.cryptocompare.com/data/price"
        data = {
            "fsym": coin,
            "tsyms": market,
            "e": exchange
        }
        return HttpParam(url=url, data=data)

