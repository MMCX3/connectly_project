# posts/permissions.py
from rest_framework.permissions import BasePermission

# class to check if the user is the author of the post and only allow them to edit/delete it.
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
