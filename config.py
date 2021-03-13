import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_CONTENT_SECURITY_POLICY = {
    'default-src': '\'self\' *.spotify.com *.google.com disqus.com *.disqus.com *.disquscdn.com',
    'style-src': '\'self\' fonts.googleapis.com',
    'font-src': '\'self\' fonts.gstatic.com',
    'script-src': '\'self\' *.google-analytics.com *.google.com/recaptcha/api.js *.disqus.com *.disquscdn.com'
}

class Config(object):
    DEBUG = False
    DEVELOPMENT = False

    # Set a secure secret key as an environment variable
    SECRET_KEY = os.environ['SECRET_KEY']

    # ReCaptcha settings
    RECAPTCHA_PUBLIC_KEY = os.environ['RECAPTCHA_PUBLIC_KEY']
    RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']

    # Logging
    LOG_LEVEL = os.environ['LOG_LEVEL']

    # Security
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY', DEFAULT_CONTENT_SECURITY_POLICY)


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
