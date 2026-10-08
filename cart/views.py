# подключаем rest framework, ответы сервера и кастомные action-методы для корзины
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from store.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


# viewset для работы с корзиной только авторизованного пользователя
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create_cart(self, user):
        # получаем или создаём корзину текущего пользователя
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        # получаем корзину текущего пользователя и возвращаем её структуру
        cart = self._get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        # добавляем товар в корзину, создавая новую позицию или увеличивая количество
        cart = self._get_or_create_cart(request.user)

        # проверяем, что product_id передан
        product_id = request.data.get('product_id')
        if product_id is None:
            return Response(
                {'error': 'Поле product_id обязательно'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # проверяем, что product_id — целое число
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return Response(
                {'error': 'product_id должен быть целым числом'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # проверяем, что quantity — целое число и больше нуля
        quantity_raw = request.data.get('quantity', 1)
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'quantity должно быть целым числом'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quantity <= 0:
            return Response(
                {'error': 'quantity должно быть больше нуля'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # проверяем, что товар существует
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # проверяем, что товар активен
        if not product.is_active:
            return Response(
                {'error': 'Товар недоступен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # создаём или обновляем позицию корзины
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch', 'delete'], url_path='items/(?P<item_id>[^/.]+)')
    def item_detail(self, request, item_id=None):
        # изменяем количество товара или удаляем позицию из корзины
        cart = self._get_or_create_cart(request.user)
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Элемент не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'PATCH':
            quantity = request.data.get('quantity')
            if quantity and int(quantity) > 0:
                item.quantity = int(quantity)
                item.save()
            return Response(CartSerializer(cart).data)