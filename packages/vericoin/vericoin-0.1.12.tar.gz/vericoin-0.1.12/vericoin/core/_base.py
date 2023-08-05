import requests

class HttpMethod:
    def __init__(self):
        raise AttributeError

    @staticmethod
    def get(func):
        def decorator(*args, **kwargs):
            param = func(*args, **kwargs)
            resp = requests.get(url=param.url, headers=param.headers, params=param.data)
            return resp.json()
        return decorator

    @staticmethod
    def post(func):
        def decorator(*args, **kwargs):
            param = func(*args, **kwargs)
            resp = requests.post(url=param.url, headers=param.headers, data=param.data)
            return resp.json()
        return decorator


class HttpParam:
    def __init__(self, url, headers=None, data=None):
        self.url = url
        self.headers = headers
        self.data = data