import logging

from django.contrib.auth import authenticate
from django.db import IntegrityError

from .models import AuthToken, User

logger = logging.getLogger("blog")


class UserServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(username: str, password: str, email: str | None = None) -> AuthToken:
    if User.objects.filter(username=username).exists():
        logger.warning("Registration failed: username '%s' already taken", username)
        raise UserServiceError("Username already taken", status_code=400)

    if len(password) < 8:
        logger.warning("Registration failed: password too short for '%s'", username)
        raise UserServiceError("Password must be at least 8 characters long", status_code=400)

    try:
        user = User.objects.create_user(username=username, password=password, email=email or "")
    except IntegrityError:
        logger.error("Registration failed: integrity error for '%s'", username)
        raise UserServiceError("Could not create user", status_code=400)

    auth_token = AuthToken.objects.create(user=user)
    logger.info("User registered: '%s' (id=%s)", user.username, user.id)
    return auth_token


def login_user(username: str, password: str) -> AuthToken:
    user = authenticate(username=username, password=password)
    if user is None:
        logger.warning("Login failed for username '%s'", username)
        raise UserServiceError("Invalid credentials", status_code=401)

    auth_token, _ = AuthToken.objects.get_or_create(user=user)
    logger.info("User logged in: '%s' (id=%s)", user.username, user.id)
    return auth_token


def logout_user(user: User) -> None:
    """Invalidate the current token by regenerating it, so it can no longer be used."""
    try:
        auth_token = user.auth_token
        auth_token.regenerate()
        logger.info("User logged out: '%s' (id=%s)", user.username, user.id)
    except AuthToken.DoesNotExist:
        logger.warning("Logout attempted for '%s' with no active token", user.username)
