# posts/urls.py
# Mapped URLs to class-based views for Users, Posts, and Comments.

# Week 3
# Replaced previous code to map class-based views for Users, Posts, and Comments.
# Previous code used in urlpatterns was for function-based views.

# Week 4
# Added PostDetailView to handle retrieving a specific post by its primary key (pk).

from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate  # imports class-based views for users, posts, and comments.
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate, PostCommentView, PostLikeView
from posts.views import GoogleLogin

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'), 
    
    # mnew Homework 5 Endpoints
    path('posts/<int:pk>/comments/', PostCommentView.as_view(), name='post-comments'), # handles GET and POST for specific post
    path('posts/<int:pk>/comment/', PostCommentView.as_view(), name='post-comment-single'), # added for exact syllabus match (POST /posts/{id}/comment)
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'), # handles POST and DELETE

    path('auth/google/login/', GoogleLogin.as_view(), name='google_login'),
    
]