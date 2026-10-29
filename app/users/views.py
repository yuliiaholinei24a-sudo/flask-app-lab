from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from . import user_bp


USERNAME = "yuliia"
PASSWORD = "33333"
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


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == USERNAME and password == PASSWORD:
            session["username"] = username
            flash("Ви увійшли в систему", "success")
            return redirect(url_for("users.profile"))

        flash("Неправильний логін або пароль", "danger")
        return redirect(url_for("users.login"))

    return render_template("users/login.html", title="Вхід")


@user_bp.route("/profile")
def profile():
    if "username" not in session:
        flash("Спочатку увійдіть у систему", "danger")
        return redirect(url_for("users.login"))

    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key.startswith(COOKIE_PREFIX)
    }

    return render_template(
        "users/profile.html",
        title="Профіль",
        username=session["username"],
        cookies=cookies,
        theme=session.get("theme", "light"),
    )


@user_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви вийшли із системи", "success")
    return redirect(url_for("users.login"))


@user_bp.route("/cookies/add", methods=["POST"])
def add_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему", "danger")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    max_age = request.form.get("max_age", "").strip()

    if not key or not max_age:
        flash("Заповніть усі обов'язкові поля", "danger")
        return redirect(url_for("users.profile"))

    try:
        max_age = int(max_age)
    except ValueError:
        flash("Термін дії має бути цілим числом!", "danger")
        return redirect(url_for("users.profile"))

    if not 1 <= max_age <= 34560000:
        flash("Термін дії має бути від 1 до 34560000 секунд!", "danger")
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
def delete_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему", "danger")
        return redirect(url_for("users.login"))

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
def delete_all_cookies():
    if "username" not in session:
        flash("Спочатку увійдіть у систему", "danger")
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies:
        if key.startswith(COOKIE_PREFIX):
            response.delete_cookie(key)

    flash("Усі додані cookies видалено", "success")
    return response


@user_bp.route("/theme/<string:theme>", methods=["POST"])
def change_theme(theme):
    if "username" not in session:
        flash("Спочатку увійдіть у систему", "danger")
        return redirect(url_for("users.login"))

    if theme not in ("light", "dark"):
        flash("Невідома кольорова тема", "danger")
        return redirect(url_for("users.profile"))

    session["theme"] = theme
    flash("Кольорову тему змінено", "success")
    return redirect(url_for("users.profile"))