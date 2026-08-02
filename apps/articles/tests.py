from django.test import TestCase

from apps.users.models import AuthToken, User

from .models import Article

API = "/api/articles"


class ArticleTestBase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="strongpass123")
        self.author_token = AuthToken.objects.create(user=self.author)

        self.other_user = User.objects.create_user(username="other", password="strongpass123")
        self.other_token = AuthToken.objects.create(user=self.other_user)

        self.article = Article.objects.create(
            title="Original title", content="Original content", author=self.author
        )

    def auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token}"}


class ListGetArticleTests(ArticleTestBase):
    def test_list_articles_success(self):
        response = self.client.get(API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_single_article_success(self):
        response = self.client.get(f"{API}/{self.article.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Original title")

    def test_get_nonexistent_article_fails(self):
        response = self.client.get(f"{API}/9999")
        self.assertEqual(response.status_code, 404)


class CreateArticleTests(ArticleTestBase):
    def test_create_article_success(self):
        response = self.client.post(
            API,
            data={"title": "New article", "content": "Some content"},
            content_type="application/json",
            **self.auth(self.author_token.key),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 2)

    def test_create_article_without_auth_fails(self):
        response = self.client.post(
            API,
            data={"title": "New article", "content": "Some content"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Article.objects.count(), 1)


class UpdateArticleTests(ArticleTestBase):
    def test_owner_can_update_article(self):
        response = self.client.put(
            f"{API}/{self.article.id}",
            data={"title": "Updated title"},
            content_type="application/json",
            **self.auth(self.author_token.key),
        )
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated title")

    def test_non_owner_cannot_update_article(self):
        response = self.client.put(
            f"{API}/{self.article.id}",
            data={"title": "Hacked title"},
            content_type="application/json",
            **self.auth(self.other_token.key),
        )
        self.assertEqual(response.status_code, 403)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Original title")


class DeleteArticleTests(ArticleTestBase):
    def test_owner_can_delete_article(self):
        response = self.client.delete(f"{API}/{self.article.id}", **self.auth(self.author_token.key))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_non_owner_cannot_delete_article(self):
        response = self.client.delete(f"{API}/{self.article.id}", **self.auth(self.other_token.key))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())

    def test_delete_nonexistent_article_fails(self):
        response = self.client.delete(f"{API}/9999", **self.auth(self.author_token.key))
        self.assertEqual(response.status_code, 404)
