from ninja import Schema


class CommentIn(Schema):
    article_id: int
    content: str


class CommentUpdateIn(Schema):
    content: str


class CommentOut(Schema):
    id: int
    article_id: int
    author_id: int
    author_username: str
    content: str
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_author_username(obj):
        return obj.author.username

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()


class MessageOut(Schema):
    message: str


class ErrorOut(Schema):
    detail: str
