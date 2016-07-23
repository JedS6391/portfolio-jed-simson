from flask import Flask
from flaskext.markdown import Markdown
from flask_compress import Compress
from flask_assets import Environment, Bundle

from portfolio.views import portfolio
from config import Config

import os


def create_app(config=None):
    app = Flask(__name__)

    # Enable Markdown for better/simpler blog posts
    Markdown(app)

    # Enable Flask-Compress for gzipping static files
    Compress(app)

    # Enable Flask-Assets to create bundles for assets
    assets = Environment(app)

    css = Bundle('css/bootstrap.min.css', 'css/custom.min.css',
                 filters='cssmin', output='css/app.css')
    assets.register('css_all', css)

    if config:
        # There is a specified configuration
        app.config.from_object(config)
    else:
        app.config.from_object(os.environ.get('APP_SETTINGS', Config))

    app.register_blueprint(portfolio)

    return app

if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', port=5050)
