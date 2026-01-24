# Replaced previous code to map class-based views for Users, Posts, and Comments.
# Previous code used in urlpatterns was for function-based views.

from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate  # imports class-based views for users, posts, and comments.

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),  # handles GET (list) and POST (create) for users
    path('posts/', PostListCreate.as_view(), name='post-list-create'),  # handles GET (list) and POST (create) for posts
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),  # handles GET (list) and POST (create) for comments
]