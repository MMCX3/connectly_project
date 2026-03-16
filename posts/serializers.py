# posts/serializers.py
# Maps models to JSON and enforces validation rules for API input and output.

from rest_framework import serializers
from django.contrib.auth.models import User  # changed from custom User to Django's built-in User for password hashing | Week 4 : Enhancing API Security for Connectly
from .models import Post, Comment

class UserSerializer(serializers.ModelSerializer):
    """Serializes User model data for registration and retrieval."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'date_joined'] # retained password and retained created_at to match format of other serializers, as info is not confidential/sensitive; renamed the created_at to date_joined too to match Django's User model (different from Manual Week 4)
        extra_kwargs = {'password': {'write_only': True}}  # don't return password in responses; added this for security since we have password in the fields, this ensures we can include password for user creation and 'write_only=True' hides pass from responses
    
class PostSerializer(serializers.ModelSerializer):
    """Serializes Post model data including computed like and comment counts."""

    # returns __str__ of each comment
    comments = serializers.StringRelatedField(many=True, read_only=True)
    # added fields for advanced features: like_count and comment_count to show how many likes and comments a post has without needing separate API calls; computed from related Like objects; avoids extra API calls
    like_count = serializers.SerializerMethodField()
    #computed from related Comment objects; avoids extra API calls 
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'post_type', 'metadata', 'author', 'created_at', 'comments', 'like_count', 'comment_count']
        read_only_fields = ['author']
        
    def get_like_count(self, obj):
        """Return the total number of likes for the post."""
        return obj.likes.count()

    def get_comment_count(self, obj):
        """Return the total number of comments for the post."""
        return obj.comments.count()
        
class CommentSerializer(serializers.ModelSerializer):
    """Serializes Comment model data with read-only author and post fields."""

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']
        # Made author and post read-only so we can inject them securely in the view
        read_only_fields = ['author', 'post']