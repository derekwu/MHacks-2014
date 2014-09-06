from django.contrib.auth.models import User, Group 
from apps.core.models import Matches 
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = User
    fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Group
    fields = ('url', 'name')

class MatchesSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Matches
    fields = ('gender', 'pref', 'money')
