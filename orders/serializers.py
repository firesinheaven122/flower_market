from rest_framework import serializers
from .models import Order, OrderItem
from store.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'status', 'status_display', 
            'total_amount', 'delivery_address', 'comment', 
            'items', 'created_at'
        )
        read_only_fields = ('user', 'status', 'total_amount')