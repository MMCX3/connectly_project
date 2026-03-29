# posts/views.py
# Handles HTTP requests for Users, Posts, and Comments

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
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User

# for complex database filtering
from django.db.models import Q 

# for homework 9 caching layer
from django.core.cache import cache

from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer

# permissions for RBAC and Privacy
from .permissions import RoleBasedAccessControl, EnforcePrivacySettings

from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory

# logger and config are initialized once at module level.
logger = LoggerSingleton().get_logger()
logger.info('API initialized successfully.')
config = ConfigManager()


def get_post_or_404(pk):
    """ Retrieve a Post by primary key, or return None if not found. """
  
    try:
        # advanced query optimization; prefetch related data to avoid the n+1 query issues.
        return Post.objects.select_related('author').prefetch_related('comments', 'likes').get(pk=pk)
    except Post.DoesNotExist:
        return None

def invalidate_post_caches(user_id, post_id=None):
    """ 
    Invalidates relevant cache keys on post/comment/like mutations.
    
    Deletes the acting user's feed pages (1-10) and global post list cache.
    Also deletes the specific post cache if post_id is provided.
    This is more fitting than cache.clear() which wipes all users' caches.
    """
    # invalidate the acting user's feed pages
    for page in range(1, 11): 
        cache.delete(f"feed_user_{user_id}_page_{page}")

    # invalidate the global post list for this user
    cache.delete(f"all_posts_user_{user_id}")

    # invalidate the specific post detail cache if relevant
    if post_id:
        cache.delete(f"post_{post_id}_user_{user_id}")

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLogin(SocialLoginView):
    """ Handles Google OAuth login using dj-rest-auth and allauth. """

    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://127.0.0.1:8000/"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        """ Processes Google OAuth login and returns a Django token key."""

        try:
            return super().post(request, *args, **kwargs)
        except OAuth2Error:
            return Response(
                {"error": "Invalid or expired Google token."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserListCreate(APIView):
    """ Handles user registration (public) and listing all users (authenticated). """
    
    def get_authenticators(self):
        """ Returns no authenticator for POST (registration); token auth for other methods. """

        if self.request.method == 'POST':
            return []  
        return [TokenAuthentication()]

    def get_permissions(self):
        """ Returns no permissions for registration; IsAuthenticated for all other methods. """
       
        if self.request.method == 'POST':
            return []  
        return [IsAuthenticated()]

    def get(self, request): 
        """ Handles GET requests to retrieve all registered users. """

        # query optimization: select related profile.
        users = User.objects.select_related('profile').all()
        serializer = UserSerializer(users, many=True) 
        return Response(serializer.data)

    def post(self, request):
        """ Handles POST requests to register a new user (with hashed password). """

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
        # 1. unique cache key for the global post list per user
        cache_key = f"all_posts_user_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        # 2. check cache first
        if cached_data:
            logger.info(f"posts cache hit for {request.user.username}")
            response = Response(cached_data)
            response['X-Cache-Status'] = 'HIT'
            return response

        logger.info("fetching all posts")  
        
        # 3. cache miss -> query database
        # filter out private posts from other users on the general list too!
        # adv query optimization - select_related and prefetch_related applied.

        posts = Post.objects.select_related('author').prefetch_related('comments', 'likes').filter(
            Q(privacy='public') | Q(author=request.user)
        ).order_by('-created_at')
        
        serializer = PostSerializer(posts, many=True) 
        response_data = serializer.data

        # 4. store in cache for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        logger.info(f"posts cache miss for {request.user.username}")
        
        response = Response(response_data)
        response['X-Cache-Status'] = 'MISS'
        return response

    def post(self, request): 
        try:
            post = PostFactory.create_post(
                post_type=request.data.get('post_type', 'text'),
                title=request.data.get('title', 'Untitled'),
                content=request.data.get('content', ''),
                metadata=request.data.get('metadata'),
                author=request.user  
            )
            
            privacy_setting = request.data.get('privacy', 'public')
            if privacy_setting in ['public', 'private']:
                post.privacy = privacy_setting
                post.save()

            # cache invalidation: clear cache so both feed and global list update
            cache.clear()
            logger.info("cache cleared due to new post creation.")

            logger.info(f"post created successfully: {post.title} (type: {post.post_type})")  
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.error(f"error creating post: {str(e)}")  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"unexpected error creating post: {str(e)}")
            return Response({'error': 'an error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentListCreate(APIView):
    """ Handles listing all comments and creating new comments. """
    
    authentication_classes = [TokenAuthentication] 
    # roleBasedAccessControl prevents Guests from commenting.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl] 

    def get(self, request): 
        """ Handles GET requests to retrieve all comments. """

        # advanced query optimization applied.
        # filter out comments on private posts that don't belong to the requesting user.
        comments = Comment.objects.select_related('author', 'post').filter(
            Q(post__privacy='public') | Q(post__author=request.user))
        serializer = CommentSerializer(comments, many=True) 
        return Response(serializer.data)

    def post(self, request): 
        """ Handles POST requests to create a new comment (logged-in user is automatically set as author). """

        # privacy check: prevent commenting on a private post via the global comment endpoint.
        post_id = request.data.get('post')
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.privacy == 'private' and post.author != request.user:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save(author=request.user, post=post) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """ Handles CRUD operations for individual posts. """
    
    authentication_classes = [TokenAuthentication] 

    # layered permissions to handle Privacy (GET) and Admin-only logic (DELETE).
    permission_classes = [IsAuthenticated, RoleBasedAccessControl, EnforcePrivacySettings] 

    def get(self, request, pk): 
        """ Handles GET requests to retrieve a specific post (privacy settings enforced). """

        # 1. unique cache key per user per post
        cache_key = f"post_{pk}_user_{request.user.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Post {pk} cache HIT for {request.user.username}")
            response = Response(cached_data)
            response['X-Cache-Status'] = 'HIT'
            return response

        # 2. cache miss -> retrieve from database
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # enforce privacy check manually if DRF doesn't catch it on get().
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post)
        logger.info(f"Post {pk} retrieved by {request.user.username}")

        # 3. store in cache for 5 minutes
        cache.set(cache_key, serializer.data, timeout=300)

        response = Response(serializer.data)
        response['X-Cache-Status'] = 'MISS'
        return response

    def delete(self, request, pk):
        """ Handles DELETE requests to remove a post, restricted to admin only. """

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
    """ Handles the pagination class for comments with settings from ConfigManager. """
   
    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  
    page_size_query_param = 'limit'
    max_page_size = 50

class PostCommentView(APIView):
    """ Handles listing and creating comments for a specific post, with privacy checks. """

    authentication_classes = [TokenAuthentication]
    # RoleBasedAccessControl prevents Guests from commenting.
    permission_classes = [IsAuthenticated, RoleBasedAccessControl, EnforcePrivacySettings]

    def get(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        # privacy - non-owners cannot read comments on a private post.
        self.check_object_permissions(request, post)

        # advanced query optimization
        comments = post.comments.select_related('author').all().order_by('-created_at') 
        paginator = CommentPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        # privacy - non-owners cannot comment on a private post.
        self.check_object_permissions(request, post)   

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)

            # cache invalidation - clear cache so feed comment_count updates
            cache.clear()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, comment_id):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = post.comments.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # check object permissions; only admin can delete
        self.check_object_permissions(request, comment)

        comment.delete()

        # cache invalidation - clear cache so feed comment_count updates
        cache.clear()
        logger.info(f"comment {comment_id} on post {pk} deleted by {request.user.username}")
        return Response({"message": "comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class PostLikeView(APIView):
    # handles liking and unliking a post, with privacy checks to prevent liking private posts by non-owners.

    authentication_classes = [TokenAuthentication]
    # added EnforcePrivacySettings to prevent liking private posts!!

    permission_classes = [IsAuthenticated, RoleBasedAccessControl, EnforcePrivacySettings]

    def post(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        # enforce privacy check before allowing the like
        self.check_object_permissions(request, post)

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            # cache invalidation - clear cache so feed like_count updates
            cache.clear()
            return Response({"message": "post liked successfully."}, status=status.HTTP_201_CREATED)
        return Response({"error": "you have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_post_or_404(pk)
        if post is None:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        # only enforce privacy here ; unliking is a user action, not an admin-only delete
        if post.privacy == 'private' and post.author != request.user:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            # cache invalidation - clear cache so feed like_count updates
            cache.clear()
            return Response({"message": "post unliked successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "you have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)

class FeedPagination(PageNumberPagination):
    """ Handles pagination for user feed (posts) with settings from ConfigManager. """

    page_size = config.get_setting('DEFAULT_PAGE_SIZE')  
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedView(APIView):
    """ Handles the user feed with caching for performance optimization. """
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Handles GET requests to retrieve the paginated feed; uses cache to reduce database load. """ 

        # 1. create a unique cache key for this user and the page they are on.
        page_number = request.query_params.get('page', 1)
        cache_key = f"feed_user_{request.user.id}_page_{page_number}"
        
        # 2. check cache first.
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Feed cache HIT for {request.user.username} (page {page_number})")

            # create the response and add a custom header to prove it's from the cache!
            response = Response(cached_data)
            response['X-Cache-Status'] = 'HIT'
            return response

        # 3. cache miss -> query the database.
        # advanced database filtering for privacy;
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
        logger.info(f"Feed cache MISS for {request.user.username} (page {page_number})")
        
        # create the response and add a custom header to prove that it hit the database!
        response = Response(response_data)
        response['X-Cache-Status'] = 'MISS'
        
        return response