import hashlib
import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import *
from flask_wtf import FlaskForm
# Import upload file element that will be used in web forms
from sqlalchemy.exc import SQLAlchemyError
# Import web form elements that will be used in web forms
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from wtforms.widgets.core import CheckboxInput

from models import User, db

auth = Blueprint("auth", __name__, template_folder="templates")
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(user_id)


@auth.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()

    if form.validate_on_submit():
        if request.method == 'POST' and 'submit' in request.form:
            user: User = User.query.filter_by(username=form.username.data).first()
            if not user:
                return render_template("login.html", form=form, error="Incorrect username/password")
            hashed_password = hashlib.scrypt(str(form.password.data).encode("utf-8"), salt=user.password_salt, r=8, p=1,
                                             n=32)
            if hashed_password == user.password_hash:
                login_user(user, remember=form.remember.data)
            else:
                return render_template("login.html", form=form, error="Incorrect username/password")
        return redirect(url_for("index"))

    return render_template("login.html", form=form)


@auth.route("/signup", methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SigunUpForm()

    if form.validate_on_submit():
        if request.method == 'POST' and 'submit' in request.form:
            salt = os.urandom(16)
            password_hash = hashlib.scrypt(str(form.password.data).encode("utf-8"), salt=salt, r=8, p=1, n=32)
            new_user = User(id=str(uuid.uuid4()), username=form.username.data, email=form.email.data,
                            password_hash=password_hash, password_salt=salt)

            try:
                db.session.add(new_user)
                db.session.commit()
            except SQLAlchemyError as err:
                return render_template("signup.html", form=form, error="Username taken")
            login_user(new_user, remember=form.remember.data)

        return redirect(url_for("index"))

    return render_template("signup.html", form=form)


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired("Username required")]
    )
    password = PasswordField(
        "Password",
        validators=[Length(max=8, message="Password is too short")]
    )
    remember = BooleanField(
        "Remember Me",
        widget=CheckboxInput()
    )
    submit = SubmitField('Login')


class SigunUpForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired("Username required")]
    )
    email = StringField(
        "Email",
        validators=[Email("Email required")]
    )
    password = PasswordField(
        "Password",
        validators=[Length(max=8, message="Password is too short")]
    )
    passwordConfirmation = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password", "Password doesn't match")]
    )
    remember = BooleanField(
        "Remember Me",
        widget=CheckboxInput()
    )
    submit = SubmitField('Sign up')
