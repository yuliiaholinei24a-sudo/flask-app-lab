from flask import render_template, abort
from . import product_bp

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
