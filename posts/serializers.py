from rest_framework import serializers
from .models import User, Post, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at'] # specifies which User fields to include in the API response.

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True) # shows related comments as strings; many=True allows multiple comments; read_only=True means this field is not for input.

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments'] # includes all Post fields plus the related comments.

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at'] # specifies which Comment fields to include in the API response.

    def validate_post(self, value): # custom validation to ensure the post exists before creating a comment.
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value): # custom validation to ensure the author exists before creating a comment.
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value