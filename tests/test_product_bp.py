import unittest
from app import app


class FlaskProductTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_page(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)

    def test_products_list(self):
        response = self.client.get("/products/")
        html = response.get_data(as_text=True)
        self.assertIn("Таємна історія", html)
        self.assertIn("Bunny", html)
        self.assertIn("Піранезі", html)

    def test_product_detail(self):
        response = self.client.get("/products/1")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Таємна історія", html)
        self.assertIn("Донна Тартт", html)

    def test_product_price(self):
        response = self.client.get("/products/2")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("540", html)

    def test_product_image(self):
        response = self.client.get("/products/3")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("piranesi.jpg", html)

    def test_invalid_product(self):
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
