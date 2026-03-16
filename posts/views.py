# posts/views.py
# Handles HTTP requests for Users, Posts, and Comments.

# Google OAuth
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Error 

# CSRF exemption for API views 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator 

# Django and DRF imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor, IsPostAuthorOrAdmin
from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory
from rest_framework.pagination import PageNumberPagination
from .models import Post, Comment, Like

# logger and config are initialized once at module level
# reuses the same singleton instance across all views
logger = LoggerSingleton().get_logger()
logger.info('API initialized successfully.')
config = ConfigManager()


def get_post_or_404(pk):
    """Retrieve a Post by primary key, or return None if not found."""

    try:
        return Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return None

@method_decorator(csrf_exempt, name='dispatch')  # exempts CSRF check required after upgrading to dj-rest-auth 7.0.1; safe because token authentication is used instead of session-based auth where CSRF applies

class GoogleLogin(SocialLoginView):
    """Handles Google OAuth login using dj-rest-auth and allauth."""

    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://127.0.0.1:8000/"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            # attempt to process the login as usual
            return super().post(request, *args, **kwargs)
        except OAuth2Error:
            # if Google rejects the token, return a 401 error. error handling req
            return Response(
                {"error": "Invalid or expired Google token."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserListCreate(APIView):
    """Handles user registration (public) and listing all users (authenticated)."""
    
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
    """Handles listing all posts and creating new posts via the PostFactory."""
    
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
    """Handles listing all comments and creating new comments."""
    
    authentication_classes = [TokenAuthentication] # token authentication required
    permission_classes = [IsAuthenticated] # only authenticated users can access

    def get(self, request): # handles GET requests to retrieve all comments.
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True) # many=True serializes multiple comment objects.
        return Response(serializer.data)

    def post(self, request): # handles POST requests to create a new comment.
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(): # validates the incoming data
            serializer.save(author=request.user) # saves the new comment to the database; automatically assigns the logged-in user as the author of the comment for security and data integrity.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedView(APIView): 
    """
    Handles GET requests to a protected endpoint, demonstrating token authentication.
    Only authenticated users can access this view using valid tokens.
    """
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})
    
class PostDetailView(APIView):
    """
    Handles CRUD operations for individual posts:
    - GET: Retrieve a specific post (any authenticated user)
    - PUT: Update a post (only author or admin)
    - DELETE: Delete a post (only author or admin)
    """
    
    authentication_classes = [TokenAuthentication] # token-based authentication
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdmin] # role-based access control

    def get(self, request, pk): 
        """Retrieve a specific post by ID"""
        post = get_post_or_404(pk)
        if post is None:
            logger.warning(f"Post {pk} not found")
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # GET requests don't need author/admin check - any authenticated user can view
        serializer = PostSerializer(post)
        logger.info(f"Post {pk} retrieved by {request.user.username}")
        return Response(serializer.data)

    def put(self, request, pk):
        """Fully update a post (only author or admin)"""
        post = get_post_or_404(pk)
        if post is None:
            logger.warning(f"Post {pk} not found for update")
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # check if user is author or admin
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Post {pk} updated by {request.user.username}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a post (only author or admin)"""
        
        post = get_post_or_404(pk)
        if post is None:
            logger.warning(f"Post {pk} not found for deletion")
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # check if user is author or admin
        self.check_object_permissions(request, post)
        
        post.delete()
        logger.info(f"Post {pk} deleted by {request.user.username}")
        return Response(
            {"message": "Post deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
        

# HW5 advanced features: pagination for Comments
class CommentPagination(PageNumberPagination):
    """Custom pagination class for comments with configurable page size."""

    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  # sourced from ConfigManager for consistency
    page_size_query_param = 'limit'
    max_page_size = 50

class PostCommentView(APIView):
    """Handles GET (Retrieve all comments for a post) and POST (Add a comment to a post)"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Handles GET requests to retrieve paginated comments for a specific post"""
        
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        comments = post.comments.all().order_by('-created_at') # Newest first
        paginator = CommentPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk):
        """Handles POST requests to add a comment to a specific post"""
       
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # automatically assign the logged-in user and the specific post
            serializer.save(author=request.user, post=post)
            logger.info(f"Comment added to post {pk} by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostLikeView(APIView):
    """Handles POST (Like a post) and DELETE (Unlike a post)"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Handles POST requests to like a specific post"""
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            logger.info(f"User {request.user.username} liked post {pk}")
            return Response({"message": "Post liked successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Handles DELETE requests to unlike a specific post"""
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            logger.info(f"User {request.user.username} unliked post {pk}")
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)



# HW7 feature - personalized feed with pagination and sorting by date (newest first)

class FeedPagination(PageNumberPagination):
    """ 
    (1) Define the Pagination Logic
    """

    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  # sourced from ConfigManager for consistency
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedView(APIView):
    """
    (2) Define the Feed View 
    endpoint: GET /feed/
    requirement: Retrieve posts sorted by date with pagination (cite: 138, 139).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """"Handles GET requests to retrieve the paginated news feed"""
        
        # sorting: '-created_at' means descending (aka newest first) 
        posts = Post.objects.all().order_by('-created_at')
        
        # pagination: Break the results into chunks 
        paginator = FeedPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        
        # serialization
        serializer = PostSerializer(paginated_posts, many=True)
        
        # return the paginated response (includes the 'next' and 'previous' links) 
        return paginator.get_paginated_response(serializer.data)