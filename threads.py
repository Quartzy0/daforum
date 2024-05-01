from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from werkzeug.exceptions import NotFound
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

from models import db, Post, Thread, Likes

threads = Blueprint("thread", __name__, url_prefix="/threads", template_folder="templates")


@threads.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = NewThreadForm()

    if form.validate_on_submit():
        new_thread = Thread(form.title.data, current_user.id, form.body.data)
        db.session.add(new_thread)
        db.session.commit()
        return redirect(url_for("thread.view_thread", thread_id=new_thread.id))
    return render_template("threads/new.html", form=form)


@threads.route("/<thread_id>", methods=["GET"])
def view_thread(thread_id):
    thread = Thread.query.get(thread_id)
    if thread is None:
        raise NotFound()
    posts = Post.query.filter_by(thread_id=thread_id).all()
    return render_template("threads/thread.html", thread=thread, posts=posts, form=ReplyForm())


@threads.route("/reply/<thread_id>", methods=["POST"])
@login_required
def reply_thread(thread_id):
    form = ReplyForm()
    if form.validate_on_submit():
        thread = Thread.query.get(thread_id)
        if thread is None:
            raise NotFound()
        new_post = Post(current_user.id, thread_id, form.body.data)
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for("thread.view_thread", thread_id=thread_id))


@threads.route("/<thread_id>/like", methods=["POST"])
@login_required
def like_thread(thread_id):
    thread = Thread.query.get(thread_id)
    if thread is None:
        raise NotFound("Thread not found")
    like = Likes.query.filter_by(user_id=current_user.id, thread_id=thread_id).first()
    if like:
        like.liked = True
    else:
        like = Likes(user_id=current_user.id, thread_id=thread_id, liked=True)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for("thread.view_thread", thread_id=thread_id))


@threads.route("/<thread_id>/dislike", methods=["POST"])
@login_required
def dislike_thread(thread_id):
    thread = Thread.query.get(thread_id)
    if thread is None:
        raise NotFound("Thread not found")
    like = Likes.query.filter_by(user_id=current_user.id, thread_id=thread_id).first()
    if like:
        like.liked = False
    else:
        like = Likes(user_id=current_user.id, thread_id=thread_id, liked=False)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for("thread.view_thread", thread_id=thread_id))


@threads.route("/<thread_id>/unlike", methods=["POST"])
@login_required
def unlike_thread(thread_id):
    thread = Thread.query.get(thread_id)
    if thread is None:
        raise NotFound("Thread not found")
    Likes.query.filter_by(user_id=current_user.id, thread_id=thread_id).delete()
    db.session.commit()
    return redirect(url_for("thread.view_thread", thread_id=thread_id))


class NewThreadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("Please enter a title.")])
    body = PageDownField("Body", validators=[DataRequired("Please enter a body.")])
    submit = SubmitField("Post")


class ReplyForm(FlaskForm):
    body = PageDownField("Reply", validators=[DataRequired("Please enter a body.")])
    submit = SubmitField("Reply")
