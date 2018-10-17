from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user

from . import auth_blueprint
from ..models import db, User
from ..forms import LoginForm, RegistrationForm


@auth_blueprint.route('/login', methods=['get', 'post'])
def login():
    lf = LoginForm()
    if lf.validate_on_submit():
        user = User.query.filter((User.name == lf.username.data) | (User.email == lf.username.data)).first()
        if user is not None and user.verify(lf.password.data):
            login_user(user, lf.remember_me.data)
            flash('Login successful')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Wrong username or password')
    return render_template('login.html', form=lf)


@auth_blueprint.route('/register', methods=['get', 'post'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit():
        user = User(name=rf.username.data, email=rf.email.data, password=rf.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Login successful')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=rf)


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/users/<int:user_id>')
@login_required
def show(user_id):
    pass
