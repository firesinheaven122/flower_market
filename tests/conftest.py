"""
Общие фикстуры для всех тестов.
Фикстура — это функция, которая готовит данные и передаёт их в тест.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from store.models import Category, Product

User = get_user_model()


@pytest.fixture
def api_client():
    """Анонимный API-клиент. Как будто пользователь без логина."""
    return APIClient()


@pytest.fixture
def client_user(db):
    """Обычный клиент с ролью CLIENT."""
    return User.objects.create_user(
        username="client@test.com",
        email="client@test.com",
        password="TestPass123!",
        first_name="Иван",
        last_name="Клиентов",
        phone="+79000000001",
    )


@pytest.fixture
def admin_user(db):
    """Администратор с ролью ADMIN."""
    return User.objects.create_user(
        username="admin@test.com",
        email="admin@test.com",
        password="AdminPass123!",
        first_name="Админ",
        role="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def auth_client(api_client, client_user):
    """Авторизованный клиент — сразу с JWT-токеном в заголовке."""
    response = api_client.post(
        "/api/v1/auth/login/",
        {"email": "client@test.com", "password": "TestPass123!"},
        format="json",
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Авторизованный администратор — сразу с JWT."""
    response = api_client.post(
        "/api/v1/auth/login/",
        {"email": "admin@test.com", "password": "AdminPass123!"},
        format="json",
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def category(db):
    """Одна тестовая категория."""
    return Category.objects.create(name="Розы", slug="roses")


@pytest.fixture
def product(db, category):
    """Один тестовый активный товар."""
    return Product.objects.create(
        category=category,
        title="Букет роз",
        description="Красивые розы",
        price="1500.00",
        stock_quantity=10,
        is_active=True,
    )


@pytest.fixture
def inactive_product(db, category):
    """Неактивный товар — не должен быть виден обычным пользователям."""
    return Product.objects.create(
        category=category,
        title="Скрытый букет",
        description="Не должен отображаться",
        price="999.00",
        stock_quantity=5,
        is_active=False,
    )