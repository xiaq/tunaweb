class ProductionConfig(object):
    DEBUG = False
    TESTING = False
    host = '127.0.0.1'
    port = 5050

DefaultConfig = ProductionConfig


class DevelopmentConfig(object):
    DEBUG = True
    TESTING = False
    host = '127.0.0.1'
    port = 5000


class StagingConfig(object):
    DEBUG = False
    TESTING = False
    host = '127.0.0.1'
    port = 5000
