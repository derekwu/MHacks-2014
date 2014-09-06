from django.shortcuts import render

# Create your views here.

#TODO: Update the base.html navigation to use templated views
from django.contrib.auth.models import User, Group, Matches
from rest_framework import viewsets
from apps.core.serializers import UserSerializer, GroupSerializer, MatchesSerializer 


class UserViewSet(viewsets.ModelViewSet):
  """
    API endpoint that allows users to be viewed or edited.
  """
  queryset = User.objects.all()
  serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows groups to be viewed or edited.
  """
  queryset = Group.objects.all()
  serializer_class = GroupSerializer

class MatchesViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows groups to be viewed or edited.
  """
  queryset = Matches.objects.all()
  serializer_class = MatchesSerializer 
