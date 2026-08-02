import logging

from django.contrib import admin

from .models import Category

logger = logging.getLogger("blog")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        logger.info("Admin %s category '%s' (id=%s)", action, obj.name, obj.id)

    def delete_model(self, request, obj):
        logger.warning("Admin deleted category '%s' (id=%s)", obj.name, obj.id)
        super().delete_model(request, obj)
