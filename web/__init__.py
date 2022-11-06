from flask import Flask
import cx_Oracle


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']= 'alcs'
    from .auth import auth

    app.register_blueprint(auth, url_prefix='/')

    return app