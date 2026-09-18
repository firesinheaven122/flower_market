from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-слаг")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Категория",
    )
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Остаток на складе"
    )
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="Изображение"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.title} ({self.price} руб.)"