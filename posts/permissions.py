# posts/permissions.py
# Defines custom permission classes for role-based access control (RBAC).

from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    """Allows access only to the author of the post."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdminUser(BasePermission):
    """Allows access only to users in the Admin group."""

    def has_permission(self, request, view):
        # check if user is authenticated and in the Admin group
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()


# combined permission: allows access if user is either the author OR an admin
# idea is admin can: edit inappropriate content, manage posts, moderate comments, delete harmful/spam posts, while authors/reg users can only edit their own posts.
class IsPostAuthorOrAdmin(BasePermission):
    """Allows access if the user is the post author or an Admin group member."""
    
    def has_object_permission(self, request, view, obj):
        # allow if user is the author or in Admin group
        is_admin = request.user.groups.filter(name='Admin').exists()
        is_author = obj.author == request.user
        return is_author or is_admin