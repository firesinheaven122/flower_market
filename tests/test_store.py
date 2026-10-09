"""
Тесты для /api/v1/categories/ и /api/v1/products/
"""
import pytest
from store.models import Product


class TestCategories:
    URL = "/api/v1/categories/"

    def test_list_public(self, api_client, category):
        """Список категорий доступен анонимно."""
        response = api_client.get(self.URL)
        assert response.status_code == 200

    def test_create_requires_admin(self, api_client, client_user, db):
        """Обычный клиент не может создать категорию."""
        response = api_client.post(self.URL, {
            "name": "Пионы", "slug": "peonies",
        }, format="json")
        assert response.status_code in (401, 403)

    def test_admin_can_create(self, admin_client, db):
        """Админ создаёт категорию."""
        response = admin_client.post(self.URL, {
            "name": "Пионы", "slug": "peonies",
        }, format="json")
        assert response.status_code == 201


class TestProducts:
    URL = "/api/v1/products/"

    def test_list_public(self, api_client, product):
        """Анонимный пользователь видит активные товары."""
        response = api_client.get(self.URL)
        assert response.status_code == 200
        # Может быть пагинация или просто список
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        assert any(p["title"] == "Букет роз" for p in data)

    def test_inactive_hidden_from_public(self, api_client, inactive_product, product):
        """Неактивные товары не видны обычным пользователям."""
        response = api_client.get(self.URL)
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        titles = [p["title"] for p in data]
        assert "Скрытый букет" not in titles

    def test_admin_sees_inactive(self, admin_client, inactive_product):
        """Админ видит и неактивные товары."""
        response = admin_client.get(self.URL)
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        titles = [p["title"] for p in data]
        assert "Скрытый букет" in titles

    def test_search_by_title(self, api_client, product, db, category):
        """Поиск ?search= находит товар по части названия."""
        Product.objects.create(
            category=category, title="Пионы белые",
            price="2000.00", stock_quantity=3, is_active=True,
        )
        response = api_client.get(f"{self.URL}?search=Пионы")
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        titles = [p["title"] for p in data]
        assert "Пионы белые" in titles
        assert "Букет роз" not in titles

    def test_filter_by_category(self, api_client, product, category, db):
        """?category_id= фильтрует товары по категории."""
        response = api_client.get(f"{self.URL}?category_id={category.id}")
        assert response.status_code == 200

    def test_create_requires_admin(self, api_client, client_user, db):
        """Обычный клиент не может создать товар."""
        response = api_client.post(self.URL, {
            "title": "Новый", "price": "500.00", "stock_quantity": 1,
        }, format="json")
        assert response.status_code in (401, 403)

    def test_admin_create_product(self, admin_client, category):
        """Админ создаёт товар."""
        response = admin_client.post(self.URL, {
            "title": "Новый букет",
            "category": category.id,
            "price": "500.00",
            "stock_quantity": 5,
            "is_active": True,
        }, format="json")
        assert response.status_code == 201, response.data

    def test_create_negative_price(self, admin_client, category, db):
        """Отрицательная цена → 400 после добавления валидатора."""
        response = admin_client.post("/api/v1/products/", {
            "title": "Дешёвый",
            "category": category.id,
            "price": "-100.00",
            "stock_quantity": 1,
        }, format="json")
        assert response.status_code == 400, "БАГ: отрицательная цена принята"
        assert "price" in response.data

    def test_price_is_decimal(self, api_client, product):
        """Цена возвращается в правильном формате."""
        response = api_client.get(f"{self.URL}{product.id}/")
        assert response.status_code == 200
        assert response.data["price"] == "1500.00"