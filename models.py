import uuid
from datetime import datetime

from flask import url_for
from flask_login import UserMixin
from flask_minio import Minio
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

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
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True, default=generate_uuid)
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

    def __repr__(self):
        return "<User %r>" % self.id

    def get_profile_pic(self):
        if self.has_profile_pic:
            return config.MINIO_ENDPOINT + self.str_id
        return url_for('static', filename='img/profile.png')


class Thread(UuidStrMixin, db.Model):
    __tablename__ = "threads"
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True, default=generate_uuid)
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

    def __repr__(self):
        return "<Thread %r>" % self.id


class Post(UuidStrMixin, db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Uuid(as_uuid=config.DATABASE_UUID_SUPPORT), nullable=False, primary_key=True, default=generate_uuid)
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
