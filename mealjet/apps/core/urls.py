from django.conf.urls import patterns, url

from apps.core import views

urlpatterns = patterns('',
  # ex: /
    url(r'^$', views.base, name='base'),
)