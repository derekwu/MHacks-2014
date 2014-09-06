#from django.conf.urls import patterns, url
#
#from apps.core import views
#from django.views.generic.base import TemplateView
#
#urlpatterns = patterns('',
#    # ex: /
#    url(r'^$',
#        TemplateView.as_view(template_name='core/base.html'),
#        name='base'),
#    # ex: /about
#    url(r'^about/$',
#        TemplateView.as_view(template_name='core/about.html'),
#        name='about'),
#    # ex: /faq
#    url(r'^faq/$',
#        TemplateView.as_view(template_name='core/faq.html'),
#        name='faq'),
#)

from django.conf.urls import url, include
from rest_framework import routers
from apps.core import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

