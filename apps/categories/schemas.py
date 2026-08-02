from ninja import Schema


class CategoryOut(Schema):
    id: int
    name: str
    slug: str
    description: str


class ErrorOut(Schema):
    detail: str
