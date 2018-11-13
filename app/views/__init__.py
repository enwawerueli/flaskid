from flask import Blueprint, request, redirect, url_for
from flask_login import current_user

main_blueprint = Blueprint('main', __name__)
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
posts_blueprint = Blueprint('posts', __name__, url_prefix='/posts')

from . import auth
from . import posts
from . import helpers


@main_blueprint.before_app_request
def before_request():
    if (current_user.is_authenticated and
            not current_user.is_active and
            request.endpoint[:5] != 'auth.' and
            request.endpoint != 'bootstrap.static'):  # allow serving static files
        return redirect(url_for('auth.inactive'))


blueprints = [main_blueprint, auth_blueprint, posts_blueprint]
