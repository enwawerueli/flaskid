from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import db, login_manager


class CCMixin(object):

    uid = db.Column(db.Integer(), primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    modified_at = db.Column(db.DateTime(), default=datetime.now)


class Post(db.Model, CCMixin):

    __tablename__ = 'posts'
    title = db.Column(db.String(255), nullable=False, unique=True, index=True)
    body = db.Column(db.Text(), nullable=False)
    author_id = db.Column(db.Integer(), db.ForeignKey('users.uid'))
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    def __str__(self):
        return '<Post: %s>' % self.title


class Comment(db.Model, CCMixin):

    __tablename__ = 'comments'
    body = db.Column(db.Text(), nullable=False)
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.uid'), nullable=False)
    post = db.relationship('Post', back_populates='comments')
    author_id = db.Column(db.Integer(), db.ForeignKey('users.uid'), nullable=False)
    author = db.relationship('User', back_populates='comments')
    comment_id = db.Column(db.Integer(), db.ForeignKey('comments.uid'))
    comments = db.relationship('Comment')

    def __str__(self):
        return '<Comment: <Post: %s>>' % self.post.title


class User(db.Model, UserMixin, CCMixin):

    __tablename__ = 'users'
    name = db.Column(db.String(60), nullable=False, unique=True, index=True)
    email = db.Column(db.String(60), unique=True, index=True)
    _password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=True)
    posts = db.relationship('Post', back_populates='author')
    comments = db.relationship('Comment', back_populates='author')

    @property
    def password(self):
        """ read password forbidden """
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, value):
        """ hash password """
        self._password = generate_password_hash(value)

    def __str__(self):
        return '<User: %s>' % self.name

    def verify(self, password):
        """ verify user """
        return check_password_hash(self._password, password)

    # Override
    def get_id(self):
        return str(self.uid)


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
