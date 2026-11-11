from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length

from .models import utc_now


def strip_text(value):
    return value.strip() if isinstance(value, str) else value


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        filters=[strip_text],
        validators=[
            DataRequired(message="Введіть заголовок."),
            Length(
                max=150,
                message="Максимум 150 символів.",
            ),
        ],
    )

    content = TextAreaField(
        "Текст поста",
        filters=[strip_text],
        validators=[
            DataRequired(message="Введіть текст поста."),
        ],
    )

    enabled = BooleanField(
        "Відображати у списку",
        default=True,
    )

    publish_date = DateTimeLocalField(
        "Дата та час публікації (UTC)",
        format="%Y-%m-%dT%H:%M",
        default=utc_now,
        validators=[
            DataRequired(message="Укажіть дату та час."),
        ],
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікації"),
            ("tech", "Технології"),
            ("other", "Інше"),
        ],
        default="other",
        validators=[DataRequired()],
    )

    submit = SubmitField("Зберегти")


class DeletePostForm(FlaskForm):
    submit = SubmitField("Так, видалити")