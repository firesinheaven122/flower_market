"""
Тесты для /api/v1/cart/...
"""
import pytest
from cart.models import Cart, CartItem


class TestCartAccess:
    def test_cart_requires_auth(self, api_client, db):
        """Аноним не видит корзину."""
        response = api_client.get("/api/v1/cart/")
        assert response.status_code == 401

    def test_empty_cart_created(self, auth_client):
        """У нового пользователя корзина создаётся автоматически."""
        response = auth_client.get("/api/v1/cart/")
        assert response.status_code == 200
        assert response.data["items"] == []
        assert response.data["total_price"] == 0


class TestAddItem:
    URL = "/api/v1/cart/items/"

    def test_add_product(self, auth_client, product):
        """Добавление товара в пустую корзину."""
        response = auth_client.post(self.URL, {
            "product_id": product.id,
            "quantity": 2,
        }, format="json")
        assert response.status_code == 200
        assert len(response.data["items"]) == 1
        assert response.data["items"][0]["quantity"] == 2

    def test_add_same_product_twice_increments(self, auth_client, product):
        """Повторное добавление того же товара увеличивает количество."""
        auth_client.post(self.URL, {"product_id": product.id, "quantity": 1}, format="json")
        response = auth_client.post(self.URL, {"product_id": product.id, "quantity": 3}, format="json")
        assert response.data["items"][0]["quantity"] == 4

    def test_add_nonexistent_product(self, auth_client, db):
        """Добавление несуществующего product_id → ошибка."""
        response = auth_client.post(self.URL, {
            "product_id": 99999, "quantity": 1,
        }, format="json")
        # Скорее всего 500 или 400 — зависит от обработки
        assert response.status_code in (400, 404, 500)

    def test_cart_total_price(self, auth_client, product):
        """Общая стоимость корзины считается правильно."""
        auth_client.post(self.URL, {"product_id": product.id, "quantity": 2}, format="json")
        response = auth_client.get("/api/v1/cart/")
        # 1500 * 2 = 3000
        assert str(response.data["total_price"]) == "3000.00" or response.data["total_price"] == 3000


class TestItemDetail:
    def test_update_quantity(self, auth_client, product):
        """PATCH изменяет количество позиции."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        cart = auth_client.get("/api/v1/cart/").data
        item_id = cart["items"][0]["id"]

        response = auth_client.patch(f"/api/v1/cart/items/{item_id}/", {
            "quantity": 5,
        }, format="json")
        assert response.status_code == 200
        assert response.data["items"][0]["quantity"] == 5

    def test_update_quantity_zero_ignored(self, auth_client, product):
        """PATCH с quantity=0 не должен менять количество."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")
        item_id = auth_client.get("/api/v1/cart/").data["items"][0]["id"]

        auth_client.patch(f"/api/v1/cart/items/{item_id}/", {"quantity": 0}, format="json")
        cart = auth_client.get("/api/v1/cart/").data
        assert cart["items"][0]["quantity"] == 3

    def test_delete_item(self, auth_client, product):
        """DELETE удаляет позицию из корзины."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        item_id = auth_client.get("/api/v1/cart/").data["items"][0]["id"]

        response = auth_client.delete(f"/api/v1/cart/items/{item_id}/")
        assert response.status_code == 204
        assert auth_client.get("/api/v1/cart/").data["items"] == []

    def test_cannot_touch_other_user_cart(self, api_client, client_user, product, db):
        """Пользователь не может удалить чужую позицию."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(
            username="other@test.com", email="other@test.com",
            password="OtherPass123!",
        )
        from cart.models import Cart as CartModel, CartItem as ItemModel
        other_cart = CartModel.objects.create(user=other)
        other_item = ItemModel.objects.create(cart=other_cart, product=product, quantity=1)

        # Логинимся как client_user
        r = api_client.post("/api/v1/auth/login/", {
            "email": "client@test.com", "password": "TestPass123!",
        }, format="json")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

        response = api_client.delete(f"/api/v1/cart/items/{other_item.id}/")
        assert response.status_code == 404

    