from ninja import Schema


class ArticleIn(Schema):
    title: str
    content: str
    category_id: int | None = None


class ArticleUpdateIn(Schema):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None


class ArticleOut(Schema):
    id: int
    title: str
    content: str
    author_id: int
    author_username: str
    category_id: int | None = None
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
