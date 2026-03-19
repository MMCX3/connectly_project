# posts/views.py
# handles HTTP requests for Users, Posts, and Comments.

# Google OAuth.
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Error 

# CSRF exemption for API views.
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator 

# Django and DRF imports.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User

# for complex database filtering.
from django.db.models import Q 

# for homework 9 caching layer.
from django.core.cache import cache

from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer

# permissions for RBAC and Privacy.
from .permissions import RoleBasedAccessControl, IsOwnerOrAdmin, EnforcePrivacySettings

from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory

# logger and config are initialized once at module level.
logger = LoggerSingleton().get_logger()
logger.info('API initialized successfully.')
config = ConfigManager()


def get_post_or_404(pk):
    # retrieve a Post by primary key, or return None if not found.
    try:
        # advanced query optimization; prefetch related data to avoid thw n+1 query issues.
        return Post.objects.select_related('author').prefetch_related('comments', 'likes').get(pk=pk)
    except Post.DoesNotExist:
        return None


@method_decorator(csrf_exempt, name='dispatch')
class GoogleLogin(SocialLoginView):

    # handles Google OAuth login using dj-rest-auth and allauth.
    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://127.0.0.1:8000/"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except OAuth2Error:
            return Response(
                {"error": "Invalid or expired Google token."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserListCreate(APIView):
    # handles user registration (public) and listing all users (authenticated).
    
    def get_authenticators(self):
        if self.request.method == 'POST':
            return []  
        return [TokenAuthentication()]

    def get_permissions(self):
        if self.request.method == 'POST':
            return []  
        return [IsAuthenticated()]

    def get(self, request): 

        # query optimization: select related profile.

        users = User.objects.select_related('profile').all()
        serializer = UserSerializer(users, many=True) 
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        try:  
            user = User.objects.create_user(
                username=username,
                password=password,  
                email=email
            )
            logger.info(f"User created successfully: {username}")  
            serializer = UserSerializer(user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")  
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    # handles listing all posts and creating new posts via the PostFactory.
    
    authentication_classes = [TokenAuthentication] 

    # added RoleBasedAccessControl to block Guests from POSTing.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl] 

    def get(self, request): 
        logger.info("Fetching all posts")  
        
        # filter out private posts from other users on the general list too!
        # query optimization: select_related and prefetch_related applied.

        posts = Post.objects.select_related('author').prefetch_related('comments', 'likes').filter(
            Q(privacy='public') | Q(author=request.user)
        ).order_by('-created_at')
        
        serializer = PostSerializer(posts, many=True) 
        return Response(serializer.data)

    def post(self, request): 
        try:
            post = PostFactory.create_post(
                post_type=request.data.get('post_type', 'text'),
                title=request.data.get('title', 'Untitled'),
                content=request.data.get('content', ''),
                metadata=request.data.get('metadata'),
                author=request.user  
            )
            
            # safely set privacy if provided in request, otherwise defaults to public.

            privacy_setting = request.data.get('privacy', 'public')
            if privacy_setting in ['public', 'private']:
                post.privacy = privacy_setting
                post.save()

            # clear the cache when a new post is made so the feed updates.

            cache.clear()
            logger.info("cache cleared due to new post creation.")

            logger.info(f"Post created successfully: {post.title} (type: {post.post_type})")  
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.error(f"Error creating post: {str(e)}")  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Unexpected error creating post: {str(e)}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentListCreate(APIView):
    # handles listing all comments and creating new comments.
    
    authentication_classes = [TokenAuthentication] 
    # roleBasedAccessControl prevents Guests from commenting.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl] 

    def get(self, request): 

        # advanced query optimization applied.
        comments = Comment.objects.select_related('author', 'post').all()
        serializer = CommentSerializer(comments, many=True) 
        return Response(serializer.data)

    def post(self, request): 
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save(author=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    # handles CRUD operations for individual posts.
    
    authentication_classes = [TokenAuthentication] 

    # layered permissions to handle Privacy (GET), Admin/Owner logic (PUT), and Admin-only logic (DELETE).
    permission_classes = [IsAuthenticated, RoleBasedAccessControl, EnforcePrivacySettings, IsOwnerOrAdmin] 

    def get(self, request, pk): 
        # retrieve a specific post by ID.
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # enforce privacy check manually if DRF doesn't catch it on get().
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post)
        logger.info(f"Post {pk} retrieved by {request.user.username}")
        return Response(serializer.data)

    def put(self, request, pk):

        # fully update a post (only author or admin).
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
            
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # clear cache on update.
            cache.clear()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # delete a post (only admin).
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
            
        self.check_object_permissions(request, post)
        
        post.delete()
        # clear cache on delete.
        cache.clear()
        logger.info(f"Post {pk} deleted by {request.user.username}")
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        

class CommentPagination(PageNumberPagination):
    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  
    page_size_query_param = 'limit'
    max_page_size = 50

class PostCommentView(APIView):
    authentication_classes = [TokenAuthentication]

    # RoleBasedAccessControl prevents Guests from commenting.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl]

    def get(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # advanced query optimization.
        comments = post.comments.select_related('author').all().order_by('-created_at') 
        paginator = CommentPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostLikeView(APIView):
    authentication_classes = [TokenAuthentication]

    # RoleBasedAccessControl prevents Guests from liking/unliking.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl]

    def post(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({"message": "Post liked successfully."}, status=status.HTTP_201_CREATED)
        return Response({"error": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)


class FeedPagination(PageNumberPagination):
    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 1. create a unique cache key for this user and the page they are on.
        page_number = request.query_params.get('page', 1)
        cache_key = f"feed_user_{request.user.id}_page_{page_number}"
        
        # 2. check cache first.
        cached_data = cache.get(cache_key)
        if cached_data:

            # create the response and add a custom header to prove it's from the cache!
            response = Response(cached_data)
            response['X-Cache-Status'] = 'HIT'
            return response

        # 3. cache miss -> query the database.
        # advanced database filtering for privac;
        # advanced query optimization: fetching related data to drastically reduce db load.
        posts = Post.objects.select_related('author').prefetch_related('comments', 'likes').filter(
            Q(privacy='public') | Q(author=request.user)
        ).order_by('-created_at')
        
        paginator = FeedPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(paginated_posts, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data

        # 4. store the result in the cache for 5 minutes (300 seconds).
        cache.set(cache_key, response_data, timeout=300)

        # create the response and add a custom header to prove thatit hit the database!
        response = Response(response_data)
        response['X-Cache-Status'] = 'MISS'
        
        return response