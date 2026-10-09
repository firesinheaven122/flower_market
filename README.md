# flower_market

# Проект Цветочный магазин

Команда состоит из:
- Васюкова Саша,
- Данилова Анастасия,
- Николенко Денис,
- Вацурова Елизавета.

Ссылка на отчёт: https://docs.google.com/document/d/1UMWGKg6kGMo7zi43GoU9Fhy1VUGqGvw3F8h7cN4ZiC8/edit?tab=t.0#heading=h.3334o2cpsck9

## Локальный запуск

Backend использует локальную SQLite-базу `db.sqlite3` по умолчанию. Для PostgreSQL можно задать `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` и `DB_PORT` переменными окружения.

В первом терминале из корня проекта выполни:

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_demo_catalog
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Во втором терминале запусти frontend:

```powershell
cd frontendik
npm install
npm run dev
```

Открой магазин по адресу [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Frontend обращается к API Django на `http://127.0.0.1:8000/api/v1`; CORS настроен для локального адреса frontend. `seed_demo_catalog` добавляет примеры категорий и букетов с фотографиями цветов в `media/products/`. Команда загружает фото с Unsplash только при отсутствии локального файла и безопасна при повторном запуске; существующие остатки товаров не сбрасываются. Новые товары можно добавлять через Django admin.

Полная интерактивная документация Swagger с эндпоинтами и авторизацией доступна по адресу: [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)
