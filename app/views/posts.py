import datetime as dt

from flask import request, render_template, redirect, url_for
from flask_login import login_required, current_user

from . import main_blueprint, posts_blueprint
from ..models import db, User, Post, Comment, Permission
from ..forms import PostForm, CommentForm
from ..utils import permission_required


@main_blueprint.route('/')
def index():
    query = request.args.get('q')
    filter_ = None
    if query is not None:
        filter_ = Post.title.ilike('%' + query + '%')
    month = request.args.get('month')
    if month is not None:
        month = int(month)
        frm = dt.date.today().replace(month=month, day=1)
        to = dt.date.today().replace(month=month, day=28)
        max_day = 31
        while max_day > 28:
            try:
                to = to.replace(day=max_day)
                break
            except ValueError:
                max_day -= 1
        filter_ = db.and_(Post.created_at >= dt.datetime.combine(frm, dt.time.min),
                          Post.created_at <= dt.datetime.combine(to, dt.time.max))
    qry = Post.query.order_by(db.desc(Post.created_at))
    if filter_ is not None:
        qry = qry.filter(filter_)
    posts = qry.all()
    archive = None
    if posts:
        latest, earliest = Post.query.with_entities(db.func.max(Post.created_at),
                                                    db.func.min(Post.created_at)).one()
        archive = [dt.date(dt.MINYEAR, mon, 1) for mon in range(latest.month, earliest.month - 1, -1)]
    return render_template('index.html', posts=posts, q=query, archive=archive)


@posts_blueprint.route('/<int:post_id>')
def show(post_id):
    return render_template('show.html', post=Post.query.get_or_404(post_id), form=CommentForm())


@posts_blueprint.route('/create', methods=['get', 'post'])
@login_required
@permission_required(Permission.PUBLISH)
def create():
    pf = PostForm()
    if not pf.validate_on_submit():
        return render_template('create.html', form=PostForm())
    post = Post(title=pf.title.data, body=pf.body.data, author_id=current_user.uid)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('main.index'))


@posts_blueprint.route('/<int:post_id>/comments/<int:comment_id>/like')
@posts_blueprint.route('/<int:post_id>/like')
@login_required
def like(post_id, comment_id=None):
    user = User.query.get(current_user.uid)
    if comment_id is not None:
        entity = Comment.query.get(comment_id)
    else:
        entity = Post.query.get(post_id)
    entity.likes.append(user)
    db.session.commit()
    return redirect(url_for('posts.show', post_id=post_id))


@posts_blueprint.route('/<int:post_id>/comments', methods=['post'])
@posts_blueprint.route('/<int:post_id>/comments/<int:comment_id>/reply', methods=['post'])
@login_required
def post_comment(post_id, comment_id=None):
    cf = CommentForm()
    if not cf.validate_on_submit():
        return render_template('show.html', post=Post.query.get_or_404(post_id), form=cf)
    comment = Comment(body=cf.body.data, author_id=current_user.uid)
    if comment_id is not None:
        comment.parent_id = comment_id
    else:
        comment.post_id = post_id
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('posts.show', post_id=post_id))


@posts_blueprint.route('/<int:post_id>/share')
def share(post_id):
    pass


@posts_blueprint.route('/authors/<username>')
@login_required
def author_profile(username):
    pass
