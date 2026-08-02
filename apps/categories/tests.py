from django.test import TestCase

from .models import Category

API = "/api/categories"


class CategoryTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech", slug="tech", description="Technology posts")

    def test_list_categories_success(self):
        response = self.client.get(API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Tech")

    def test_get_single_category_success(self):
        response = self.client.get(f"{API}/{self.category.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slug"], "tech")

    def test_get_nonexistent_category_fails(self):
        response = self.client.get(f"{API}/9999")
        self.assertEqual(response.status_code, 404)
