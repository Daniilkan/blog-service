from ninja import Router

from .models import Category
from .schemas import CategoryOut, ErrorOut

router = Router(tags=["categories"])


@router.get("", response=list[CategoryOut])
def list_categories(request):
    """Read-only listing of categories (management is done via the admin panel)."""
    return Category.objects.all()


@router.get("/{category_id}", response={200: CategoryOut, 404: ErrorOut})
def get_category(request, category_id: int):
    try:
        return 200, Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return 404, {"detail": "Category not found"}
