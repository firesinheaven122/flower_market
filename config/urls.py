#подключаем django admin, маршруты и jwt-авторизацию для api
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

#подключаем view для регистрации, профиля, каталога, корзины и заказов
from users.views import RegisterView, ProfileView
from store.views import CategoryViewSet, ProductViewSet
from cart.views import CartViewSet
from orders.views import OrderViewSet

#создаём router для автоматической генерации api-маршрутов по viewset
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')

#основной список маршрутов проекта
urlpatterns = [
    path('admin/', admin.site.urls),

    #здесь подключён openapi schema и документация swagger/redoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    #маршруты для регистрации, логина и получения данных пользователя
    path('api/v1/auth/register/', RegisterView.as_view(), name='register'),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/me/', ProfileView.as_view(), name='profile'),

    #маршруты для управления корзиной пользователя
    path('api/v1/cart/', CartViewSet.as_view({'get': 'list'})),
    path('api/v1/cart/items/', CartViewSet.as_view({'post': 'add_item'})),
    path('api/v1/cart/items/<int:item_id>/', CartViewSet.as_view({'patch': 'item_detail', 'delete': 'item_detail'})),

    #маршруты каталога и заказов подключаются через router
    path('api/v1/', include(router.urls)),
]

#подключаем медиаресурсы при разработке для просмотра изображений товаров
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)