# posts/models.py
# Defines the database models for Users, Posts, and Comments.

from django.db import models
from django.contrib.auth.models import User

# DELETED custom User model; using Django's built-in User model instead.
# REASON: custom User lacks Django’s password hashing and auth integration, making it insecure and incompatible with groups and tokens.

class Post(models.Model):

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
        return f"{self.post_type.title()} Post: {self.title} by {self.author.username}"  # shows type, title, and author
    
class Comment(models.Model):  
    text = models.TextField() # contains the comment text.
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) # links the comment to the User who made it; CASCADE deletes comments if the user is deleted.
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE) # links the comment to the Post it belongs to; CASCADE deletes comments if the post is deleted.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}" # returns a string showing who made the comment and on which post.