class Config(object):
    CHART_OF_ACCOUNTS_API = 'http://chart-of-accounts-api-test.dev.zooplus.net/v1'


class DevelopmentConfig(Config):
    CHART_OF_ACCOUNTS_API = 'http://chart-of-accounts-api-test.dev.zooplus.net/v1'


config = {
    "dev": DevelopmentConfig,

    "default": DevelopmentConfig
}
