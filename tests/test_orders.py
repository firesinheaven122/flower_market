"""
Тесты для /api/v1/orders/...
"""
import pytest
from orders.models import Order


class TestCreateOrder:
    URL = "/api/v1/orders/"

    def test_cannot_order_empty_cart(self, auth_client, db):
        """Пустая корзина → 400."""
        response = auth_client.post(self.URL, {
            "delivery_address": "ул. Пушкина, д. 1",
        }, format="json")
        assert response.status_code == 400
        assert "error" in response.data

    def test_cannot_order_without_address(self, auth_client, product):
        """Без адреса → 400."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        response = auth_client.post(self.URL, {}, format="json")
        assert response.status_code == 400

    def test_successful_order(self, auth_client, product):
        """Успешное оформление заказа."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 2}, format="json")
        response = auth_client.post(self.URL, {
            "delivery_address": "ул. Пушкина, д. 1",
            "comment": "Позвонить за час",
        }, format="json")

        assert response.status_code == 201, response.data
        assert response.data["status"] == "CREATED"
        # 1500 * 2 = 3000
        assert str(response.data["total_amount"]) == "3000.00"

    def test_cart_cleared_after_order(self, auth_client, product):
        """После заказа корзина пуста."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        auth_client.post(self.URL, {"delivery_address": "addr"}, format="json")

        cart = auth_client.get("/api/v1/cart/").data
        assert cart["items"] == []

    def test_order_requires_auth(self, api_client, db):
        """Аноним не может создать заказ."""
        response = api_client.post(self.URL, {"delivery_address": "addr"}, format="json")
        assert response.status_code == 401


class TestOrderList:
    def test_client_sees_only_own_orders(self, auth_client, admin_client, product):
        """Клиент видит только свои заказы."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        auth_client.post("/api/v1/orders/", {"delivery_address": "addr"}, format="json")

        response = auth_client.get("/api/v1/orders/")
        assert response.status_code == 200
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        assert len(data) == 1

    def test_admin_sees_all_orders(self, auth_client, admin_client, product):
        """Админ видит заказы всех пользователей."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        auth_client.post("/api/v1/orders/", {"delivery_address": "addr"}, format="json")

        response = admin_client.get("/api/v1/orders/")
        assert response.status_code == 200


class TestOrderStatus:
    def test_only_admin_can_change_status(self, auth_client, product):
        """Клиент не может менять статус."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        order = auth_client.post("/api/v1/orders/", {"delivery_address": "addr"}, format="json").data

        response = auth_client.patch(f"/api/v1/orders/{order['id']}/status/", {
            "status": "PAID",
        }, format="json")
        assert response.status_code == 403

    def test_admin_changes_status(self, auth_client, admin_client, product):
        """Админ меняет статус заказа."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        order = auth_client.post("/api/v1/orders/", {"delivery_address": "addr"}, format="json").data

        response = admin_client.patch(f"/api/v1/orders/{order['id']}/status/", {
            "status": "PAID",
        }, format="json")
        assert response.status_code == 200
        assert response.data["status"] == "PAID"

    def test_invalid_status_rejected(self, auth_client, admin_client, product):
        """Несуществующий статус → 400."""
        auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
        order = auth_client.post("/api/v1/orders/", {"delivery_address": "addr"}, format="json").data

        response = admin_client.patch(f"/api/v1/orders/{order['id']}/status/", {
            "status": "INVALID_STATUS",
        }, format="json")
        assert response.status_code == 400

    def test_order_rejected_when_insufficient_stock(self, auth_client, product):
        """Если в корзине больше, чем на складе → 400."""
        auth_client.post("/api/v1/cart/items/", {
            "product_id": product.id, "quantity": 9999,
        }, format="json")

        response = auth_client.post("/api/v1/orders/", {
            "delivery_address": "ул. Пушкина, д. 1",
        }, format="json")

        assert response.status_code == 400
        assert "error" in response.data
        assert "Недостаточно товара" in response.data["error"]


    def test_stock_decreases_after_order(self, auth_client, product):
        """После оформления заказа остаток на складе уменьшается."""
        from store.models import Product

        auth_client.post("/api/v1/cart/items/", {
            "product_id": product.id, "quantity": 3,
        }, format="json")

        response = auth_client.post("/api/v1/orders/", {
            "delivery_address": "ул. Пушкина, д. 1",
        }, format="json")
        assert response.status_code == 201

        fresh = Product.objects.get(id=product.id)
        assert fresh.stock_quantity == 7


    def test_order_rejected_with_deleted_product(self, auth_client, product, db):
        """Если товар удалён из БД, заказ не создаётся."""
        auth_client.post("/api/v1/cart/items/", {
            "product_id": product.id, "quantity": 1,
        }, format="json")

        product.delete()

        response = auth_client.post("/api/v1/orders/", {
            "delivery_address": "ул. Пушкина, д. 1",
        }, format="json")
        assert response.status_code == 400
    