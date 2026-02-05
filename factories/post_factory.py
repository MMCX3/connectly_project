# factories/post_factory.py
# Factory pattern for centralized and validated post creation

from posts.models import Post

class PostFactory:
    @staticmethod  # static method : means that it can be called without creating a PostFactory instance
    def create_post(post_type, title, content='', metadata=None, author=None):
        # validates post_type is one of the allowed types
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError("Invalid post type.")
        
        # type-specific validation for image posts
        if post_type == 'image' and 'file_size' not in metadata:
            raise ValueError("Image posts require 'file_size' in metadata")

        
        # type-specific reqs for video posts
        if post_type == 'video' and 'duration' not in metadata:
            raise ValueError("Video posts require 'duration' in metadata")
        
        # creates and returns the post with validated data
        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author # added author field to link the post to a user; important for permissions and ownership in the app
        )