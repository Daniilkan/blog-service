import logging

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.categories.models import Category
from apps.users.auth import token_auth

from .models import Article
from .schemas import ArticleIn, ArticleOut, ArticleUpdateIn, ErrorOut, MessageOut

logger = logging.getLogger("blog")

router = Router(tags=["articles"])


@router.get("", response=list[ArticleOut])
def list_articles(request):
    """Public: list all articles."""
    return Article.objects.select_related("author", "category").all()


@router.get("/{article_id}", response={200: ArticleOut, 404: ErrorOut})
def get_article(request, article_id: int):
    """Public: view a single article."""
    try:
        return 200, Article.objects.select_related("author", "category").get(id=article_id)
    except Article.DoesNotExist:
        return 404, {"detail": "Article not found"}


@router.post("", auth=token_auth, response={201: ArticleOut, 400: ErrorOut})
def create_article(request, payload: ArticleIn):
    category = None
    if payload.category_id is not None:
        category = get_object_or_404(Category, id=payload.category_id)

    article = Article.objects.create(
        title=payload.title,
        content=payload.content,
        author=request.auth,
        category=category,
    )
    logger.info("Article created: id=%s title='%s' by '%s'", article.id, article.title, request.auth.username)
    return 201, article


@router.put("/{article_id}", auth=token_auth, response={200: ArticleOut, 403: ErrorOut, 404: ErrorOut})
def update_article(request, article_id: int, payload: ArticleUpdateIn):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return 404, {"detail": "Article not found"}

    if article.author_id != request.auth.id:
        logger.warning(
            "Forbidden article update: user '%s' tried to edit article id=%s owned by '%s'",
            request.auth.username, article.id, article.author.username,
        )
        return 403, {"detail": "You can only edit your own articles"}

    if payload.title is not None:
        article.title = payload.title
    if payload.content is not None:
        article.content = payload.content
    if payload.category_id is not None:
        article.category = get_object_or_404(Category, id=payload.category_id)
    article.save()

    logger.info("Article updated: id=%s by '%s'", article.id, request.auth.username)
    return 200, article


@router.delete("/{article_id}", auth=token_auth, response={200: MessageOut, 403: ErrorOut, 404: ErrorOut})
def delete_article(request, article_id: int):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return 404, {"detail": "Article not found"}

    if article.author_id != request.auth.id:
        logger.warning(
            "Forbidden article delete: user '%s' tried to delete article id=%s owned by '%s'",
            request.auth.username, article.id, article.author.username,
        )
        return 403, {"detail": "You can only delete your own articles"}

    article_id_val = article.id
    article.delete()
    logger.info("Article deleted: id=%s by '%s'", article_id_val, request.auth.username)
    return 200, {"message": "Article deleted"}
