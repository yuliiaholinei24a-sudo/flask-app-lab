import logging
from pathlib import Path

from flask import current_app, flash, redirect, render_template, url_for

from .forms import ContactForm


def resume():
    return render_template("resume.html", title="Резюме")


def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            log_path = Path(current_app.root_path) / "contacts.log"

            logger = logging.getLogger("contacts")
            logger.setLevel(logging.INFO)
            logger.propagate = False

            if not logger.handlers:
                handler = logging.FileHandler(
                    log_path,
                    encoding="utf-8",
                )
                handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(message)s")
                )
                logger.addHandler(handler)

            logger.info(
                "Name: %s | Email: %s | Phone: %s | Subject: %s | Message: %s",
                form.name.data,
                form.email.data,
                form.phone.data,
                form.subject.data,
                form.message.data,
            )

            flash("Повідомлення успішно збережено!", "success")
            return redirect(url_for("contacts"))

        except OSError:
            flash(
                "Помилка під час збереження повідомлення",
                "danger",
            )
            return redirect(url_for("contacts"))

    if form.is_submitted() and form.errors:
        flash(
            "Перевірте правильність заповнення форми",
            "danger",
        )

    return render_template(
        "contacts.html",
        title="Контакти",
        form=form,
    )


def home():
    return render_template("homepage.html", title="Головна")


def register_routes(app):
    app.add_url_rule("/", view_func=resume)
    app.add_url_rule(
        "/contacts",
        view_func=contacts,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/contact",
        view_func=contacts,
        methods=["GET", "POST"],
    )
    app.add_url_rule("/homepage", view_func=home)