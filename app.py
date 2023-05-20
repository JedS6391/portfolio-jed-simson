from typing import Any, List, Callable

from datetime import datetime, timezone

import logging
import os

from flask import Flask, send_from_directory
from flask_assets import Environment, Bundle
from flask_compress import Compress
from flask_talisman import Talisman
from flaskext.markdown import Markdown

import sentry_sdk as sentry
from sentry_sdk.integrations.flask import FlaskIntegration as SentryFlaskIntegration

from config import Config
from util import format_date, format_value

from portfolio.views import portfolio as portfolio_blueprint
from portfolio.blog import blog_manager
from portfolio.project_feed import project_feed_manager
from portfolio.mail import email_manager

ONE_DAY = 60 * 60 * 24

# Represents the pipeline for configuring the portfolio app.
PortfolioConfigurationStep = Callable[[Flask], Flask]
PortfolioConfigurationPipeline = List[PortfolioConfigurationStep]

class PortfolioBuilder:
    ''' Responsible for building the portfolio app. '''

    def __init__(self, app: Flask, configuration_pipeline: PortfolioConfigurationPipeline):
        self.app = app
        self.configuration_pipeline = configuration_pipeline

    def configure(self, configuration: Any) -> Flask:
        ''' Configures the app and runs the steps specified in the configuration pipeline. '''

        self.app.config.from_object(configuration)

        self.configure_logging()

        self.app.logger.info('Configuring app')

        for step in self.configuration_pipeline:
            self.app = step(self.app)

        self.app.logger.info('App configured')

        return self.app

    def configure_logging(self):
        logging.basicConfig(level=self.app.config['LOG_LEVEL'])

        self.app.logger.info('App logging configured')

def create_app(config=None) -> Flask:
    ''' Creates a ``Flask`` app instance that represents the portfolio.

        The instance returned will be configured using ``config`` or if not available
        will read which configuration to use from the ``APP_SETTINGS` environment variable.
    '''
    app = Flask(__name__)
    portfolio = PortfolioBuilder(app, [
        configure_markdown_and_blog,
        configure_project_feed,
        configure_mailer,
        configure_compression_and_asset_bundling,
        configure_security,
        configure_monitoring,
        configure_blueprints
    ])

    if config is None:
        config = os.environ.get('APP_SETTINGS', Config)

    app = portfolio.configure(config)

    return app

def configure_markdown_and_blog(app: Flask) -> Flask:
    app.logger.debug('Configuring markdown support...')

    # Enable Markdown for better/simpler blog posts
    md = Markdown(app, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.meta'])

    app.logger.debug('Configuring blog manager...')

    # Configure the blog
    if 'blog' not in app.extensions:
        app.extensions['blog'] = {}

    app.extensions['blog'] = blog_manager

    blog_manager.initialise(
        path=app.config['POSTS_PATH'],
        parser=md._instance,    
        max_cache_age=ONE_DAY
    )

    # Custom Jinja filters for the blog
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_value'] = format_value
    app.jinja_env.globals['markdown_instance'] = md._instance

    return app

def configure_project_feed(app: Flask) -> Flask:
    app.logger.debug('Configuring project feed...')

    project_feed_manager.initialise(
        path=app.config['PROJECT_FEED_PATH']
    )

    return app
 
def configure_mailer(app: Flask) -> Flask:
    email_manager.initialise(
        api_key=app.config['SENDGRID_API_KEY'],
        default_from= app.config['SENDGRID_DEFAULT_FROM']
    )

    return app
 
def configure_compression_and_asset_bundling(app: Flask) -> Flask:
    app.logger.debug('Configuring compression for static files...')

    # Enable Flask-Compress for gzipping static files
    Compress(app)

    app.logger.debug('Configuring asset bundling...')

    # Enable Flask-Assets to create bundles for assets
    assets = Environment(app)

    css = Bundle(
        # Styling overrides for the portfolio application
        'css/custom.css',
        # Halfmoon UI framework: https://www.gethalfmoon.com/
        'css/halfmoon-ui.css',
        # Dracula code highlighting theme
        'css/dracula-code-highlight.css',        
        filters='cssmin',
        output='css/app.css'
    )

    js = Bundle(
        # Logic for the portfolio application 
        'js/custom.js',
        # Halfmoon UI framework: https://www.gethalfmoon.com/
        'js/halfmoon.min.js', 
        # Code highlighting: https://highlightjs.org/
        'js/highlight.min.js',   
        # Feather icons: https://feathericons.com/
        'js/feather.min.js',
        filters='jsmin',
        output='js/app.js'
    )
    
    assets.register('css_all', css)
    assets.register('js_all', js)

    return app

def configure_monitoring(app: Flask) -> Flask:
    app.logger.debug('Configuring app monitoring...')

    sentry.init(
        dsn=app.config['SENTRY_DSN'],
        integrations=[SentryFlaskIntegration()]
    )

    # Set up routes used for health checks
    def ping():
        return 'Pong @ {}'.format(datetime.now(timezone.utc))

    app.add_url_rule(
        rule='/ping',
        view_func=ping
    )

    return app

def configure_security(app: Flask) -> Flask:
    app.logger.debug('Configuring security features...')

    # Enable Flask-Talisman to automatically set HTTP headers for web app security issues
    Talisman(
        app, 
        content_security_policy=app.config['CONTENT_SECURITY_POLICY'],
        content_security_policy_nonce_in=['script-src'])

    app.logger.debug('Configuring ACME challenge routes...')

    def acme_challenge_portfolio() -> str:
        return 'mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU'

    def acme_challenge_www() -> str:
        return 'aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0.K2tT6yEn2xKfamcfv_y2hTXLbRbp3qeaqp6AC0yItFE'

    # Set routes for ACME challenges needed for Let's Encrypt verification
    app.add_url_rule(
        rule='/.well-known/acme-challenge/mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU',
        view_func=acme_challenge_portfolio
    )

    app.add_url_rule(
        rule='/.well-known/acme-challenge/aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0',
        view_func=acme_challenge_www
    )

    app.logger.debug('Configuring Keybase verification routes...')

    # Set up routes to support Keybase verification
    def keybase():
        return send_from_directory('static/', 'keybase.txt')

    app.add_url_rule(
        rule='/keybase.txt',
        view_func=keybase
    )

    return app

def configure_blueprints(app: Flask) -> Flask:
    app.register_blueprint(portfolio_blueprint)

    return app
