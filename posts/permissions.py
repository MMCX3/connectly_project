# posts/permissions.py
from rest_framework.permissions import BasePermission

# class to check if the user is the author of the post and only allow them to edit/delete it.
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

# class to check if the user is in the Admin group (for RBAC)
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        # check if user is authenticated and in the Admin group
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()


# combined permission: allows access if user is either the author OR an admin
# idea is admin can: edit inappropriate content, manage posts, moderate comments, delete harmful/spam posts, while authors/reg users can only edit their own posts.
class IsPostAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # allow if user is the author or in Admin group
        is_admin = request.user.groups.filter(name='Admin').exists()
        is_author = obj.author == request.user
        return is_author or is_admin