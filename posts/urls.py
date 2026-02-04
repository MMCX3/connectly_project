# posts/urls.py
# Mapped URLs to class-based views for Users, Posts, and Comments.

# Week 3
# Replaced previous code to map class-based views for Users, Posts, and Comments.
# Previous code used in urlpatterns was for function-based views.

# Week 4
# Added PostDetailView to handle retrieving a specific post by its primary key (pk).

from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate  # imports class-based views for users, posts, and comments.

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),  # handles GET (list) and POST (create) for users
    path('posts/', PostListCreate.as_view(), name='post-list-create'),  # handles GET (list) and POST (create) for posts
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'), # handles GET for a specific post by primary key (pk)
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),  # handles GET (list) and POST (create) for comments
]