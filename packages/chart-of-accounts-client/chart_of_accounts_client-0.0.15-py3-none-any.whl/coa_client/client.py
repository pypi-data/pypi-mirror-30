from cacheout import Cache
import requests
from .config import config


class Client(object):

    def __init__(self, cache_timeout=86400, request_timeout=1):
        self.cache = Cache(ttl=cache_timeout)
        self.request_timeout = request_timeout

    def get_accounting_chart(self, organization=None):
        charts = self.cache.get('charts')
        if charts is None:
            url = config.CHART_OF_ACCOUNTS_API + '/charts'
            if organization:
                url = url + '/' + organization
            charts = requests.get(url, timeout=self.request_timeout).json()
            # TODO: Call Account library here to transform dict into tree and save it in cache below
            self.cache.set('charts', charts)
        return charts

