import logging

from django.contrib import admin

from .models import Comment

logger = logging.getLogger("blog")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "author", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__username", "article__title")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        logger.info("Admin %s comment (id=%s)", action, obj.id)

    def delete_model(self, request, obj):
        logger.warning("Admin deleted comment (id=%s)", obj.id)
        super().delete_model(request, obj)
