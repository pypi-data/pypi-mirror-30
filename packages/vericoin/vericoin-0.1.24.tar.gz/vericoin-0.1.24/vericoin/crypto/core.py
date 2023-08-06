from vericoin.base import *

class RestApi:
    def __init__(self):
        self.http = CryptoHttp()

    def histoday(self, **kwargs):
        """
        - See. https://www.cryptocompare.com/api/#-api-data-histoday- 
        """
        return self.http.get('/data/histoday', **kwargs)

    def histominute(self, **kwargs):
        """
        - See. https://www.cryptocompare.com/api/#-api-data-histominute- 
        """
        return self.http.get('/data/histominute', **kwargs)


class CryptoHttp(HttpMethod):
    def __init__(self):
        super(CryptoHttp, self).__init__()

    @property
    def base_url(self):
        return "https://min-api.cryptocompare.com"

