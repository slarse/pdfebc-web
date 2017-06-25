"""Module for starting up the pdfebc-web application.

.. module:: startapp
    :platform: Linux
    :synopsis: Single-script module for starting pdfebc-web.
.. moduleauthor: Simon Larsén <slarse@kth.se>
"""
from .factory import create_app

celery, app = create_app()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80)
