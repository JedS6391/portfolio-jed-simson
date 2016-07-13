import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    DEVELOPMENT = False

    # Set a secure secret key as an environment
    # variable
    SECRET_KEY = os.environ['SECRET_KEY']


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
