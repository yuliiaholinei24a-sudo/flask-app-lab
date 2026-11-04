from datetime import datetime
from decimal import Decimal

from flask import abort, flash, redirect, render_template, url_for

from . import product_bp
from .db import products_table
from .forms import ProductForm

products = [
    {
        "id": 1,
        "name": "Таємна історія",
        "author": "Донна Тартт",
        "price": 650,
        "content": "Шестеро студентів престижного коледжу захоплюються античною культурою. Їхня дружба, інтелектуальні пошуки та небезпечні таємниці поступово призводять до трагедії.",
        "image": "images/books/secret-history.jpg"
    },
    {
        "id": 2,
        "name": "Bunny",
        "author": "Мона Авад",
        "price": 540,
        "content": "Студентка Саманта потрапляє до дивного товариства однокурсниць, які називають одна одну Bunny. Її життя поступово перетворюється на химерну суміш реальності, фантазії та жаху.",
        "image": "images/books/bunny.jpg"
    },
    {
        "id": 3,
        "name": "Піранезі",
        "author": "Сюзанна Кларк",
        "price": 490,
        "content": "Піранезі живе у величезному загадковому Будинку, наповненому нескінченними залами, статуями й океанськими припливами. Поступово він починає відкривати правду про цей світ.",
        "image": "images/books/piranesi.jpg"
    }
]


@product_bp.route("/")
def product_list():
    return render_template(
        "products/products.html",
        title="Каталог книг",
        products=products
    )


@product_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = next(
        (p for p in products if p["id"] == product_id),
        None
    )

    if product is None:
        abort(404)

    return render_template(
        "products/detail_product.html",
        title=product["name"],
        product=product
    )


@product_bp.route("/add", methods=["GET", "POST"])
def product_add():
    form = ProductForm()

    if form.validate_on_submit():
        price = form.price.data.quantize(Decimal("0.01"))

        product = {
            "name": form.name.data.strip(),
            "content": form.content.data.strip(),
            "price": str(price),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": "",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

        product_id = products_table.insert(product)
        products_table.update(
            {"id": product_id},
            doc_ids=[product_id],
        )

        flash("Книжку успішно додано!", "success")
        return redirect(url_for("products.product_add"))

    if form.is_submitted() and form.errors:
        flash("Перевірте правильність заповнення форми", "danger")

    return render_template(
        "products/add_product.html",
        title="Додати книжку",
        form=form,
    )
