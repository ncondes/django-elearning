from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """Permission class that only allows teachers."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher


class IsStudent(permissions.BasePermission):
    """Permission class that only allows students."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission class that allows owners to edit, others to read."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
