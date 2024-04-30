import hashlib
import os
from io import BytesIO

from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# Import upload file element that will be used in web forms
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import NotFound
# Import web form elements that will be used in web forms
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from wtforms.widgets.core import CheckboxInput

from models import User, db, minio, Thread

users = Blueprint("users", __name__, url_prefix="/user", template_folder="templates")
login_manager = LoginManager()
login_manager.login_view = 'users.login'


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(user_id)


def redirect_dest(fallback):
    dest = request.args.get('next')
    return redirect(dest) if dest else redirect(fallback)


@users.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect_dest(url_for("index"))
    form = LoginForm()

    if form.validate_on_submit():
        if request.method == 'POST' and 'submit' in request.form:
            user: User = User.query.filter_by(username=form.username.data).first()
            if not user:
                flash('Invalid username or password.', 'danger')
                return render_template("users/login.html", form=form)
            hashed_password = hashlib.scrypt(str(form.password.data).encode('utf-8'),
                                             salt=user.password_salt, r=8, p=1, n=32)
            if hashed_password == user.password_hash:
                login_user(user, remember=form.remember.data)
                return redirect_dest(url_for("index"))
            else:
                flash('Invalid username or password.', 'danger')

    return render_template("users/login.html", form=form)


@users.route("/signup", methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        return redirect_dest(url_for("index"))
    form = SigunUpForm()

    if form.validate_on_submit():
        if request.method == 'POST' and 'submit' in request.form:
            salt = os.urandom(16)
            password_hash = hashlib.scrypt(str(form.password.data).encode("utf-8"), salt=salt, r=8, p=1, n=32, dklen=64)
            new_user = User(username=form.username.data, email=form.email.data,
                            password_hash=password_hash,
                            password_salt=salt)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=form.remember.data)
                return redirect_dest(url_for("index"))
            except IntegrityError:
                flash("Username/Email already taken!", "danger")
            except SQLAlchemyError as e:
                raise e

    return render_template("users/signup.html", form=form)


@users.route("/<user_id>")
def view_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User not found")
    return render_template("users/profile.html", user=user)


@users.route("/<user_id>/threads")
def user_threads(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise NotFound("User not found")
    threads = Thread.query.filter_by(author_id=user_id).all()
    return render_template("users/threads.html", user=user, threads=threads)


@users.route("/", methods=["GET", "POST"])
@login_required
def view_current_user():
    form = EditProfileForm()
    if form.validate_on_submit():
        hashed_password = hashlib.scrypt(str(form.password.data).encode("utf-8"),
                                         salt=current_user.password_salt,
                                         r=8, p=1, n=32)
        if hashed_password != current_user.password_hash:
            flash("Wrong password.", "danger")
            return render_template("users/edit-profile.html", form=form)
        current_user.username = form.username.data
        current_user.email = form.email.data

        image = form.profilePicture.data
        if image is not None:
            try:
                imgL = int(form.profilePictureCropX.data)
                imgU = int(form.profilePictureCropY.data)
                imgR = imgL + int(form.profilePictureCropSize.data)
                imgB = imgU + int(form.profilePictureCropSize.data)
                img = Image.open(image.stream)
                temp = BytesIO()
                img = img.crop((imgL, imgU, imgR, imgB))
                img.save(temp, format="webp")
                img_bytes = temp.getvalue()
                minio.client.put_object("profile-pictures", current_user.str_id, BytesIO(img_bytes), len(img_bytes),
                                        content_type="image/webp")
                current_user.has_profile_pic = True
            except:
                flash("Error when processing profile picture", "danger")
        db.session.commit()
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("users/edit-profile.html", form=form)


@users.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("index"))


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired("Username required")]
    )
    password = PasswordField(
        "Password",
        validators=[Length(min=5, message="Password is too short")]
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
        validators=[Length(min=5, message="Password is too short")]
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


class EditProfileForm(FlaskForm):
    profilePicture = FileField(
        'Photo',
        validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'])],
        description='Profile picture.'
    )
    profilePictureCropX = StringField(
        "Crop X",
    )
    profilePictureCropY = StringField(
        "Crop Y",
    )
    profilePictureCropSize = StringField(
        "Crop Size",
    )
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
        validators=[DataRequired(message="Password required")]
    )
    submit = SubmitField('Save')
