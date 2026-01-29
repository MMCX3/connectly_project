# posts/views.py
# Handles HTTP requests for Users, Posts, and Comments.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor

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

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor] # only authenticated users who are the post author can access

    def get(self, request, pk): # handles GET requests to retrieve a specific post by its primary key (pk).
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)
        return Response({"content": post.content})

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

class ProtectedView(APIView): # only authenticated users can access this view using valid tokens.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})