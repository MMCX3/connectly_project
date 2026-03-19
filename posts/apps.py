# posts/apps.py
# Contains the configuration for the posts app

from django.apps import AppConfig


class PostsConfig(AppConfig):
    """ Handles the name of the app in a single place. """
    name = 'posts'
