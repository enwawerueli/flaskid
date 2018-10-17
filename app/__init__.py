from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from config import config


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(env):
    """ app factory allows dynamic initialization of an app instance
    with different configurations
    """
    app = Flask(__name__)
    app.config.from_object(config[env])
    config[env].configure(app)
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    return app
