from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from app import db
from app.posts.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Введіть ім'я користувача."),
            Length(min=4, max=16, message="Довжина має бути від 4 до 16 символів."),
            Regexp(
                r"^[A-Za-z][A-Za-z0-9_.]*$",
                message="Username must start with a letter and contain only letters, numbers, dots or underscores.",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введіть електронну пошту."),
            Email(message="Некоректна адреса електронної пошти."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Введіть пароль."),
            Length(min=6, message="Пароль має містити щонайменше 6 символів."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Підтвердіть пароль."),
            EqualTo("password", message="Паролі не збігаються."),
        ],
    )

    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(
            db.select(User).where(User.username == username.data)
        )
        if user:
            raise ValidationError(
                f"Користувач з таким іменем {username.data} вже існує."
            )

    def validate_email(self, email):
        user = db.session.scalar(
            db.select(User).where(User.email == email.data)
        )
        if user:
            raise ValidationError(
                f"Користувач з таким емейлом {email.data} вже існує."
            )


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введіть електронну пошту."),
            Email(message="Некоректна адреса електронної пошти."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Введіть пароль."),
        ],
    )

    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")