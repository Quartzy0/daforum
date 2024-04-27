
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, nullable=False, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    password_salt = db.Column(db.String(16), nullable=False)

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
