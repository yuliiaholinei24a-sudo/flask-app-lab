import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post


class PostTests(unittest.TestCase):
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

    def data(self, **changes):
        data = {
            "title": "Новий пост",
            "content": "Текст нового поста",
            "category": "tech",
            "publish_date": "2026-11-12T12:30",
            "enabled": "y",
        }
        data.update(changes)
        return data

    def add_post(self, **changes):
        data = {
            "title": "Початковий пост",
            "content": "Початковий текст",
            "posted": datetime(2026, 11, 12, 12, 30),
            "category": "news",
            "author": "yuliia",
            "is_active": True,
        }
        data.update(changes)

        post = Post(**data)
        db.session.add(post)
        db.session.commit()

        return post.id

    def test_create_page(self):
        response = self.client.get("/post/create")
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        response = self.client.post(
            "/post/create",
            data=self.data(),
        )

        self.assertEqual(response.status_code, 302)

        post = db.session.scalar(db.select(Post))

        self.assertEqual(post.title, "Новий пост")
        self.assertEqual(post.author, "Anonymous")

        page = self.client.get(response.headers["Location"])

        self.assertIn(
            "Пост успішно створено.",
            page.get_data(as_text=True),
        )

    def test_author_from_session(self):
        with self.client.session_transaction() as session:
            session["username"] = "yuliia"

        self.client.post("/post/create", data=self.data())

        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.author, "yuliia")

    def test_invalid_form(self):
        for changes in [
            {"title": " "},
            {"category": "invalid"},
        ]:
            with self.subTest(changes=changes):
                response = self.client.post(
                    "/post/create",
                    data=self.data(**changes),
                )

                self.assertEqual(response.status_code, 200)
                self.assertIsNone(
                    db.session.scalar(db.select(Post))
                )

    def test_list_filters_and_sorts(self):
        self.add_post(
            title="Старий пост",
            posted=datetime(2026, 1, 1),
        )
        self.add_post(
            title="Новіший пост",
            posted=datetime(2026, 2, 1),
        )
        self.add_post(
            title="Прихований пост",
            is_active=False,
        )

        response = self.client.get("/post")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Прихований пост", html)
        self.assertLess(
            html.index("Новіший пост"),
            html.index("Старий пост"),
        )

    def test_detail(self):
        post_id = self.add_post()
        response = self.client.get(f"/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Початковий текст",
            response.get_data(as_text=True),
        )

    def test_update_prefills_form(self):
        post_id = self.add_post(is_active=False)

        response = self.client.get(
            f"/post/{post_id}/update"
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('value="2026-11-12T12:30"', html)
        self.assertNotIn("checked", html)

    def test_update_post(self):
        post_id = self.add_post()
        data = self.data(title="Оновлений пост")
        data.pop("enabled")

        response = self.client.post(
            f"/post/{post_id}/update",
            data=data,
        )

        self.assertEqual(response.status_code, 302)

        db.session.expire_all()
        post = db.session.get(Post, post_id)

        self.assertEqual(post.title, "Оновлений пост")
        self.assertEqual(post.author, "yuliia")
        self.assertFalse(post.is_active)

    def test_invalid_update_preserves_data(self):
        post_id = self.add_post()

        response = self.client.post(
            f"/post/{post_id}/update",
            data=self.data(
                title="",
                content="Введений текст",
                publish_date="2026-12-01T09:15",
            ),
        )

        html = response.get_data(as_text=True)

        self.assertIn("Введений текст", html)
        self.assertIn('value="2026-12-01T09:15"', html)

        db.session.expire_all()

        self.assertEqual(
            db.session.get(Post, post_id).title,
            "Початковий пост",
        )

    def test_delete_post(self):
        post_id = self.add_post()

        response = self.client.get(
            f"/post/{post_id}/delete"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(
            db.session.get(Post, post_id)
        )

        response = self.client.post(
            f"/post/{post_id}/delete"
        )

        self.assertEqual(response.status_code, 302)

        db.session.expire_all()

        self.assertIsNone(
            db.session.get(Post, post_id)
        )

    def test_csrf_protection(self):
        post_id = self.add_post()
        self.app.config["WTF_CSRF_ENABLED"] = True

        response = self.client.post(
            f"/post/{post_id}/delete"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(
            db.session.get(Post, post_id)
        )

    def test_404(self):
        for path in [
            "/post/9999",
            "/post/9999/update",
            "/post/9999/delete",
            "/missing",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 404)
                self.assertIn(
                    "Сторінку не знайдено",
                    response.get_data(as_text=True),
                )


if __name__ == "__main__":
    unittest.main()