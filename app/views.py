import datetime as dt

from flask import request, session, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user

from . import main, auth, posts, users
from .models import db, User, Post, Comment
from .forms import LoginForm, RegistrationForm, PostForm, CommentForm


@auth.route('/login', methods=['get', 'post'])
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


@auth.route('/register', methods=['get', 'post'])
def register():
    rf = RegistrationForm()
    if rf.validate_on_submit():
        user = User(name=rf.username.data, email=rf.email.data, password=rf.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('register.html', form=rf)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@main.route('/')
@posts.route('/')
def index():
    g = request.args.get('g')
    if g is not None:
        month = int(g)
        frm = dt.date.today().replace(month=month, day=1)
        to = dt.date.today().replace(month=month)
        last_day = 31
        while True:
            try:
                to = to.replace(day=last_day)
            except ValueError:
                last_day -= 1
            else:
                break
        ce = db.and_(Post.created_at >= dt.datetime.combine(frm, dt.time.min),
                     Post.created_at <= dt.datetime.combine(to, dt.time.max))
        posts = Post.query.filter(ce).order_by(db.desc(Post.created_at)).all()
    else:
        posts = Post.query.order_by(db.desc(Post.created_at)).all()
    archive = None
    if posts:
        latest, earliest = Post.query.with_entities(db.func.max(Post.created_at), db.func.min(Post.created_at)).one()
        archive = [dt.date(dt.MINYEAR, mon, 1) for mon in range(latest.month, earliest.month - 1, -1)]
    return render_template('index.html', posts=posts, archive=archive)


@posts.route('/<int:post_id>')
def show(post_id):
    return render_template('show.html', post=Post.query.get_or_404(post_id), form=CommentForm())


@posts.route('/create', methods=['get', 'post'])
@login_required
def create():
    pf = PostForm()
    if not pf.validate_on_submit():
        return render_template('create.html', form=PostForm())
    post = Post(title=pf.title.data, body=pf.body.data, author_id=session['user_id'])
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('main.index'))


@posts.route('/<int:post_id>/comments/<int:comment_id>/like')
@posts.route('/<int:post_id>/like')
@login_required
def like(post_id, comment_id=None):
    user = User.query.get(session['user_id'])
    if comment_id is not None:
        entity = Comment.query.get(comment_id)
    else:
        entity = Post.query.get(post_id)
    entity.likes.append(user)
    db.session.commit()
    return redirect(url_for('posts.show', post_id=post_id))


@posts.route('/<int:post_id>/comments', methods=['post'])
@posts.route('/<int:post_id>/comments/<int:comment_id>/reply', methods=['post'])
@login_required
def post_comment(post_id, comment_id=None):
    cf = CommentForm()
    if not cf.validate_on_submit():
        return render_template('show.html', post=Post.query.get_or_404(post_id), form=cf)
    comment = Comment(body=cf.body.data, author_id=session['user_id'])
    if comment_id is not None:
        comment.comment_id = comment_id
    else:
        comment.post_id = post_id
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('posts.show', post_id=post_id))


@posts.route('/<int:post_id>/share')
def share(post_id):
    pass


@users.route('/<int:user_id>')
def show(user_id):
    pass


@main.add_app_template_filter
def date(date):
    return date.strftime('%A %B %d %Y')


@main.add_app_template_filter
def month(date):
    return date.strftime('%B')


@main.add_app_template_filter
def count(collection):
    return len(collection)


blueprints = [auth, main, posts, users]
