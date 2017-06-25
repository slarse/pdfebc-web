# -*- coding: utf-8 -*-
"""Factory module for pdfebc-web.

.. module:: factory
    :platform: Unix
    :synopsis: Factory functions for pdfebc-web.
.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from .main import construct_blueprint

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
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    main_blueprint = construct_blueprint(celery)
    app.register_blueprint(main_blueprint)

    return celery, app
