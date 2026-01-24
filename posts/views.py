# Replaced previous code with class-based views using APIView for better structure and scalability.
# Previous code was function-based views handling GET and POST requests for Users, Posts, and Comments.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer

class UserListCreate(APIView):
    def get(self, request): # handles GET requests to retrieve all users.
        users = User.objects.all()
        serializer = UserSerializer(users, many=True) # many=True serializes multiple user objects.
        return Response(serializer.data)

    def post(self, request): # handles POST requests to create a new user.
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(): # validates the incoming data.
            serializer.save() # saves the new user to the database.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListCreate(APIView):
    def get(self, request): # handles GET requests to retrieve all posts.
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True) # many=True serializes multiple post objects.
        return Response(serializer.data)

    def post(self, request): # handles POST requests to create a new post.
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(): # validates the incoming data.
            serializer.save() # saves the new post to the database.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    def get(self, request): # handles GET requests to retrieve all comments.
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True) # many=True serializes multiple comment objects.
        return Response(serializer.data)

    def post(self, request): # handles POST requests to create a new comment.
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(): # validates the incoming data
            serializer.save() # saves the new comment to the database.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)