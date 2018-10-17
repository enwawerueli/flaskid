from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app

from . import db, login_manager


class CCMixin(object):

    uid = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)


class Post(db.Model, CCMixin):

    __tablename__ = 'posts'
    title = db.Column(db.String(255), nullable=False, unique=True, index=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', cascade='all, delete-orphan')
    likes = db.relationship('User', back_populates='liked_posts', secondary='users_like_posts')

    def __str__(self):
        return '<Post: %s>' % self.title


class Comment(db.Model, CCMixin):

    __tablename__ = 'comments'
    body = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.uid'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    author = db.relationship('User', back_populates='comments')
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.uid'))
    comments = db.relationship('Comment')
    likes = db.relationship('User', back_populates='liked_comments', secondary='users_like_comments')

    def __str__(self):
        return '<Comment: <Post: %s>>' % self.post.title


class User(db.Model, UserMixin, CCMixin):

    __tablename__ = 'users'
    name = db.Column(db.String(60), nullable=False, unique=True, index=True)
    email = db.Column(db.String(60), unique=True, index=True)
    _password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.uid'), nullable=False)
    role = db.relationship('Role', back_populates='users')
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    liked_posts = db.relationship('Post', back_populates='likes', secondary='users_like_posts')
    liked_comments = db.relationship('Comment', back_populates='likes', secondary='users_like_comments')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            role = 'administrator' if self.email == current_app.config['MAIL_USERNAME'] else 'user'
            self.role = Role.query.filter_by(name=role).one()

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

    def can(self, permission):
        return self.role is not None and (self.role.permissions & permission) == permission

    def is_admin(self):
        return self.can(Permission.ADMINISTRATE)


class AnonymousUser(AnonymousUserMixin):

    def can(self, permission):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))  # Get user by id


users_like_posts = db.Table(
    'users_like_posts', db.metadata,
    db.Column('user_id', db.ForeignKey('users.uid'), nullable=False),
    db.Column('post_id', db.ForeignKey('posts.uid'), nullable=False),
    db.UniqueConstraint('user_id', 'post_id')
)


users_like_comments = db.Table(
    'users_like_comments', db.metadata,
    db.Column('user_id', db.ForeignKey('users.uid'), nullable=False),
    db.Column('comment_id', db.ForeignKey('comments.uid'), nullable=False),
    db.UniqueConstraint('user_id', 'comment_id')
)


class Permission(object):

    LIKE = 0x01
    COMMENT = 0x02
    PUBLISH = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTRATE = 0x80


class Role(db.Model):

    __tablename__ = 'roles'
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, index=True)
    permissions = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', back_populates='role')

    @classmethod
    def populate(cls):
        roles = dict(
            user=Permission.LIKE | Permission.COMMENT,
            moderator=Permission.LIKE | Permission.COMMENT | Permission.PUBLISH | Permission.MODERATE_COMMENTS,
            administrator=0xff
        )
        for name, permissions in roles.items():
            role = cls.query.filter_by(name=name).first()
            if role is None:
                role = cls(name=name)
            role.permissions = permissions  # update permissions
            db.session.add(role)
        db.session.commit()
