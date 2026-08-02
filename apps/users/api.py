import logging

from ninja import Router

from .auth import token_auth
from .schemas import ErrorOut, LoginIn, MessageOut, RegisterIn, TokenOut, UserOut
from .services import UserServiceError, login_user, logout_user, register_user

logger = logging.getLogger("blog")

router = Router(tags=["auth"])


@router.post("/register", response={201: TokenOut, 400: ErrorOut})
def register(request, payload: RegisterIn):
    try:
        auth_token = register_user(payload.username, payload.password, payload.email)
    except UserServiceError as exc:
        return exc.status_code, {"detail": exc.message}
    return 201, {
        "token": auth_token.key,
        "username": auth_token.user.username,
        "user_id": auth_token.user.id,
    }


@router.post("/login", response={200: TokenOut, 401: ErrorOut})
def login(request, payload: LoginIn):
    try:
        auth_token = login_user(payload.username, payload.password)
    except UserServiceError as exc:
        return exc.status_code, {"detail": exc.message}
    return 200, {
        "token": auth_token.key,
        "username": auth_token.user.username,
        "user_id": auth_token.user.id,
    }


@router.post("/logout", auth=token_auth, response={200: MessageOut})
def logout(request):
    logout_user(request.auth)
    return 200, {"message": "Logged out successfully. Token has been invalidated."}


@router.get("/me", auth=token_auth, response={200: UserOut})
def me(request):
    user = request.auth
    return 200, {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "date_joined": user.date_joined.isoformat(),
    }
