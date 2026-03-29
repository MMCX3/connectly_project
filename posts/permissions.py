# posts/permissions.py
# Defines custom permission classes for role-based access control (RBAC) and Privacy

from rest_framework.permissions import BasePermission, SAFE_METHODS
from singletons.logger_singleton import LoggerSingleton
from .models import Post, Comment

# fetch singleton logger for security event tracking
logger = LoggerSingleton().get_logger()

class RoleBasedAccessControl(BasePermission):
    """ 
    Enforces role restrictions based on the version 6 Flow Diagram:
    - guests cannot create content (POST).
    - only Admins can perform sensitive operations like deletion (DELETE).
    """
    
    def has_permission(self, request, view):
        """ Allows or denies access based on user role and request method. """

        # allow read-only operations to pass through to object-level checks.
        if request.method in SAFE_METHODS:
            return True
            
        # ensure that user has a profile to check roles against.
        if not hasattr(request.user, 'profile'):
            return False
            
        role = request.user.profile.role
        
        # prevent Guests from creating content (POST).
        if request.method == 'POST' and role == 'guest':
            logger.warning(f"403 Forbidden: Guest user '{request.user.username}' attempted a POST operation.")
            return False
            
        return True

    def has_object_permission(self, request, view, obj):
        """ 
        Enforces object-level permissions, particularly for DELETE operations.
        
        DELETE is restricted to admins only for Post and Comment objects.
        Like deletions (unlike actions) are intentionally excluded since they are
        user-level actions, not moderation actions.
        """

        role = request.user.profile.role if hasattr(request.user, 'profile') else 'user'
        
        # only Admins can delete Posts or Comments (content moderation).
        # Like objects are excluded — unliking is a normal user action, not admin-only.
        if request.method == 'DELETE' and isinstance(obj, (Post, Comment)) and role != 'admin':
            logger.warning(f"403 Forbidden: Non-admin '{request.user.username}' attempted to DELETE object {obj.id}.")
            return False
            
        return True


class EnforcePrivacySettings(BasePermission):
    """     
    Enforces the post privacy logic:
    - PUBLIC posts: visible to everyone.
    - PRIVATE posts: visible ONLY to the owner. 
    """

    def has_object_permission(self, request, view, obj):
        """ Enforces object-level permissions based on post privacy settings. """

        if request.method in SAFE_METHODS:
            # Check if the object has a privacy attribute (like our Post model)
            if hasattr(obj, 'privacy') and obj.privacy == 'private':
                is_owner = obj.author == request.user
                if not is_owner:
                    logger.info(f"Privacy Filter: Blocked '{request.user.username}' from viewing private Post {obj.id}.")
                return is_owner
        return True