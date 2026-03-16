# posts/admin.py
# Contains the admin configuration for the posts app.

from django.contrib import admin
from .models import Post, Comment, Like

# Registered models to make them visible and manageable in the Django Admin interface
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)