from rest_framework import permissions


class AuthorAndStaffOrReadOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        '''Аутентификация создателя объекта'''
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author or request.user.is_superuser


class CreateAnyOtherAuthenticatedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        if view.action == 'me':
            return request.user.is_authenticated
        return request.method in permissions.SAFE_METHODS

