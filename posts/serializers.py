# posts/serializers.py
# Maps models to JSON and enforces validation rules for API input and output.

from rest_framework import serializers
from django.contrib.auth.models import User  # changed from custom User to Django's built-in User for password hashing | Week 4 : Enhancing API Security for Connectly
from .models import Post, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email'] # deleted password field for security reasons, as well as id and created_at (which is supposed to be date_joined now since we are using User model from Django) to follow given manual from Week 4

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']  # specifies which Comment fields to include in the API response.

    def validate_post(self, value):  # custom validation to ensure the post exists before creating a comment.
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
    
class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']  # includes all Post fields plus the related comments.
