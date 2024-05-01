import uuid
from datetime import datetime

from flask import url_for
from flask_login import UserMixin
from flask_minio import Minio
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, desc

import config

db = SQLAlchemy()
minio = Minio()


def generate_uuid():
    if config.DATABASE_UUID_SUPPORT:
        return uuid.uuid4()
    return str(uuid.uuid4())


class UuidStrMixin:
    @property
    def str_id(self):
        try:
            if config.DATABASE_UUID_SUPPORT:
                return str(self.id)
            return self.id
        except AttributeError:
            raise AttributeError('UuidStrMixin was used but no id field is present')


class User(UserMixin, UuidStrMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True,
                   default=generate_uuid)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.LargeBinary(64), nullable=False)
    password_salt = db.Column(db.LargeBinary(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    has_profile_pic = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password_hash, password_salt):
        self.username = username
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.email = email

    def get_id(self):
        return self.id

    def follows_user(self, user_id):
        for follower in self.follows:
            if follower.following_id == user_id:
                return True
        return False

    def followed_by_user(self, user_id):
        for follower in self.followers:
            if follower.follower_id == user_id:
                return True
        return False

    def likes_thread(self, thread_id):
        for like in self.likes:
            if like.thread_id == thread_id:
                return like.liked
        return False

    def dislikes_thread(self, thread_id):
        for like in self.likes:
            if like.thread_id == thread_id:
                return not like.liked
        return False

    def get_feed(self, limit):
        return Thread.query.filter(Thread.author_id.in_([follow.following_id for follow in self.follows])).order_by(
            desc(Thread.posted)).limit(limit).all()

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __repr__(self):
        return "<User %r>" % self.id

    def get_profile_pic(self):
        if self.has_profile_pic:
            return config.MINIO_ENDPOINT + self.str_id
        return url_for('static', filename='img/profile.png')


class Thread(UuidStrMixin, db.Model):
    __tablename__ = "threads"
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True,
                   default=generate_uuid)
    title = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref="threads", lazy=True)
    body = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, author_id, body):
        self.title = title
        self.author_id = author_id
        self.body = body

    def get_likes(self):
        return sum([1 if like.liked else -1 for like in self.likes])

    def __repr__(self):
        return "<Thread %r>" % self.id


class Post(UuidStrMixin, db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True,
                   default=generate_uuid)
    thread_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("threads.id"), nullable=False)
    thread = db.relationship("Thread", backref="posts", lazy=True)
    author_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref="posts", lazy=True)
    body = db.Column(db.Text, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, author_id, thread_id, body):
        self.author_id = author_id
        self.thread_id = thread_id
        self.body = body

    def __repr__(self):
        return "<Post %r>" % self.id


class Follows(db.Model):
    __tablename__ = "follows"
    # The one who is following (the _follower_)
    follower_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("users.id"),
                            nullable=False, primary_key=True)
    follower = db.relationship("User", backref="follows", lazy=True, foreign_keys=[follower_id])
    # The one who is being followed (the follower is _following_ this user)
    following_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("users.id"),
                             nullable=False, primary_key=True)
    following = db.relationship("User", backref="followers", lazy=True, foreign_keys=[following_id])
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, follower_id, following_id):
        self.follower_id = follower_id
        self.following_id = following_id


class Likes(db.Model):
    __tablename__ = "likes"
    user_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("users.id"),
                        nullable=False, primary_key=True)
    user = db.relationship("User", backref="likes", lazy=True)
    thread_id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), ForeignKey("threads.id"),
                          nullable=False, primary_key=True)
    thread = db.relationship("Thread", backref="likes", lazy=True)
    # True means like, False means dislike
    liked = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id, thread_id, liked):
        self.user_id = user_id
        self.thread_id = thread_id
        self.liked = liked
