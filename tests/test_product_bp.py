import unittest
from unittest.mock import patch

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from app import create_app
from app.products import views


class FlaskProductTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        self.db = TinyDB(storage=MemoryStorage)
        self.table = self.db.table("products")

        books = [
            (
                "Таємна історія",
                "Донна Тартт",
                "360.00",
                "secret-history.jpg",
            ),
            (
                "Bunny",
                "Мона Авад",
                "540.00",
                "bunny.jpg",
            ),
            (
                "Піранезі",
                "Сюзанна Кларк",
                "404.00",
                "piranesi.jpg",
            ),
        ]

        for name, content, price, image in books:
            product_id = self.table.insert({
                "name": name,
                "content": content,
                "price": price,
                "category": "fiction",
                "quantity": 5,
                "image": image,
                "created_at": "2026-11-12T12:00:00",
            })

            self.table.update(
                {"id": product_id},
                doc_ids=[product_id],
            )

        self.table_patch = patch.object(
            views,
            "products_table",
            self.table,
        )
        self.table_patch.start()

    def tearDown(self):
        self.table_patch.stop()
        self.db.close()

    def test_products_page(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)

    def test_products_list(self):
        response = self.client.get("/products/")
        html = response.get_data(as_text=True)

        for name in ["Таємна історія", "Bunny", "Піранезі"]:
            self.assertIn(name, html)

    def test_product_detail(self):
        response = self.client.get("/products/1")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Таємна історія", html)
        self.assertIn("Донна Тартт", html)

    def test_product_price(self):
        response = self.client.get("/products/2")
        html = response.get_data(as_text=True)

        self.assertIn("540", html)

    def test_product_image(self):
        response = self.client.get("/products/3")
        html = response.get_data(as_text=True)

        self.assertIn("piranesi.jpg", html)

    def test_invalid_product(self):
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()