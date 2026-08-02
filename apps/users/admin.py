import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuthToken, User

logger = logging.getLogger("blog")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Additional info", {"fields": ("bio",)}),)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        logger.info("Admin %s user '%s' (id=%s) via admin panel", action, obj.username, obj.id)

    def delete_model(self, request, obj):
        logger.warning("Admin deleted user '%s' (id=%s) via admin panel", obj.username, obj.id)
        super().delete_model(request, obj)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username", "key")
