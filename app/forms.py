from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import Required, Email, Length, EqualTo

from .models import User


class LoginForm(FlaskForm):

    username = StringField('Username or Email:', validators=[Required()])
    password = PasswordField('Password:', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):

    username = StringField('Username:', validators=[Required(), Length(2, 30)])
    email = StringField('Email:', validators=[Required(), Email(), Length(max=60)])
    password = PasswordField('Password:', validators=[Required(), Length(min=8)])
    password_2 = PasswordField('Confirm Password:', validators=[Required(),
                               EqualTo('password', message='Password do not match')])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError('This username is taken')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is already registered')


class PostForm(FlaskForm):

    title = StringField('Title:', validators=[Required()])
    body = TextAreaField('Body:', validators=[Required()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):

    body = TextAreaField('Leave a comment...', validators=[Required()])
    submit = SubmitField('Post')
