from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_name', 'title', 
            'description', 'price', 'stock_quantity', 
            'image', 'is_active', 'created_at'
        )