# posts/models.py
# Defines the database models for Users, Posts, and Comments.

from django.db import models
from django.contrib.auth.models import User

# DELETED custom User model; using Django's built-in User model instead.
# REASON: current User model doesn't have hash password functionality, which is essential for authentication. 

class Post(models.Model):
    content = models.TextField() # whatever is inside the post.
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE) # this links the Post to the User... on_delete=models.CASCADE means if you delete the User, their Posts get deleted too; related_name='posts' was added to allow user to get all posts requested.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}" # modified from "return self.content[:50]"; shows who made the post and when.  
    
class Comment(models.Model):  
    text = models.TextField() # contains the comment text.
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) # links the comment to the User who made it; CASCADE deletes comments if the user is deleted.
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE) # links the comment to the Post it belongs to; CASCADE deletes comments if the post is deleted.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}" # returns a string showing who made the comment and on which post.