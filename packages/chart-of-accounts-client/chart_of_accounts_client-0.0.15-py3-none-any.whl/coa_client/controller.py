import requests

from .config import config
from functools import lru_cache


# def booking_accounts():
#     print('here in booking_accounts')
#     chart_dict = get_charts()
#     accounts = NodeGroup(name='booking')
#     for organization, chart in chart_dict.items():
#         accounts.add_node(AccountChart.build_chart(organization, chart))
#     return accounts

class COAClient(object):

    def __init__(self, env='default'):
        self.env = env
        self.config = config[env]

    def get_accounting_chart(self, organization=None):
        return requests.get(self.config.CHART_OF_ACCOUNTS_API + '/charts').json()

    def filter_accounts(self, organization, path):
        return requests.get(self.config.CHART_OF_ACCOUNTS_API + '/charts/' + organization + '/' + path).json()

    def get_account_details(self, organization, code):
        return requests.get(self.config.CHART_OF_ACCOUNTS_API + '/accounts/' + organization + '/' + code).json()
