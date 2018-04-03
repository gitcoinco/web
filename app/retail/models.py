from django.db import models

from economy.models import SuperModel
from github.utils import get_user
from rest_framework import serializers


class Idea(SuperModel):
    """Define the structure of idea"""
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    github_username = models.CharField(max_length=255)
    avatar_url = models.CharField(max_length=255)
    summary = models.CharField(max_length=100)
    more_info = models.CharField(max_length=500)
    looking_for_capital = models.BooleanField()
    looking_for_builders = models.BooleanField()
    looking_for_designers = models.BooleanField()
    looking_for_customers = models.BooleanField()
    capital_exists = models.BooleanField()
    builders_exists = models.BooleanField()
    designers_exists = models.BooleanField()
    customer_exists = models.BooleanField()
    posts = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    def load_avatar_url(self):
        try:            
            response = get_user(self.github_username)
            self.avatar_url = response['avatar_url']
        except Exception as e:
            print(e)

    @property
    def thread_ident(self):
        return 'idea-'+str(self.id)

class IdeaSerializer(serializers.BaseSerializer):
    """Handle serializing the Idea object."""

    class Meta:
        """Define the idea serializer metadata."""

        model = Idea
        fields = ('id', 'full_name', 'email', 'github_username', 'summary', 
        'more_info', 'looking_for_capital', 'looking_for_builders',
        'looking_for_designers', 'looking_for_customers', 'capital_exists',
        'builders_exists', 'designers_exists', 'customer_exists', 'avatar_url',
        'posts', 'likes', 'thread_ident')

    def to_representation(self, instance):
        """Provide the serialized representation of the Idea.

        Args:
            instance (Idea): The Idea object to be serialized.

        Returns:
            dict: The serialized Idea.

        """
        return {
            'id': instance.id,
            'full_name': instance.full_name,
            'email': instance.email,
            'github_username': instance.github_username,
            'summary': instance.summary,
            'more_info': instance.more_info,
            'looking_for_capital': instance.looking_for_capital,
            'looking_for_builders': instance.looking_for_builders,
            'looking_for_designers': instance.looking_for_designers,
            'looking_for_customers': instance.looking_for_customers,
            'capital_exists': instance.capital_exists,
            'builders_exists': instance.builders_exists,
            'designers_exists': instance.designers_exists,
            'customer_exists': instance.customer_exists,
            'avatar_url': instance.avatar_url,
            'posts': instance.posts,
            'likes': instance.likes,
            'thread_ident': instance.thread_ident
        }
