import uuid

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from werkzeug.exceptions import HTTPException, NotFound
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets.core import TextArea

from models import db, Post, User, Thread

threads = Blueprint("thread", __name__, url_prefix="/threads", template_folder="templates")


@threads.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = NewThreadForm()

    if form.validate_on_submit():
        new_thread = Thread(str(uuid.uuid4()), form.title.data, current_user.id, form.body.data, 0)
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
        new_post = Post(str(uuid.uuid4()), current_user.id, thread_id, form.body.data)
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for("thread.view_thread", thread_id=thread_id))


class NewThreadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("Please enter a title.")])
    body = StringField("Body", widget=TextArea(), validators=[DataRequired("Please enter a body.")])
    submit = SubmitField("Post")


class ReplyForm(FlaskForm):
    body = StringField("Reply", widget=TextArea(), validators=[DataRequired("Please enter a body.")])
    submit = SubmitField("Reply")
