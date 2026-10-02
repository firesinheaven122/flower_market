#подключаем serializers и модель корзины для отдачи данных в api
from rest_framework import serializers
from .models import Cart, CartItem
from store.serializers import ProductSerializer


#сериализатор элемента корзины, который содержит товар и итоговую стоимость позиции
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')


#сериализатор корзины с полным перечнем товаров и общей стоимостью
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_price', 'updated_at')