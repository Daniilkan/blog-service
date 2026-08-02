import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models

TOKEN_LENGTH = 256


def generate_token() -> str:
    """Generate a URL-safe random token that is exactly TOKEN_LENGTH characters long."""
    token = secrets.token_urlsafe(TOKEN_LENGTH)
    while len(token) < TOKEN_LENGTH:
        token += secrets.token_urlsafe(TOKEN_LENGTH)
    return token[:TOKEN_LENGTH]


class User(AbstractUser):
    """Custom user model. Authentication token is stored on AuthToken (1-to-1)."""

    bio = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.username


class AuthToken(models.Model):
    """A 256-char random authentication token issued to a user on registration/login."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="auth_token")
    key = models.CharField(max_length=TOKEN_LENGTH, unique=True, db_index=True, default=generate_token)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_tokens"

    def __str__(self) -> str:
        return f"Token for {self.user.username}"

    def regenerate(self) -> "AuthToken":
        self.key = generate_token()
        self.save(update_fields=["key"])
        return self
