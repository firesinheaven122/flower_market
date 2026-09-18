from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # Доступно зарегистрированным

    def _get_or_create_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        """GET /api/v1/cart/ — просмотр своей корзины"""
        cart = self._get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """POST /api/v1/cart/items/ — добавить товар в корзину"""
        cart = self._get_or_create_cart(request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch', 'delete'], url_path='items/(?P<item_id>[^/.]+)')
    def item_detail(self, request, item_id=None):
        """
        PATCH /api/v1/cart/items/{id}/ — изменить количество
        DELETE /api/v1/cart/items/{id}/ — удалить позицию
        """
        cart = self._get_or_create_cart(request.user)
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Элемент не найден'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'PATCH':
            quantity = request.data.get('quantity')
            if quantity and int(quantity) > 0:
                item.quantity = int(quantity)
                item.save()
            return Response(CartSerializer(cart).data)