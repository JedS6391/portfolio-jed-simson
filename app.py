from flask import Flask
from flaskext.markdown import Markdown
from flask_compress import Compress
from flask_assets import Environment, Bundle
from flask_cachecontrol import FlaskCacheControl

from markdown.extensions.meta import MetaExtension

from portfolio.views import portfolio
from config import Config

import os


def format_date(value, format='%a, %d %b %Y'):
    return value.strftime(format)


def format_tags(tags):
    return ['#{}'.format(tag) for tag in tags[0].split(', ')]


def create_app(config=None):
    app = Flask(__name__)

    # Enable Markdown for better/simpler blog posts
    md = Markdown(app, extensions=['markdown.extensions.meta'])

    # Enable Flask-Compress for gzipping static files
    Compress(app)

    # Enable Flask-Assets to create bundles for assets
    assets = Environment(app)

    cache_control = FlaskCacheControl()
    cache_control.init_app(app)

    css = Bundle('css/bootstrap.min.css', 'css/custom.css',
                 filters='cssmin', output='css/app.css')
    assets.register('css_all', css)

    if config:
        # There is a specified configuration
        app.config.from_object(config)
    else:
        app.config.from_object(os.environ.get('APP_SETTINGS', Config))

    # Custom filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_tags'] = format_tags
    app.jinja_env.globals['markdown_instance'] = md._instance

    app.register_blueprint(portfolio)

    return app

if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', port=5050)
