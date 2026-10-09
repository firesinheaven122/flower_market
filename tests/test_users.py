"""
Тесты для /api/v1/auth/...
Проверяем регистрацию, логин, получение и обновление профиля.
"""
import pytest


class TestRegister:
    URL = "/api/v1/auth/register/"

    def test_register_success(self, api_client, db):
        """Успешная регистрация возвращает 201 и создаёт пользователя."""
        response = api_client.post(self.URL, {
            "email": "new@test.com",
            "password": "StrongPass123!",
            "first_name": "Пётр",
            "last_name": "Новый",
            "phone": "+79001112233",
        }, format="json")

        assert response.status_code == 201, response.data
        assert response.data["email"] == "new@test.com"

        from django.contrib.auth import get_user_model
        User = get_user_model()
        assert User.objects.filter(email="new@test.com").exists()

    def test_register_duplicate_email(self, api_client, client_user):
        """Повторная регистрация на тот же email → 400."""
        response = api_client.post(self.URL, {
            "email": client_user.email,
            "password": "StrongPass123!",
        }, format="json")

        assert response.status_code == 400
        assert "email" in response.data

    def test_register_short_password(self, api_client, db):
        """Пароль короче 6 символов → 400."""
        response = api_client.post(self.URL, {
            "email": "short@test.com",
            "password": "123",
        }, format="json")

        assert response.status_code == 400
        assert "password" in response.data

    def test_register_without_email(self, api_client, db):
        """Без email → 400."""
        response = api_client.post(self.URL, {
            "password": "StrongPass123!",
        }, format="json")

        assert response.status_code == 400

    def test_register_default_role_is_client(self, api_client, db):
        """По умолчанию пользователь создаётся с ролью CLIENT."""
        api_client.post(self.URL, {
            "email": "role@test.com",
            "password": "StrongPass123!",
        }, format="json")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email="role@test.com")
        assert user.role == "CLIENT"


class TestLogin:
    URL = "/api/v1/auth/login/"

    def test_login_success(self, api_client, client_user):
        """Успешный логин возвращает access и refresh токены."""
        response = api_client.post(self.URL, {
            "email": "client@test.com",
            "password": "TestPass123!",
        }, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, client_user):
        """Неверный пароль → 401."""
        response = api_client.post(self.URL, {
            "email": "client@test.com",
            "password": "WrongPass",
        }, format="json")

        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client, db):
        """Несуществующий email → 401."""
        response = api_client.post(self.URL, {
            "email": "nobody@test.com",
            "password": "any",
        }, format="json")

        assert response.status_code == 401


class TestProfile:
    URL = "/api/v1/auth/me/"

    def test_profile_requires_auth(self, api_client, db):
        """Без токена профиль недоступен."""
        response = api_client.get(self.URL)
        assert response.status_code == 401

    def test_profile_returns_current_user(self, auth_client, client_user):
        """Авторизованный пользователь получает свой профиль."""
        response = auth_client.get(self.URL)

        assert response.status_code == 200
        assert response.data["email"] == client_user.email
        assert response.data["role"] == "CLIENT"

    def test_update_first_name(self, auth_client):
        """Можно обновить имя."""
        response = auth_client.patch(self.URL, {
            "first_name": "Обновлённое",
        }, format="json")

        assert response.status_code == 200
        assert response.data["first_name"] == "Обновлённое"

    def test_cannot_change_role(self, auth_client):
        """Роль только для чтения — попытка изменить игнорируется."""
        response = auth_client.patch(self.URL, {
            "role": "ADMIN",
        }, format="json")

        # Сериализатор помечает role как read_only, поэтому либо 200 с игнором, либо всё равно CLIENT
        assert response.status_code == 200
        assert response.data["role"] == "CLIENT"

    def test_cannot_change_email(self, auth_client):
        """Email только для чтения."""
        response = auth_client.patch(self.URL, {
            "email": "hacked@test.com",
        }, format="json")

        assert response.status_code == 200
        assert response.data["email"] == "client@test.com"