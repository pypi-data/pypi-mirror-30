import requests


class HttpMethod:
    def __init__(self):
        self.session = requests.session()

    @property
    def base_url(self):
        return ""

    def _handle_response(self, response):
        """        
        requests에 대한 error handling
        """
        # statue code가 000이 아닐경우, requests.exceptions.HTTPError 발생
        # 이부분은 에러처리를 어떻게 할 것인지 논의를 더 해 봐야 함
        # response.raise_for_status()
        return response.json()

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def post(self, path, timeout=1, **kwargs):
        uri = self.base_url + path
        response = self.session.post(url=uri, data=kwargs, timeout=timeout)
        return self._handle_response(response)

    def get(self, path, timeout=1, **kwargs):
        uri = self.base_url + path
        response = self.session.get(url=uri, params=kwargs, timeout=timeout)
        return self._handle_response(response)

