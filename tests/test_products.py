import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tinydb import TinyDB

from app import create_app
from app.products import images, views


class ProductTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.db = TinyDB(
            Path(self.temp_dir.name) / "products.json"
        )
        self.table = self.db.table("products")

        self.table_patch = patch.object(
            views,
            "products_table",
            self.table,
        )
        self.table_patch.start()

        self.upload_patch = patch.object(
            views,
            "save_image",
            return_value=None,
        )
        self.upload_patch.start()

        self.app = create_app("testing")
        self.client = self.app.test_client()

    def tearDown(self):
        self.upload_patch.stop()
        self.table_patch.stop()
        self.db.close()
        self.temp_dir.cleanup()

    def create_product(self):
        product = {
            "name": "Маленький принц",
            "content": "Книга про дружбу та любов",
            "price": "350.00",
            "category": "fiction",
            "quantity": 10,
            "image": "",
            "created_at": "2026-11-04T12:00:00",
        }

        product_id = self.table.insert(product)

        self.table.update(
            {"id": product_id},
            doc_ids=[product_id],
        )

        return product_id

    def valid_form_data(self):
        return {
            "name": "Нова книжка",
            "content": "Цікавий опис нової книжки",
            "price": "250.00",
            "category": "fantasy",
            "quantity": "5",
        }

    def test_product_list(self):
        self.create_product()

        response = self.client.get("/products/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Маленький принц".encode("utf-8"),
            response.data,
        )

    def test_product_detail(self):
        product_id = self.create_product()

        response = self.client.get(
            f"/products/{product_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Маленький принц".encode("utf-8"),
            response.data,
        )

    def test_product_not_found(self):
        response = self.client.get("/products/99999")
        self.assertEqual(response.status_code, 404)

    def test_create_product(self):
        response = self.client.post(
            "/products/add",
            data=self.valid_form_data(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.table), 1)

        product = self.table.all()[0]

        self.assertEqual(product["name"], "Нова книжка")
        self.assertEqual(product["price"], "250.00")
        self.assertEqual(product["quantity"], 5)

    def test_create_invalid_name(self):
        data = self.valid_form_data()
        data["name"] = "AB"

        response = self.client.post(
            "/products/add",
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.table), 0)

    def test_create_invalid_price(self):
        data = self.valid_form_data()
        data["price"] = "-10"

        response = self.client.post(
            "/products/add",
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.table), 0)

    def test_create_invalid_quantity(self):
        data = self.valid_form_data()
        data["quantity"] = "-5"

        response = self.client.post(
            "/products/add",
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.table), 0)

    def test_edit_product(self):
        product_id = self.create_product()
        data = self.valid_form_data()

        data["name"] = "Оновлена книжка"
        data["price"] = "500.00"

        response = self.client.post(
            f"/products/{product_id}/edit",
            data=data,
        )

        self.assertEqual(response.status_code, 302)

        product = self.table.get(doc_id=product_id)

        self.assertEqual(product["name"], "Оновлена книжка")
        self.assertEqual(product["price"], "500.00")

    def test_edit_not_found(self):
        response = self.client.get(
            "/products/99999/edit"
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_product(self):
        product_id = self.create_product()

        response = self.client.post(
            f"/products/{product_id}/delete"
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(
            self.table.get(doc_id=product_id)
        )

    def test_delete_not_found(self):
        response = self.client.post(
            "/products/99999/delete"
        )

        self.assertEqual(response.status_code, 404)

    def test_image_upload(self):
        data = self.valid_form_data()
        data["image"] = (
            io.BytesIO(b"fake image data"),
            "cover.jpg",
        )

        response = self.client.post(
            "/products/add",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.table), 1)

    def test_create_bunny_with_image(self):
        image_path = (
            Path(self.app.static_folder)
            / "images"
            / "books"
            / "bunny.jpg"
        )

        self.assertTrue(
            image_path.is_file(),
            f"Не знайдено зображення: {image_path}",
        )

        upload_dir = Path(self.temp_dir.name) / "uploads"

        with patch.object(
            images,
            "UPLOAD_FOLDER",
            upload_dir,
        ):
            with patch.object(
                views,
                "save_image",
                images.save_image,
            ):
                with image_path.open("rb") as image_file:
                    response = self.client.post(
                        "/products/add",
                        data={
                            "name": "Bunny",
                            "content": (
                                "Роман про студентів, дружбу "
                                "та загадкові події."
                            ),
                            "price": "450.00",
                            "category": "fiction",
                            "quantity": "5",
                            "image": (
                                image_file,
                                image_path.name,
                            ),
                        },
                        content_type="multipart/form-data",
                    )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.table), 1)

        product = self.table.all()[0]

        self.assertEqual(product["name"], "Bunny")
        self.assertEqual(product["price"], "450.00")
        self.assertTrue(product["image"])

        saved_image = upload_dir / product["image"]

        self.assertTrue(saved_image.is_file())
        self.assertEqual(
            saved_image.suffix.lower(),
            image_path.suffix.lower(),
        )

        with image_path.open("rb") as original:
            self.assertEqual(
                saved_image.read_bytes(),
                original.read(),
            )


if __name__ == "__main__":
    unittest.main()