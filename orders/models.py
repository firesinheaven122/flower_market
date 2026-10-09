from django.conf import settings
from django.db import models
from store.models import Product


class Order(models.Model):
    class Statuses(models.TextChoices):
        CREATED = 'CREATED', 'Создан'
        PAID = 'PAID', 'Оплачен'
        IN_ASSEMBLY = 'IN_ASSEMBLY', 'В сборке'
        DELIVERING = 'DELIVERING', 'Передан в доставку'
        COMPLETED = 'COMPLETED', 'Выполнен'
        CANCELLED = 'CANCELLED', 'Отменен'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Покупатель",
    )
    status = models.CharField(
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.CREATED,
        verbose_name="Статус заказа",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Итоговая сумма"
    )
    delivery_address = models.TextField(verbose_name="Адрес доставки")
    comment = models.TextField(
        blank=True, null=True, verbose_name="Комментарий/Текст открытки"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name="Товар",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена при покупке"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.title if self.product else 'Удаленный товар'} x {self.quantity}"