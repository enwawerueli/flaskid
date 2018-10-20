from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from . import auth_blueprint
from ..models import db, User
from ..forms import LoginForm, RegistrationForm
from ..utils import send_mail


@auth_blueprint.route('/login', methods=['get', 'post'])
def login():
    lf = LoginForm()
    if lf.validate_on_submit():
        user = User.query.filter(db.or_(User.name == lf.username.data, User.email == lf.username.data)).one()
        if user is not None and user.verify_password(lf.password.data):
            if login_user(user, lf.remember_me.data):
                flash('Login successful.')
                return redirect(request.args.get('next') or url_for('main.index'))
            elif not user.is_active:
                login_user(user, lf.remember_me.data, force=True)
                return redirect(url_for('auth.inactive'))
        flash('Wrong username or password')
    return render_template('login.html', form=lf)


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/register', methods=['get', 'post'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit():
        user = User(name=rf.username.data, email=rf.email.data, password=rf.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        send_mail(to=user.email, subject='Account activation', template='mail/welcome', user=user, token=token)
        login_user(user, force=True)
        flash('An activation link has been sent to your email. The link will expire after 1 hour.')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=rf)


@auth_blueprint.route('/accounts/activate/<token>')
@login_required
def activate(token):
    if not current_user.is_active:
        if current_user.verify_token(token):
            flash('You have activated your account. Thank you!')
        else:
            flash('The activation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/accounts/inactive')
@login_required
def inactive():
    if current_user.is_anonymous or current_user.is_active:
        return redirect(url_for('main.index'))
    return render_template('inactive.html')


@auth_blueprint.route('/accounts/activate')
@login_required
def resend_activation_link():
    token = current_user.generate_token()
    send_mail(to=current_user.email, subject='Account activation', template='mail/welcome', user=current_user,
              token=token)
    flash('A new activation link has been sent to your email. The link will expire after 1 hour.')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/users/<int:user_id>')
@login_required
def show(user_id):
    pass


@auth_blueprint.before_app_request
def before_request():
    if (current_user.is_authenticated and
            not current_user.is_active and
            request.endpoint[:5] != 'auth.' and
            request.endpoint != 'bootstrap.static'):  # allow serving static files
        return redirect(url_for('auth.inactive'))
