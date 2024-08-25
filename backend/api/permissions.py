from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class AuthorAuthenticatedPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                (request.method in SAFE_METHODS or obj.author == request.user))
