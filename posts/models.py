# posts/models.py
# Defines the database models for Users, Posts, and Comments.

from django.db import models
from django.contrib.auth.models import User

# DELETED custom User model; using Django's built-in User model instead.
# REASON: custom User lacks Django’s password hashing and auth integration, making it insecure and incompatible with groups and tokens.

class Post(models.Model):
    """Represents a user post with support for text, image, and video types."""

    # post type choices for factory pattern implementation; allows for different post types in the future without changing the database schema
    POST_TYPES = [ 
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video Post'),
    ]

    title = models.CharField(max_length=200, default='Untitled')  # post title
    content = models.TextField()  # whatever is inside the post
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # type of post (text, image, video)
    metadata = models.JSONField(null=True, blank=True)  # stores additional data like file_size, duration, etc.
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)  # this links the Post to the User... on_delete=models.CASCADE means if you delete the User, their Posts get deleted too; related_name='posts' was added to allow user to get all posts requested.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a string representation of the Post, showing its type, title, and author."""
        return f"{self.post_type.title()} Post: {self.title} by {self.author.username}"  
    
class Comment(models.Model):  
    """Represents a comment made by a user on a specific post."""

    text = models.TextField() # contains the comment text.
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) # links the comment to the User who made it; CASCADE deletes comments if the user is deleted.
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE) # links the comment to the Post it belongs to; CASCADE deletes comments if the post is deleted.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a string representation of the Comment, showing who made it and on which post."""
        return f"Comment by {self.author.username} on Post {self.post.id}" 

class Like(models.Model):
    """Represents a like action by a user on a specific post."""

    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # a user can only like a specific post once
        unique_together = ('user', 'post')

    def __str__(self):
        """Returns a string representation of the Like, showing which user liked which post."""
        return f"{self.user.username} liked Post {self.post.id}"