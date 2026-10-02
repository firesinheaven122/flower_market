#подключаем базовый permission от rest framework
from rest_framework import permissions

#permission, который разрешает чтение всем, а изменения только админу
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'ADMIN' or request.user.is_staff)
        )