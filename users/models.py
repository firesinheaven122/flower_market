from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        GUEST = 'GUEST', 'Гость'
        CLIENT = 'CLIENT', 'Клиент'
        ADMIN = 'ADMIN', 'Администратор'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=10, 
        choices=Roles.choices, 
        default=Roles.CLIENT
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"
