from django.conf.urls import patterns, url

from apps.core import views

urlpatterns = patterns('',
    # ex: /
    url(r'^$', views.base, name='base'),
    # ex: /about
    url(r'^about/$', views.about, name='about'),
    # ex: /faq
    url(r'^faq/$', views.faq, name='faq'),
)