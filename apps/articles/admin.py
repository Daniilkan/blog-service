import logging

from django.contrib import admin

from .models import Article

logger = logging.getLogger("blog")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "content", "author__username")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        logger.info("Admin %s article '%s' (id=%s)", action, obj.title, obj.id)

    def delete_model(self, request, obj):
        logger.warning("Admin deleted article '%s' (id=%s)", obj.title, obj.id)
        super().delete_model(request, obj)
