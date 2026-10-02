#подключаем django rest framework для сериализации данных
from rest_framework import serializers
from .models import Category, Product


#сериализатор для категорий, который отдаёт все поля модели в json
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


#сериализатор для товаров, с дополнительным полем category_name для удобного отображения
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_name', 'title',
            'description', 'price', 'stock_quantity',
            'image', 'is_active', 'created_at'
        )