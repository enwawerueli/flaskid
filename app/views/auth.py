import os

from flask import (
    request, render_template, redirect, url_for, flash, current_app,
    send_from_directory)
from flask_login import login_required, login_user, logout_user, current_user

from . import auth_blueprint
from ..models import db, User
from ..forms import (
    LoginForm, RegistrationForm, ChangeUsernameForm, ChangeEmailForm,
    ChangePasswordForm, AccountRecoveryForm, PasswordResetForm, UpdateBioForm,
    ProfilePicForm)
from ..utils import send_mail, generate_token, verify_token


@auth_blueprint.route('/login', methods=['get', 'post'])
def login():
    lf = LoginForm()
    if lf.validate_on_submit():
        user = User.query.filter((User.username == lf.username.data) |
                                 (User.email == lf.username.data)).first()
        if user is not None and user.verify_password(lf.password.data):
            if login_user(user, lf.remember_me.data):
                flash('Login successful.', 'success')
            elif not user.is_active:
                login_user(user, lf.remember_me.data, force=True)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Wrong username or password.', 'danger')
    return render_template('login.html', form=lf)


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/register', methods=['get', 'post'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit():
        user = User(username=rf.username.data, email=rf.email.data,
                    password=rf.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.uid, 'account-activation')
        url = url_for('auth.activate', token=token, _external=True)
        send_mail(user.email, 'Account Activation', 'mail/welcome', user=user, url=url)
        login_user(user, force=True)
        flash('An activation link has been sent to your email.'
              'The link will expire after 1 hour.', 'info')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=rf)


@auth_blueprint.route('/account/activate/<token>')
@login_required
def activate(token):
    if not current_user.is_active:
        uid = verify_token(token, 'account-activation')
        if uid == current_user.uid:
            current_user.activated = True
            db.session.commit()
            flash('You have activated your account. Thank you!', 'success')
        else:
            flash('This activation link is invalid or has expired.', 'danger')
            return redirect(url_for('auth.inactive'))
    return redirect(url_for('main.index'))


@auth_blueprint.route('/account/inactive')
@login_required
def inactive():
    if current_user.is_anonymous or current_user.is_active:
        return redirect(url_for('main.index'))
    return render_template('activate_account.html')


@auth_blueprint.route('/account/activate')
@login_required
def resend_activation_link():
    token = generate_token(current_user.uid, 'account-activation')
    url = url_for('auth.activate', token=token, _external=True)
    send_mail(current_user.email, 'Account Activation', 'mail/welcome', url=url)
    flash('A new activation link has been sent to your email.'
          'The link will expire after 1 hour.', 'info')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/account/recovery', methods=['get', 'post'])
def recover_account():
    arf = AccountRecoveryForm()
    if arf.validate_on_submit():
        user = User.query.filter_by(email=arf.email.data).first()
        token = generate_token(user.uid, 'account-recovery')
        url = url_for('auth.reset_password', token=token, _external=True)
        send_mail(user.email, 'Account Recovery', 'mail/recover_account', user=user, url=url)
        flash('A password reset link has been sent to your email.'
              'The link will expire after 1 hour.', 'info')
    return render_template('recover_account.html', form=arf)


@auth_blueprint.route('/account/recovery/<token>', methods=['get', 'post'])
def reset_password(token):
    uid = verify_token(token, 'account-recovery')
    if uid is None:
        flash('This password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    prf = PasswordResetForm()
    if prf.validate_on_submit():
        user = User.query.get(uid)
        user.password = prf.password.data
        db.session.commit()
        login_user(user)
        flash('Your password was reset.', 'success')
        return redirect(url_for('main.index'))
    return render_template('reset_password.html', form=prf, token=token)


@auth_blueprint.route('/account/profile', methods=['get', 'post'])
@login_required
def profile():
    cuf = ChangeUsernameForm(obj=current_user)
    ubf = UpdateBioForm(obj=current_user)
    cef = ChangeEmailForm(obj=current_user)
    cpf = ChangePasswordForm()
    ppf = ProfilePicForm(obj=current_user)
    if 'submit_username' in request.form:
        if cuf.validate_on_submit():
            current_user.username = cuf.username.data
            db.session.commit()
            flash('Username changed.', 'success')
            return redirect(url_for('auth.profile'))
    elif 'submit_email' in request.form:
        if cef.validate_on_submit():
            token = generate_token([current_user.uid, cef.email.data], 'change-email')
            url = url_for('auth.confirm_new_email', token=token, _external=True)
            send_mail(cef.email.data, 'Confirm Your Email', 'mail/confirm_new_email', url=url)
            flash(
                'A confirmation link has been sent to your new email.'
                'The link will expire after 1 hour.', 'info')
            return redirect(url_for('auth.profile'))
    elif 'submit_password' in request.form:
        if cpf.validate_on_submit():
            current_user.password = cpf.new_password.data
            db.session.commit()
            flash('Password changed.', 'success')
            return redirect(url_for('auth.profile'))
    elif 'submit_bio' in request.form:
        if ubf.validate_on_submit():
            current_user.bio = ubf.bio.data
            db.session.commit()
            flash('Bio updated.', 'success')
            return redirect(url_for('auth.profile'))
    elif 'submit_pic' in request.form:
        if ppf.validate_on_submit():
            file = request.files['profile_pic']
            path = os.path.join(current_app.config['FILE_UPLOAD_PATH'], file.filename)
            file.save(path)
            current_user.profile_pic = file.filename
            db.session.commit()
            return redirect(url_for('auth.profile'))
    return render_template(
        'profile.html', name_form=cuf, email_form=cef, pswd_form=cpf,
        bio_form=ubf, pic_form=ppf)


@auth_blueprint.route('/account/profile/<filename>')
def profile_picture(filename):
    return send_from_directory(current_app.config['FILE_UPLOAD_PATH'], filename)


@auth_blueprint.route('/account/confirm-new-email/<token>')
@login_required
def confirm_new_email(token):
    uid, new_email = verify_token(token, 'change-email')
    if uid == current_user.uid:
        current_user.email = new_email
        db.session.commit()
        flash('Email changed.', 'success')
    else:
        flash('This confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('auth.profile'))


@auth_blueprint.route('/account/delete')
@login_required
def delete_account():
    uid = current_user.uid
    logout_user()
    db.session.delete(User.query.get(uid))
    db.session.commit()
    flash('Your account was deleted. Come back anytime!', 'info')
    return redirect(url_for('main.index'))
