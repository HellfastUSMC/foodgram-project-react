from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerPostOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj == request.user


class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsOwnerOrReadOnlyAndPostAll(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'retrive', 'list', 'detail']:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAuthenticatedAndOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


#----------------------------NEW PERMISSIONS


class AllowPostOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.method == 'POST'


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class ReadAnyPostAuthChangeOwner(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user.is_authenticated and request.method == 'POST' or request.user == obj.author
