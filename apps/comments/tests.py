from django.test import TestCase

from apps.articles.models import Article
from apps.users.models import AuthToken, User

from .models import Comment

API = "/api/comments"


class CommentTestBase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="commenter", password="strongpass123")
        self.author_token = AuthToken.objects.create(user=self.author)

        self.other_user = User.objects.create_user(username="other", password="strongpass123")
        self.other_token = AuthToken.objects.create(user=self.other_user)

        self.article = Article.objects.create(title="Article", content="Body", author=self.author)
        self.comment = Comment.objects.create(article=self.article, author=self.author, content="First!")

    def auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token}"}


class ListGetCommentTests(CommentTestBase):
    def test_list_comments_success(self):
        response = self.client.get(API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_single_comment_success(self):
        response = self.client.get(f"{API}/{self.comment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "First!")

    def test_get_nonexistent_comment_fails(self):
        response = self.client.get(f"{API}/9999")
        self.assertEqual(response.status_code, 404)


class CreateCommentTests(CommentTestBase):
    def test_create_comment_success(self):
        response = self.client.post(
            API,
            data={"article_id": self.article.id, "content": "Great read"},
            content_type="application/json",
            **self.auth(self.author_token.key),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 2)

    def test_create_comment_without_auth_fails(self):
        response = self.client.post(
            API,
            data={"article_id": self.article.id, "content": "Great read"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_on_nonexistent_article_fails(self):
        response = self.client.post(
            API,
            data={"article_id": 9999, "content": "Great read"},
            content_type="application/json",
            **self.auth(self.author_token.key),
        )
        self.assertEqual(response.status_code, 404)


class UpdateCommentTests(CommentTestBase):
    def test_owner_can_update_comment(self):
        response = self.client.put(
            f"{API}/{self.comment.id}",
            data={"content": "Updated comment"},
            content_type="application/json",
            **self.auth(self.author_token.key),
        )
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated comment")

    def test_non_owner_cannot_update_comment(self):
        response = self.client.put(
            f"{API}/{self.comment.id}",
            data={"content": "Hacked comment"},
            content_type="application/json",
            **self.auth(self.other_token.key),
        )
        self.assertEqual(response.status_code, 403)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "First!")


class DeleteCommentTests(CommentTestBase):
    def test_owner_can_delete_comment(self):
        response = self.client.delete(f"{API}/{self.comment.id}", **self.auth(self.author_token.key))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_non_owner_cannot_delete_comment(self):
        response = self.client.delete(f"{API}/{self.comment.id}", **self.auth(self.other_token.key))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
