import requests
from configparser import ConfigParser

class CourtSession:
    def __init__(self, headers, timeout):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.timeout = timeout

    def get(self, url, params=None):
        return self.session.get(url, params=params, timeout=self.timeout)

    def post(self, url, data):
        return self.session.post(url, data=data, timeout=self.timeout)

