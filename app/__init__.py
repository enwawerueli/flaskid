from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
mailer = Mail()


def create_app(env='default'):
    """App factory for dynamic initialization of an app with different configurations."""

    from app.config import config
    from app.views import blueprints
    from app.models import User, AnonymousUser

    app = Flask(__name__)
    app.config.from_object(config[env])
    config[env].configure(app)

    # set up extensions
    for ext in (db, login_manager, bootstrap, mailer):
        ext.init_app(app)

    # register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'
    login_manager.anonymous_user = AnonymousUser
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def get_user(uid):
        return User.query.get(int(uid))

    # error handlers
    @app.errorhandler(401)
    def unauthorised(error):
        return render_template('errors/401.html', error=error), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html', error=error), 500

    return app
