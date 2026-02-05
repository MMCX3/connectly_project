# posts/views.py
# Handles HTTP requests for Users, Posts, and Comments.

'''
WEEK 5 NOTES (difference from manual):
# Factory pattern integrated into PostListCreate (didn't create separate CreatePostView) to maintain REST principles, Week 4 security, and avoid endpoint duplication.
# LoggerSingleton added to UserListCreate (registration/errors) and PostListCreate (factory validation/creation) for centralized logging.
'''


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory

# initialize logger once at module level
logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")

class UserListCreate(APIView):

    def get_authenticators(self):
        # allow public registration (POST) but require token for viewing users (GET)
        if self.request.method == 'POST':
            return []  # no authentication for user registration
        return [TokenAuthentication()]

    def get_permissions(self):
        # allow public registration (POST) but require authentication for viewing users (GET)
        if self.request.method == 'POST':
            return []  # no permissions for user registration
        return [IsAuthenticated()]

    def get(self, request): # handles GET requests to retrieve all users.
        users = User.objects.all()
        serializer = UserSerializer(users, many=True) # many=True serializes multiple user objects.
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        try:  # error handling for logging
            # create_user method for password hashing 
            user = User.objects.create_user(
                username=username,
                password=password,  # will be automatically hashed
                email=email
            )
            logger.info(f"User created successfully: {username}")  # log successful user creation
            serializer = UserSerializer(user) # serialize the newly created user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")  # log errors during user creation
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication] # token authentication required
    permission_classes = [IsAuthenticated] # only authenticated users can access

    def get(self, request): # handles GET requests to retrieve all posts.
        logger.info("Fetching all posts")  # log posts retrieval
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True) # many=True serializes multiple post objects.
        return Response(serializer.data)

    def post(self, request): # handles POST requests to create a new post.
         # use factory pattern to create posts with validation
        try:
            post = PostFactory.create_post(
                post_type=request.data.get('post_type', 'text'),
                title=request.data.get('title', 'Untitled'),
                content=request.data.get('content', ''),
                metadata=request.data.get('metadata'),
                author=request.user  # automatically use authenticated user
            )
            logger.info(f"Post created successfully: {post.title} (type: {post.post_type})")  # log post creation
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error(f"Error creating post: {str(e)}")  # log validation errors
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error creating post: {str(e)}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication] # token authentication required
    permission_classes = [IsAuthenticated] # only authenticated users can access

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
    
class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication] # added for token-based authentication
    permission_classes = [IsAuthenticated, IsPostAuthor] # role-based access control using IsPostAuthor

    def get(self, request, pk): # modified GET method with error handling for non-existent posts.
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )