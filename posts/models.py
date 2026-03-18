# posts/models.py
# defines the database models for Users, Posts, and Comments.

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# DELETED custom User model; using Django's built-in User model instead.
# REASON: custom User lacks Django’s password hashing and auth integration, making it insecure and incompatible with groups and tokens.

class UserProfile(models.Model):
# UserProfile for RBAC extends the built-in User model to include RBAC roles without breaking auth.
    
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
        ('guest', 'Guest User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} Profile ({self.role})"

# automatically creates a UserProfile whenever a new User is created.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Post(models.Model):
    # represents a user post with support for text, image, and video types.

    # post type choices for factory pattern implementation;
    # allows for different post types in the future without changing the database schema

    POST_TYPES = [ 
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video Post'),
    ]

    # privacy choices for RBAC implementation; allows users to set the visibility of their posts.

    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    title = models.CharField(max_length=200, default='Untitled')  # post title
    content = models.TextField()  # whatever is inside the post
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # type of post (text, image, video)
    
    # privacy field added here.
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    
    metadata = models.JSONField(null=True, blank=True) 
    # stores additional data like file_size, duration, etc.

    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    # this links the Post to the User... on_delete=models.CASCADE means if you delete the User, their Posts get deleted too; related_name='posts' was added to allow user to get all posts requested.

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #this returns a string representation of the Post, showing its type, title, and author.
        return f"[{self.privacy.upper()}] {self.post_type.title()} Post: {self.title} by {self.author.username}"  
    

class Comment(models.Model):  
    # represents a comment made by a user on a specific post.

    text = models.TextField()
    # contains the comment text.

    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    # links the comment to the User who made it; CASCADE deletes comments if the user is deleted.

    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    # links the comment to the Post it belongs to; CASCADE deletes comments if the post is deleted.

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #returns a string representation of the Comment, showing who made it and on which post.
        return f"Comment by {self.author.username} on Post {self.post.id}" 


class Like(models.Model):
    # represents a like action by a user on a specific post.

    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # a user can only like a specific post once.
        unique_together = ('user', 'post')

    def __str__(self):
        # returns a string representation of the Like, showing which user liked which post.
        return f"{self.user.username} liked Post {self.post.id}"