# подключаем rest framework, транзакции, модели и сериализаторы заказов
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from .serializers import OrderSerializer


# viewset для управления заказами клиентов и администратора
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # администратор видит все заказы, а клиент только свои
        if user.role == 'ADMIN' or user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # создаём заказ из текущей корзины пользователя
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response(
                {'error': 'Ваша корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        delivery_address = request.data.get('delivery_address')
        if not delivery_address:
            return Response(
                {'error': 'Укажите адрес доставки'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # проверяем, что на складе достаточно каждой позиции корзины
        for cart_item in cart.items.all():
            if cart_item.product is None:
                return Response(
                    {'error': 'В корзине есть удалённый товар'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if cart_item.quantity > cart_item.product.stock_quantity:
                return Response(
                    {
                        'error': (
                            f'Недостаточно товара «{cart_item.product.title}» на складе. '
                            f'В наличии: {cart_item.product.stock_quantity}, '
                            f'в корзине: {cart_item.quantity}.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # создаём заказ и сохраняем итоговую сумму по текущей корзине
        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            comment=request.data.get('comment', ''),
            total_amount=cart.total_price
        )

        # переносим элементы корзины в позиции заказа и списываем остатки
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            # уменьшаем остаток на складе
            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save(update_fields=['stock_quantity'])

        # очищаем корзину после успешного оформления заказа
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        # изменение статуса заказа доступно только админу
        if not (request.user.role == 'ADMIN' or request.user.is_staff):
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.Statuses.choices):
            order.status = new_status
            order.save()
            return Response(OrderSerializer(order).data)

        return Response(
            {'error': 'Некорректный статус'},
            status=status.HTTP_400_BAD_REQUEST
        )