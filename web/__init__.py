from flask import Flask


def create():
    instance = Flask(__name__)
    instance.config['SECRET_KEY']= 'x'
    from .auth import auth

    instance.register_blueprint(auth, url_prefix='/')

    return instance
