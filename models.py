from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_minio import Minio

db = SQLAlchemy()
minio = Minio()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, nullable=False, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    password_salt = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    has_profile_pic = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, id, username, email, password_hash, password_salt):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.email = email

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User %r>" % self.id


class Thread(db.Model):
    __tablename__ = "threads"
    id = db.Column(db.String, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author_id = db.Column(db.String, ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref="threads", lazy=True)
    body = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, id, title, author_id, body, rating):
        self.id = id
        self.title = title
        self.author_id = author_id
        self.body = body
        self.rating = rating

    def __repr__(self):
        return "<Thread %r>" % self.id


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String, nullable=False, primary_key=True)
    thread_id = db.Column(db.Integer, ForeignKey("threads.id"), nullable=False)
    thread = db.relationship("Thread", backref="posts", lazy=True)
    author_id = db.Column(db.String, ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref="posts", lazy=True)
    body = db.Column(db.Text, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, id, author_id, thread_id, body):
        self.id = id
        self.author_id = author_id
        self.thread_id = thread_id
        self.body = body

    def __repr__(self):
        return "<Post %r>" % self.id
