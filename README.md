# 🌸 Flower Shop — Экосистема онлайн-магазина авторской флористики

![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

---

## 🚀 О продукте

**Flower Shop** — это современное, высокопроизводительное e-commerce решение для продажи цветов, авторских монобукетов и подарочных наборов[cite: 2]. Проект построен на классическом стекe **Django REST Framework + React (Vite)** и решает ключевую задачу сервиса доставки: дает покупателям удобный, премиальный интерфейс выбора букетов, а флористам и администраторам — полный контроль над остатками, ценами и статусами заказов в реальном времени[cite: 3, 4, 6].

### 🔥 Почему это крутое решение:
* **Изолированная корзина и ролевой доступ:** Четкое разделение прав (`GUEST`, `CLIENT`, `ADMIN`) с автоматической ротацией JWT-токенов без повторных разлогинов[cite: 3, 6, 15].
* **Гарантия неизменяемости цен (Price Snapshot):** При оформлении заказа цена каждого букета навсегда фиксируется в сущности `OrderItem`[cite: 4, 11, 12]. Даже если цена в каталоге изменится на следующий день, история чека покупателя останется юридически чистой и нетронутой[cite: 11, 12].
* **Умная защита складских остатков:** Система автоматически контролирует наличие букетов на складе, исключая возможность заказа отсутствующих позиций[cite: 4, 11].
* **Безопасная работа с медиафайлами:** Динамическая подгрузка изображений букетов с автонастройкой базовых URL для Vite/React фронтенда[cite: 4, 13, 14].

---

## 👥 Команда разработки

* **Васюкова Александра** — Бэкэнд-разработчик
* **Данилова Анастасия** — Фронтенд-разработчик
* **Николенко Денис** — Системный аналитик
* **Вацурова Елизавета** — Тестировщик

📄 **[Читать полный отчёт по проекту в Google Docs](https://docs.google.com/document/d/1UMWGKg6kGMo7zi43GoU9Fhy1VUGqGvw3F8h7cN4ZiC8/edit?tab=t.0#heading=h.3334o2cpsck9)**

---

## 📂 Подробный разбор сущностей базы данных (ERD)

База данных проекта спроектирована на **PostgreSQL** (с возможностью локального фоллбека на SQLite) и разбита на 4 функциональных модуля из 7 ключевых таблиц[cite: 4, 5, 6].

### 1. Модуль пользователей (`users`)
* **`users_user` (Пользователи):**
  * `id` (`bigint`, PK) — Уникальный ID пользователя[cite: 1, 5].
  * `email` (`varchar`, UNIQUE) — Основной идентификатор для логина[cite: 1, 5, 11].
  * `password` (`varchar`) — Безопасный PBKDF2/SHA256 хеш пароля[cite: 1, 5, 11].
  * `first_name`, `last_name` (`varchar`) — Имя и фамилия покупателя[cite: 1, 5].
  * `phone` (`varchar`) — Контактный номер для связи с курьером[cite: 1, 5].
  * `role` (`varchar`) — Кастомная роль: `GUEST`, `CLIENT` или `ADMIN`[cite: 1, 3, 5].

### 2. Модуль каталога (`store`)
* **`store_category` (Категории букетов):**
  * `id` (`bigint`, PK) — Идентификатор категории[cite: 1, 5].
  * `name` (`varchar`) — Название (например: *«Монобукеты»*, *«Цветочные боксы»*)[cite: 1, 5, 7].
  * `slug` (`varchar`, UNIQUE) — Человекопонятная ссылка для фильтрации и красивых URL[cite: 1, 5, 10].
  * `description` (`text`) — Подробное описание категории[cite: 1, 5].

* **`store_product` (Букеты и товары):**
  * `id` (`bigint`, PK) — Идентификатор товара[cite: 1, 5].
  * `category_id` (`bigint`, FK) — Ссылка на категорию товара[cite: 1, 5, 10].
  * `title` (`varchar`) — Название букета (*«Воздушная нежность»*)[cite: 1, 5, 7].
  * `description` (`text`) — Полный состав букета, инструкция по уходу[cite: 1, 5, 10].
  * `price` (`decimal(10,2)`) — Текущая розничная стоимость товара[cite: 1, 5, 10].
  * `stock_quantity` (`integer`) — Доступное количество букетов на складе[cite: 1, 4, 5, 10].
  * `image` (`varchar`) — Путь к файлу фотографии букета в медиа-хранилище `media/products/`[cite: 1, 4, 5, 10].
  * `is_active` (`boolean`) — Флаг видимости (неактивные товары видят только администраторы)[cite: 1, 5, 11].

### 3. Модуль корзины (`cart`)
* **`cart_cart` (Персональная корзина):**
  * `id` (`bigint`, PK) — Идентификатор корзины[cite: 1, 5].
  * `user_id` (`bigint`, FK, UNIQUE) — Связь **1:1** с пользователем. У каждого покупателя может быть строго одна активная корзина[cite: 1, 5, 11].
  * `created_at` (`timestamp`) — Дата и время первого добавления товара[cite: 1, 5].

* **`cart_cartitem` (Элементы корзины):**
  * `id` (`bigint`, PK) — Идентификатор позиции[cite: 1, 5].
  * `cart_id` (`bigint`, FK) — Ссылка на корзину покупателя[cite: 1, 5, 11].
  * `product_id` (`bigint`, FK) — Ссылка на выбранный букет[cite: 1, 5, 11].
  * `quantity` (`integer`) — Выбранное количество букетов[cite: 1, 5, 11].

### 4. Модуль заказов (`orders`)
* **`orders_order` (Оформленные заказы):**
  * `id` (`bigint`, PK) — Уникальный номер заказа[cite: 1, 5].
  * `user_id` (`bigint`, FK) — Ссылка на клиента, оформившего покупку[cite: 1, 5, 12].
  * `status` (`varchar`) — Статус выполнения: `CREATED`, `PAID`, `IN_ASSEMBLY`, `DELIVERING`, `COMPLETED`, `CANCELLED`[cite: 1, 4, 5, 12].
  * `total_amount` (`decimal(10,2)`) — Итоговая сумма заказа с учетом всех позиций[cite: 1, 5, 12].
  * `delivery_address` (`text`) — Адрес вручения цветов[cite: 1, 4, 5, 12].
  * `created_at` (`timestamp`) — Точное время создания заказа[cite: 1, 5, 12].

* **`orders_orderitem` (Состав заказа / Snapshot):**
  * `id` (`bigint`, PK) — Идентификатор записи[cite: 1, 5].
  * `order_id` (`bigint`, FK) — Ссылка на сформированный заказ[cite: 1, 5, 12].
  * `product_id` (`bigint`, FK) — Ссылка на купленный товар[cite: 1, 5, 12].
  * `price` (`decimal(10,2)`) — **Зафиксированная цена** единицы товара на момент покупки[cite: 1, 4, 5, 12].
  * `quantity` (`integer`) — Купленное количество[cite: 1, 5, 12].

---

## 🛠 Технологический стек

* **Backend:** Python 3.10+, Django 4+, Django REST Framework (DRF), SimpleJWT, `drf-spectacular` (Swagger/OpenAPI 3)[cite: 5, 11, 13].
* **Database:** PostgreSQL / SQLite[cite: 5, 6].
* **Frontend:** React 18 (Pure JavaScript, Без TypeScript), Vite, React Router DOM, Axios[cite: 6, 13, 14].
* **Безопасность:** CORS-Headers, JWT Auth (Bearer Tokens), кастомные Permission-классы (`IsAdminOrReadOnly`)[cite: 13].

---

## 📡 Полный справочник REST API Эндпоинтов (`/api/v1/`)

### 🔑 Аутентификация и Профиль (`/auth/`)
| Метод | Эндпоинт | Права | Описание |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Любой | Регистрация нового аккаунта (`email`, `password`, `first_name`, `last_name`, `phone`)[cite: 12, 13]. |
| `POST` | `/api/v1/auth/login/` | Любой | Авторизация и получение пары JWT-токенов (`access`, `refresh`)[cite: 11, 13]. |
| `POST` | `/api/v1/auth/token/refresh/` | Любой | Автоматическое обновление просроченного `access`-токена[cite: 13, 14, 15]. |
| `GET` | `/api/v1/auth/me/` | Client / Admin | Получение данных текущего авторизованного профиля[cite: 12, 13]. |
| `PATCH` | `/api/v1/auth/me/` | Client / Admin | Обновление личных данных (имя, телефон)[cite: 12, 13]. |

### 💐 Каталог и Категории (`/categories/`, `/products/`)
| Метод | Эндпоинт | Права | Описание |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/categories/` | Любой | Список всех категорий цветов[cite: 11]. |
| `GET` | `/api/v1/products/` | Любой | Каталог товаров с поиском (`?search=`), фильтром (`?category=`) и сортировкой (`?ordering=price`)[cite: 11]. |
| `GET` | `/api/v1/products/{id}/` | Любой | Детальная карточка выбранного букета[cite: 11]. |
| `POST` | `/api/v1/products/` | Admin | Добавление нового букета в каталог (с загрузкой фото)[cite: 4, 13]. |
| `PATCH` | `/api/v1/products/{id}/` | Admin | Редактирование цены, остатка на складе или описания букета[cite: 4, 13]. |
| `DELETE`| `/api/v1/products/{id}/` | Admin | Удаление товара из каталога[cite: 4, 13]. |

### 🛒 Управление корзиной (`/cart/`)
| Метод | Эндпоинт | Права | Описание |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/cart/` | Client / Admin | Просмотр содержимого корзины с автоматическим пересчетом итоговой суммы[cite: 11, 12]. |
| `POST` | `/api/v1/cart/items/` | Client / Admin | Добавление товара в корзину (`product_id`, `quantity`)[cite: 12]. |
| `PATCH` | `/api/v1/cart/items/{item_id}/` | Client / Admin | Изменение количества конкретного товара в корзине[cite: 12]. |
| `DELETE`| `/api/v1/cart/items/{item_id}/` | Client / Admin | Удаление позиции из корзины[cite: 12]. |

### 📦 Заказы (`/orders/`)
| Метод | Эндпоинт | Права | Описание |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/orders/` | Client / Admin | История заказов (Клиент видит только свои; Админ видит заказы всех клиентов)[cite: 4, 12, 15]. |
| `POST` | `/api/v1/orders/` | Client / Admin | Оформление заказа из текущей корзины с фиксацией цен и списыванием остатков[cite: 4, 12]. |
| `GET` | `/api/v1/orders/{id}/` | Client / Admin | Детальная информация по конкретному заказу[cite: 12]. |
| `PATCH` | `/api/v1/orders/{id}/` | Admin | Изменение статуса заказа (`CREATED` $\rightarrow$ `IN_ASSEMBLY` $\rightarrow$ `DELIVERING` $\rightarrow$ `COMPLETED`)[cite: 4, 12, 15]. |

---

## 💻 Инструкция по локальному запуску

Для работы приложения потребуются установленный **Python 3.10+** и **Node.js 18+**.

### 1️⃣ Шаг 1: Запуск Backend (Django REST Framework)
Откройте первый терминал в корне проекта:

```bash
# 1. Установка зависимостей
venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Применение миграций базы данных
venv\Scripts\python.exe manage.py migrate

# 3. Наполнение каталога красивыми демо-товарами и категориями
venv\Scripts\python.exe manage.py seed_demo_catalog

# 4. Запуск локального сервера API
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

### 2️⃣ Шаг 2: Запуск Frontend (React + Vite)
Во втором терминале запустите frontend:

```powershell
cd frontendik
npm install
npm run dev
```

Открой магазин по адресу [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Frontend обращается к API Django на `http://127.0.0.1:8000/api/v1`; CORS настроен для локального адреса frontend.

Полная интерактивная документация Swagger с эндпоинтами и авторизацией доступна по адресу: [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)
