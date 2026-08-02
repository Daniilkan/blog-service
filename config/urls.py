from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from apps.articles.api import router as articles_router
from apps.categories.api import router as categories_router
from apps.comments.api import router as comments_router
from apps.users.api import router as users_router

api = NinjaAPI(
    title="Blog API",
    version="1.0.0",
    description=(
        "Blog backend API. Use POST /api/auth/register or /api/auth/login to obtain a "
        "256-character token, then send it as `Authorization: Token <token>` on protected "
        "endpoints. A JWT alternative is available at /api/jwt/ (django-ninja-jwt)."
    ),
)

api.add_router("/auth", users_router)
api.add_router("/articles", articles_router)
api.add_router("/comments", comments_router)
api.add_router("/categories", categories_router)

# Optional "plus" requirement: JWT auth via django-ninja-jwt, mounted separately.
jwt_api = NinjaExtraAPI(urls_namespace="jwt")
jwt_api.register_controllers(NinjaJWTDefaultController)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/jwt/", jwt_api.urls),
]
