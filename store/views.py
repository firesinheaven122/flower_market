from rest_framework import viewsets, filters
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Гости и клиенты видят только активные товары
        if not (self.request.user.is_authenticated and self.request.user.role == 'ADMIN'):
            queryset = queryset.filter(is_active=True)
            
        # Фильтрация по категории через GET параметр ?category_id=1
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset