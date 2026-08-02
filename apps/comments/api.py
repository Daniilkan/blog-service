import logging

from ninja import Router

from apps.articles.models import Article
from apps.users.auth import token_auth

from .models import Comment
from .schemas import CommentIn, CommentOut, CommentUpdateIn, ErrorOut, MessageOut

logger = logging.getLogger("blog")

router = Router(tags=["comments"])


@router.get("", response=list[CommentOut])
def list_comments(request, article_id: int | None = None):
    """Public: list comments, optionally filtered by article_id."""
    qs = Comment.objects.select_related("author", "article").all()
    if article_id is not None:
        qs = qs.filter(article_id=article_id)
    return qs


@router.get("/{comment_id}", response={200: CommentOut, 404: ErrorOut})
def get_comment(request, comment_id: int):
    try:
        return 200, Comment.objects.select_related("author", "article").get(id=comment_id)
    except Comment.DoesNotExist:
        return 404, {"detail": "Comment not found"}


@router.post("", auth=token_auth, response={201: CommentOut, 404: ErrorOut})
def create_comment(request, payload: CommentIn):
    try:
        article = Article.objects.get(id=payload.article_id)
    except Article.DoesNotExist:
        return 404, {"detail": "Article not found"}

    comment = Comment.objects.create(
        article=article,
        author=request.auth,
        content=payload.content,
    )
    logger.info(
        "Comment created: id=%s on article id=%s by '%s'", comment.id, article.id, request.auth.username
    )
    return 201, comment


@router.put("/{comment_id}", auth=token_auth, response={200: CommentOut, 403: ErrorOut, 404: ErrorOut})
def update_comment(request, comment_id: int, payload: CommentUpdateIn):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return 404, {"detail": "Comment not found"}

    if comment.author_id != request.auth.id:
        logger.warning(
            "Forbidden comment update: user '%s' tried to edit comment id=%s owned by '%s'",
            request.auth.username, comment.id, comment.author.username,
        )
        return 403, {"detail": "You can only edit your own comments"}

    comment.content = payload.content
    comment.save()
    logger.info("Comment updated: id=%s by '%s'", comment.id, request.auth.username)
    return 200, comment


@router.delete("/{comment_id}", auth=token_auth, response={200: MessageOut, 403: ErrorOut, 404: ErrorOut})
def delete_comment(request, comment_id: int):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return 404, {"detail": "Comment not found"}

    if comment.author_id != request.auth.id:
        logger.warning(
            "Forbidden comment delete: user '%s' tried to delete comment id=%s owned by '%s'",
            request.auth.username, comment.id, comment.author.username,
        )
        return 403, {"detail": "You can only delete your own comments"}

    comment_id_val = comment.id
    comment.delete()
    logger.info("Comment deleted: id=%s by '%s'", comment_id_val, request.auth.username)
    return 200, {"message": "Comment deleted"}
