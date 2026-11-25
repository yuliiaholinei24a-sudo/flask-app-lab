from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.posts.models import User

from . import user_bp
from .forms import LoginForm, RegistrationForm


COOKIE_PREFIX = "lab4_"


@user_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template(
        "users/hi.html",
        name=name,
        age=age,
    )


@user_bp.route("/admin")
def admin():
    return redirect(
        url_for("users.greetings", name="administrator", age=45)
    )


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password="",
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("users.login"))

    return render_template(
        "users/register.html",
        title="Register",
        form=form,
    )


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.email == form.email.data)
        )

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            session["username"] = user.username
            flash("You logged in successfully!", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("users.account"))

        flash("Error: Invalid email or password.", "danger")

    return render_template(
        "users/login.html",
        title="Login",
        form=form,
    )


@user_bp.route("/account")
@login_required
def account():
    return render_template(
        "users/account.html",
        title="Account",
        user=current_user,
    )


@user_bp.route("/list")
@login_required
def users_list():
    users = db.session.scalars(
        db.select(User).order_by(User.id)
    ).all()

    return render_template(
        "users/users_list.html",
        title="Users List",
        users=users,
    )


@user_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("users.login"))


@user_bp.route("/profile")
@login_required
def profile():
    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key.startswith(COOKIE_PREFIX)
    }

    return render_template(
        "users/profile.html",
        title="Профіль",
        username=current_user.username,
        cookies=cookies,
        theme=session.get("theme", "light"),
    )


@user_bp.route("/cookies/add", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    max_age = request.form.get("max_age", "").strip()

    if not key or not max_age:
        flash("Заповніть усі обов'язкові поля", "danger")
        return redirect(url_for("users.profile"))

    try:
        max_age = int(max_age)
    except ValueError:
        flash("Термін дії має бути цілим числом", "danger")
        return redirect(url_for("users.profile"))

    if not 1 <= max_age <= 34560000:
        flash("Термін дії має бути від 1 до 34560000 секунд", "danger")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        f"{COOKIE_PREFIX}{key}",
        value,
        max_age=max_age,
        httponly=True,
        samesite="Lax",
    )

    flash("Cookie є", "success")
    return response


@user_bp.route("/cookies/delete", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key", "").strip()
    cookie_name = f"{COOKIE_PREFIX}{key}"

    if not key or cookie_name not in request.cookies:
        flash("Cookie з таким ключем не знайдено", "danger")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(cookie_name)

    flash("Cookie успішно видалено", "success")
    return response


@user_bp.route("/cookies/delete-all", methods=["POST"])
@login_required
def delete_all_cookies():
    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies:
        if key.startswith(COOKIE_PREFIX):
            response.delete_cookie(key)

    flash("Усі додані cookies видалено", "success")
    return response


@user_bp.route("/theme/<string:theme>", methods=["POST"])
@login_required
def change_theme(theme):
    if theme not in ("light", "dark"):
        flash("Невідома кольорова тема", "danger")
        return redirect(url_for("users.profile"))

    session["theme"] = theme
    flash("Кольорову тему змінено", "success")
    return redirect(url_for("users.profile"))