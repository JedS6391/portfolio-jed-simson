import os

from flask import Flask
from flaskext.markdown import Markdown
from flask_compress import Compress
from flask_assets import Environment, Bundle

from markdown.extensions.meta import MetaExtension

import logging

from portfolio.views import portfolio
from blog import blog_manager
from util import format_date, format_value
from config import Config
from cache import cache

ONE_DAY = 60 * 60 * 24

def create_app(config=None):
    app = Flask(__name__)

    # Enable Markdown for better/simpler blog posts
    md = Markdown(app, extensions=['markdown.extensions.meta'])

    # Enable Flask-Compress for gzipping static files
    Compress(app)

    # Enable Flask-Assets to create bundles for assets
    assets = Environment(app)

    css = Bundle(
        'css/custom.css',
        'css/uikit.min.css',
        filters='cssmin',
        output='css/app.css'
    )

    assets.register('css_all', css)

    cache.init_app(app)

    # Use my custom blogging extension
    blog_manager.init_app(
        os.environ.get('POSTS_PATH', 'static/assets/posts/'),
        md._instance,
        app,
        ONE_DAY, # Invalidate cached posts after 1 day
    )

    if config:
        # There is a specified configuration
        app.config.from_object(config)
    else:
        app.config.from_object(os.environ.get('APP_SETTINGS', Config))

    # Custom filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_value'] = format_value
    app.jinja_env.globals['markdown_instance'] = md._instance

    app.register_blueprint(portfolio)

    logging.basicConfig(level=app.config['LOG_LEVEL'])

    app.logger.info('App configured')

    return app

if __name__ == '__main__':
    app = create_app()

    app.logger.info('App starting...')

    app.run(host='0.0.0.0', port=5050)
