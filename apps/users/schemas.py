from ninja import Schema


class RegisterIn(Schema):
    username: str
    password: str
    email: str | None = None


class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    token: str
    username: str
    user_id: int


class UserOut(Schema):
    id: int
    username: str
    email: str
    bio: str
    date_joined: str


class MessageOut(Schema):
    message: str


class ErrorOut(Schema):
    detail: str
