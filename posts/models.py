from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True) #u sername's unique.. well username.
    email = models.EmailField(unique=True) # their email is unique too.
    created_at = models.DateTimeField(auto_now_add=True) # timestamp for when the user was created.

    def __str__(self):
        return self.username

class Post(models.Model):
    content = models.TextField() # whatever is inside the post.
    # this links the Post to the User... on_delete=models.CASCADE means if you delete the User, their Posts get deleted too.
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]