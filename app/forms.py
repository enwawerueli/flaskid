from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, TextAreaField,
    ValidationError, FileField)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import current_user

from .models import User


class Exists(object):

    def __init__(self, model_class, column_name, message=None):
        self._Model = model_class
        self._column_name = column_name
        self._column = getattr(model_class, column_name, None)
        self._message = message

    def __call__(self, form, field):
        if self._column is None:
            raise AttributeError('Model has no attribute \'%s\'' % self._column_name)
        if not self.check(field.data):
            raise ValidationError(self._message)  # raise error if test fails
        return None

    def check(self, value):
        if self._Model.query.filter(self._column == value).first() is not None:
            return True  # if a record exists, pass
        return False  # otherwise, fail


class Unique(Exists):

    def check(self, value):
        return not super(Unique, self).check(value)


username_is_unique = Unique(User, 'username', message='This username is taken.')
email_is_unique = Unique(User, 'email', message='This email is already registered.')
email_exists = Exists(User, 'email', message='We could not find a user with this email.')


class LoginForm(FlaskForm):

    username = StringField('Username or Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):

    username = StringField(
        'Username:', validators=[DataRequired(), Length(2, 30), username_is_unique])
    email = StringField(
        'Email:', validators=[DataRequired(), Email(), Length(max=60), email_is_unique])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=8)])
    password_2 = PasswordField('Confirm Password:', validators=[
                               EqualTo('password', message='Password do not match.')])
    submit = SubmitField('Register')


class PostForm(FlaskForm):

    title = StringField('Title:', validators=[DataRequired()])
    body = TextAreaField('Body:', validators=[DataRequired()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):

    body = TextAreaField('Leave a comment...', validators=[DataRequired()])
    submit = SubmitField('Post')


class AccountRecoveryForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email(), email_exists])
    submit_email = SubmitField('Request Link')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password:', validators=[DataRequired()])
    password_2 = PasswordField(
        'Confirm New Password:',
        validators=[EqualTo('new_password', message='Password do not match.')])
    submit = SubmitField('Reset Password')


class ChangeUsernameForm(FlaskForm):
    username = StringField(
        'Username:', validators=[DataRequired(), Length(2, 30), username_is_unique])
    submit_username = SubmitField('Change Username')


class UpdateBioForm(FlaskForm):
    bio = TextAreaField('Bio:', validators=[Length(max=255)], render_kw=dict(rows=5, maxlength=255))
    submit_bio = SubmitField('Update Bio')


class ChangeEmailForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email(), email_is_unique])
    submit_email = SubmitField('Change Email')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password:', validators=[DataRequired()])
    new_password_2 = PasswordField(
        'Confirm New Password:',
        validators=[EqualTo('new_password', message='Password do not match.')])
    old_password = PasswordField('Old Password:', validators=[DataRequired()])
    submit_password = SubmitField('Change Password')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Wrong password.')


class ProfilePicForm(FlaskForm):
    profile_pic = FileField('Choose Profile Picture:', validators=[DataRequired()])
    submit_pic = SubmitField('Upload')

    def validate_profile_pic(self, field):
        ext = field.data.filename.lower().rsplit('.', 1)[-1]
        if ext not in current_app.config['ALLOWED_FILE_EXTENSIONS']:
            raise ValidationError(
                'File must be in one of (%s) formats.'
                % ' | '.join(current_app.config['ALLOWED_FILE_EXTENSIONS']))
        field.data.filename = current_user.username + '.' + ext
