import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_POSTS_PATH = 'static/assets/posts/'
DEFAULT_POSTS_PER_PAGE = 10

DEFAULT_CONTENT_SECURITY_POLICY = {
    'default-src': '\'self\' *.spotify.com *.google.com disqus.com *.disqus.com *.disquscdn.com',
    'style-src': '\'self\' fonts.googleapis.com',
    'font-src': '\'self\' fonts.gstatic.com',
    'script-src': '\'self\' *.google-analytics.com *.google.com/recaptcha/api.js *.disqus.com *.disquscdn.com'
}

class Config:
    ''' Represents the configuration required by the application. '''

    # General
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.environ['SECRET_KEY']

    # Blog
    POSTS_PATH = os.environ.get('POSTS_PATH', DEFAULT_POSTS_PATH)
    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE', DEFAULT_POSTS_PER_PAGE)

    # Email
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
    SENDGRID_DEFAULT_FROM = os.environ['SENDGRID_DEFAULT_FROM']
    CONTACT_EMAIL = os.environ['CONTACT_EMAIL']

    # ReCaptcha
    RECAPTCHA_PUBLIC_KEY = os.environ['RECAPTCHA_PUBLIC_KEY']
    RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']

    # Logging
    LOG_LEVEL = os.environ['LOG_LEVEL']

    # Monitoring 
    SENTRY_DSN = os.environ['SENTRY_DSN']

    # Security
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY', DEFAULT_CONTENT_SECURITY_POLICY)

class ProductionConfig(Config):
    ''' A configuration for use in production environments. ''' 
    pass

class DevelopmentConfig(Config):
    ''' A configuration for use in development environments. '''
    DEVELOPMENT = True
    DEBUG = True
