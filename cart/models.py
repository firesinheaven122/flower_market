#подключаем настройки django и базовые модели для работы с бд
from django.conf import settings
from django.db import models
from store.models import Product


#определяем модель корзины пользователя
#каждому пользователю соответствует только одна корзина, поэтому используем onetoonefield
class Cart(models.Model):
    #связь с пользователем, который владеет данной корзиной
    #on_delete=models.CASCADE означает, что при удалении пользователя корзина тоже удаляется
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    #дата создания корзины; устанавливается автоматически при создании объекта
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    #дата последнего обновления корзины; автоматически изменяется при каждом сохранении
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    #настройки отображения модели в административной панели и интерфейсе
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    #возвращаем человекочитаемое название корзины для отладки и отображения в админке
    def __str__(self):
        return f"Корзина пользователя {self.user.email}"

    #вычисляем общую стоимость всех товаров в корзине
    #преобразуем список элементов в сумму их индивидуальных итогов
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


#определяем отдельный товар внутри корзины
#один объект корзины может содержать много элементов, поэтому используется foreignkey
class CartItem(models.Model):
    #ссылка на корзину, к которой относится данный элемент
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    #ссылка на конкретный товар из каталога
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар",
    )
    #количество единиц товара в корзине. по умолчанию одна позиция
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    #метаданные модели для административной панели и отображения множественного числа
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    #возвращаем строковое представление позиции в корзине
    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    #вычисляем итоговую стоимость конкретной позиции
    #для этого перемножаем цену товара на количество штук
    @property
    def total_price(self):
        return self.product.price * self.quantity