from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSameUserOrReadonly(BasePermission):
    def has_object_permission(self, request, view, another_user):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user == another_user
        )
