import unittest

from app import create_app, db
from app.posts.models import User


class FlaskUserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def create_user(self, username="testuser", email="test@example.com", password="secret123"):
        user = User(username=username, email=email, password="")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def test_greetings_page(self):
        response = self.client.get("/users/hi/John?age=30")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"JOHN", response.data)
        self.assertIn(b"30", response.data)

    def test_admin_page(self):
        response = self.client.get("/users/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ADMINISTRATOR", response.data)
        self.assertIn(b"45", response.data)

    def test_register_page_loads(self):
        response = self.client.get("/users/register")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Реєстрація", html)

    def test_login_page_loads(self):
        response = self.client.get("/users/login")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Вхід", html)

    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(
            "/users/register",
            data={
                "username": "yulia12",
                "email": "yulia12@gmail.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login", response.headers["Location"])

        user = db.session.scalar(db.select(User).where(User.email == "yulia12@gmail.com"))
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "yulia12")
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))

    def test_register_duplicate_email_fails(self):
        self.create_user(username="existing", email="dup@example.com")

        response = self.client.post(
            "/users/register",
            data={
                "username": "newuser",
                "email": "dup@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("вже існує", html)
        users_count = len(db.session.scalars(db.select(User)).all())
        self.assertEqual(users_count, 1)

    def test_login_success_and_access_account(self):
        self.create_user(username="oscar", email="oscar@gmail.com", password="mypassword")

        response = self.client.post(
            "/users/login",
            data={
                "email": "oscar@gmail.com",
                "password": "mypassword",
                "remember": "y",
            },
            follow_redirects=True,
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome, oscar!", html)
        self.assertIn("oscar@gmail.com", html)

    def test_login_invalid_password(self):
        self.create_user(username="oscar", email="oscar@gmail.com", password="mypassword")

        response = self.client.post(
            "/users/login",
            data={
                "email": "oscar@gmail.com",
                "password": "wrongpassword",
            },
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid email or password", html)

    def test_protected_routes_redirect_anonymous(self):
        for path in ("/users/account", "/users/list"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/users/login", response.headers["Location"])

    def test_users_list_for_authenticated_user(self):
        self.create_user(username="user1", email="user1@ex.com", password="pass123")
        self.create_user(username="user2", email="user2@ex.com", password="pass123")

        self.client.post(
            "/users/login",
            data={"email": "user1@ex.com", "password": "pass123"},
        )

        response = self.client.get("/users/list")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Users List (2)", html)
        self.assertIn("user2@ex.com", html)

    def test_logout(self):
        self.create_user(username="oscar", email="oscar@gmail.com", password="mypassword")

        self.client.post(
            "/users/login",
            data={"email": "oscar@gmail.com", "password": "mypassword"},
        )

        response = self.client.get("/users/logout", follow_redirects=True)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("You have been logged out.", html)

        account_resp = self.client.get("/users/account")
        self.assertEqual(account_resp.status_code, 302)
        self.assertIn("/users/login", account_resp.headers["Location"])


if __name__ == "__main__":
    unittest.main()