from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # Администратор видит абсолютно все заказы, Клиент — только свои
        if user.role == 'ADMIN' or user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Оформление заказа из текущей корзины"""
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

        # Создаем сам заказ
        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            comment=request.data.get('comment', ''),
            total_amount=cart.total_price
        )

        # Переносим элементы из корзины в позиции заказа с фиксацией цен
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )

        # Очищаем корзину после успешного создания заказа
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        """PATCH /api/v1/orders/{id}/status/ — Только Администратор"""
        if not (request.user.role == 'ADMIN' or request.user.is_staff):
            return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.Statuses.choices):
            order.status = new_status
            order.save()
            return Response(OrderSerializer(order).data)
        
        return Response({'error': 'Некорректный статус'}, status=status.HTTP_400_BAD_REQUEST)