from . import views

def construct_blueprint(celery):
    return views.construct_blueprint(celery)
