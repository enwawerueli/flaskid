from flask import Blueprint

main_blueprint = Blueprint('main', __name__)
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
posts_blueprint = Blueprint('posts', __name__, url_prefix='/posts')

from . import auth
from . import posts
from . import template_utils


blueprints = [main_blueprint, auth_blueprint, posts_blueprint]
