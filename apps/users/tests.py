from django.test import TestCase

from .models import AuthToken, User

API = "/api/auth"


class RegisterTests(TestCase):
    def test_register_success(self):
        response = self.client.post(
            f"{API}/register",
            data={"username": "newuser", "password": "strongpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(len(body["token"]), 256)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(AuthToken.objects.filter(key=body["token"]).exists())

    def test_register_duplicate_username_fails(self):
        User.objects.create_user(username="taken", password="strongpass123")
        response = self.client.post(
            f"{API}/register",
            data={"username": "taken", "password": "strongpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_register_short_password_fails(self):
        response = self.client.post(
            f"{API}/register",
            data={"username": "shortpw", "password": "123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="loginuser", password="strongpass123")

    def test_login_success(self):
        response = self.client.post(
            f"{API}/login",
            data={"username": "loginuser", "password": "strongpass123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["token"]), 256)

    def test_login_wrong_password_fails(self):
        response = self.client.post(
            f"{API}/login",
            data={"username": "loginuser", "password": "wrongpass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user_fails(self):
        response = self.client.post(
            f"{API}/login",
            data={"username": "ghost", "password": "whatever123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)


class LogoutMeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tokenuser", password="strongpass123")
        self.token = AuthToken.objects.create(user=self.user)

    def _auth_headers(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token}"}

    def test_me_success(self):
        response = self.client.get(f"{API}/me", **self._auth_headers(self.token.key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "tokenuser")

    def test_me_without_token_fails(self):
        response = self.client.get(f"{API}/me")
        self.assertEqual(response.status_code, 401)

    def test_logout_invalidates_token(self):
        old_key = self.token.key
        response = self.client.post(f"{API}/logout", **self._auth_headers(old_key))
        self.assertEqual(response.status_code, 200)

        # old token should no longer work
        response2 = self.client.get(f"{API}/me", **self._auth_headers(old_key))
        self.assertEqual(response2.status_code, 401)

    def test_logout_without_token_fails(self):
        response = self.client.post(f"{API}/logout")
        self.assertEqual(response.status_code, 401)
