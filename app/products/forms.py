from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


class ProductForm(FlaskForm):
    name = StringField(
        "Назва книжки",
        validators=[
            DataRequired(message="Введіть назву книжки"),
            Length(min=3, message="Назва повинна містити мінімум 3 символи"),
        ],
    )

    content = TextAreaField(
        "Опис книжки",
        validators=[
            DataRequired(message="Введіть опис книжки"),
        ],
        render_kw={"rows": 5, "cols": 40},
    )

    price = DecimalField(
        "Ціна (грн)",
        places=2,
        validators=[
            InputRequired(message="Введіть ціну"),
            NumberRange(min=0.01, message="Ціна повинна бути більшою за 0"),
        ],
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("", "Оберіть категорію"),
            ("fiction", "Художня література"),
            ("fantasy", "Фентезі"),
            ("detective", "Детективи"),
            ("romance", "Романтика"),
            ("science", "Наукова література"),
            ("other", "Інше"),
        ],
        validators=[
            DataRequired(message="Оберіть категорію"),
        ],
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(message="Введіть кількість"),
            NumberRange(min=0, message="Кількість не може бути від'ємною"),
        ],
    )

    image = FileField(
        "Зображення книжки",
        validators=[
            FileAllowed(
                ["png", "jpg", "jpeg"],
                message="Дозволені лише PNG, JPG та JPEG",
            ),
        ],
    )

    submit = SubmitField("Зберегти")
