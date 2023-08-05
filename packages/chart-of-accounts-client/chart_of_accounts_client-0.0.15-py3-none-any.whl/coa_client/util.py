import requests


def get_charts():
    return requests.get('http://chart-of-accounts-api-test.dev.zooplus.net/v1/charts').json()

