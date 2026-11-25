from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length

from app import db

from .models import Tag, User, utc_now


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

    author_id = SelectField(
        "Автор",
        coerce=int,
        validators=[DataRequired(message="Оберіть автора.")],
    )

    tags = SelectMultipleField(
        "Теги",
        coerce=int,
    )

    submit = SubmitField("Зберегти")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = db.session.scalars(db.select(User).order_by(User.id)).all()
        self.author_id.choices = [(user.id, user.username) for user in users]

        all_tags = db.session.scalars(db.select(Tag).order_by(Tag.name)).all()
        self.tags.choices = [(tag.id, tag.name) for tag in all_tags]


class DeletePostForm(FlaskForm):
    submit = SubmitField("Так, видалити")