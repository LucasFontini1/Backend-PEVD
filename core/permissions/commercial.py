from rest_framework.permissions import BasePermission


class IsActiveSuperUser(BasePermission):
    message = 'Acesso exclusivo da administração comercial.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.is_superuser)
