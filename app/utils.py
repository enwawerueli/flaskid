import os

from functools import wraps
from threading import Thread

from flask import abort, render_template, current_app
from flask_login import current_user
from flask_mail import Message
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature

from . import create_app, mailer
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTRATE)(f)


def send_mail(to, subject, template, **kwargs):
    msg = Message(subject=current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  body=render_template(template + '.txt', **kwargs),
                  html=render_template(template + '.html', **kwargs),
                  recipients=[to])
    thread = Thread(target=send_mail_async, args=[msg])
    thread.start()


def send_mail_async(msg):
    app = create_app(os.environ.get('SKY_ENV') or 'default')
    with app.app_context():
        mailer.send(msg)


def generate_token(data, role=None, expiration=3600):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps(data, salt=role)


def verify_token(token, role=None):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt=role)
    except BadSignature:
        return None
