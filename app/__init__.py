from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail

from config import config


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
mailer = Mail()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(env):
    """ app factory to facilitate dynamic initialization of an app
    for different configurations
    """
    app = Flask(__name__)
    app.config.from_object(config[env])
    config[env].configure(app)
    for ext in (db, login_manager, bootstrap, mailer):
        ext.init_app(app)
    return app
