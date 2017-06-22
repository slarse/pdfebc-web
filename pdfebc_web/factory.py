# -*- coding: utf-8 -*-
"""Factory module for pdfebc-web.

.. module:: factory
    :platform: Unix
    :synopsis: Factory functions for pdfebc-web.
.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
from flask import Flask
from flask_bootstrap import Bootstrap
from .main import main as main_blueprint

bootstrap = Bootstrap()

def create_app():
    """Instantiate the pdfebc-web app.

    Returns:
        Flask: A Flask application.
    """
    app = Flask(__name__)
    bootstrap.init_app(app)
    # TODO Make the secret key an actual secret key
    app.config['SECRET_KEY'] = 'dev_key'
    app.register_blueprint(main_blueprint)
    return app
