from .settings import *  # noqa

# Тесты используют SQLite вместо PostgreSQL — быстрее и не требует установки БД
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Ускоряем хеширование паролей в тестах (пароль всё равно проверяется, но быстрее)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Медиафайлы в отдельную временную папку
MEDIA_ROOT = '/tmp/flower_shop_test_media'