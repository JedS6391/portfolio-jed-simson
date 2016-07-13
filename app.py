from flask import Flask

from portfolio.views import portfolio
from config import Config

import os


def create_app(config=None):
    app = Flask(__name__)

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
