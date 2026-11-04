from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Введіть ім'я"),
            Length(
                min=4,
                max=10,
                message="Ім'я повинно містити від 4 до 10 символів",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введіть email"),
            Email(message="Введіть правильну електронну адресу"),
        ],
    )

    phone = StringField(
        "Телефон",
        validators=[
            Optional(),
            Regexp(
                r"^\+380\d{9}$",
                message="Формат телефону: +380XXXXXXXXX",
            ),
        ],
    )

    subject = SelectField(
        "Тема",
        choices=[
            ("", "Оберіть тему"),
            ("general", "Загальне питання"),
            ("cooperation", "Співпраця"),
            ("support", "Підтримка"),
            ("other", "Інше"),
        ],
        validators=[
            DataRequired(message="Оберіть тему повідомлення"),
        ],
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення"),
            Length(
                max=500,
                message="Повідомлення не може перевищувати 500 символів",
            ),
        ],
    )

    submit = SubmitField("Надіслати")
