import os
from typing import Any, List, Callable

from flask import Flask
from flaskext.markdown import Markdown
from flask_compress import Compress
from flask_assets import Environment, Bundle
from flask_talisman import Talisman

import logging

from portfolio.views import portfolio as portfolio_blueprint
from blog import blog_manager
from util import format_date, format_value
from config import Config

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
            step(self.app)

        self.app.logger.info('App configured')

        return self.app

    def configure_logging(self):
        logging.basicConfig(level=self.app.config['LOG_LEVEL'])

        self.app.logger.info('App logging configured')

def create_app(config=None):
    app = Flask(__name__)
    portfolio = PortfolioBuilder(app, [
        configure_markdown_and_blog,
        configure_compression_and_asset_bundling,
        configure_security,
        configure_blueprints
    ])

    if config is None:
        config = os.environ.get('APP_SETTINGS', Config)

    app = portfolio.configure(config)

    return app

def configure_markdown_and_blog(app: Flask) -> Flask:
    app.logger.debug('Configuring markdown support...')

    # Enable Markdown for better/simpler blog posts
    md = Markdown(app, extensions=['markdown.extensions.meta'])

    app.logger.debug('Configuring blog manager')

    # Configure the blog
    if 'blog' not in app.extensions:
        app.extensions['blog'] = {}

    app.extensions['blog'] = blog_manager

    blog_manager.initialise(
        path=os.environ.get('POSTS_PATH', 'static/assets/posts/'),
        parser=md._instance,    
        max_cache_age=ONE_DAY
    )

    # Custom Jinja filters for the blog
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_value'] = format_value
    app.jinja_env.globals['markdown_instance'] = md._instance

    return app

def configure_compression_and_asset_bundling(app: Flask) -> Flask:
    app.logger.debug('Configuring compression for static files...')

    # Enable Flask-Compress for gzipping static files
    Compress(app)

    app.logger.debug('Configuring asset bundling...')

    # Enable Flask-Assets to create bundles for assets
    assets = Environment(app)

    css = Bundle(
        'css/custom.css',
        'css/uikit.min.css',
        'css/tomorrow.min.css',
        filters='cssmin',
        output='css/app.css'
    )

    assets.register('css_all', css)

    return app

def configure_security(app: Flask) -> Flask:
    app.logger.debug('Configuring security features')

    # Enable Flask-Talisman to automatically set HTTP headers for web app security issues
    Talisman(
        app, 
        content_security_policy=app.config['CONTENT_SECURITY_POLICY'],
        content_security_policy_nonce_in=['script-src'])

    return app

def configure_blueprints(app: Flask) -> Flask:
    app.register_blueprint(portfolio_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()

    app.logger.info('App starting...')

    app.run(host='0.0.0.0', port=5050)
