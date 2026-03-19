# posts/urls.py
# Mapped URLs to class-based views for Users, Posts, and Comments

from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate, PostCommentView, PostLikeView, GoogleLogin

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/comment/<int:comment_id>/', PostCommentView.as_view(), name='post-comment-delete'), # handles DELETE for specific comment on a post
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'), 
    
    # Homework 5 Endpoints
    path('posts/<int:pk>/comments/', PostCommentView.as_view(), name='post-comments'), # handles GET and POST for specific post
    path('posts/<int:pk>/comment/', PostCommentView.as_view(), name='post-comment-single'), # added for exact syllabus match (POST /posts/{id}/comment)
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'), # handles POST and DELETE

    path('auth/google/login/', GoogleLogin.as_view(), name='google_login'),
    
]