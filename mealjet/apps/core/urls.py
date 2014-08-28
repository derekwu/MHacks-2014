from django.conf.urls import patterns, url

from apps.core import views
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    # ex: /
    url(r'^$',
        TemplateView.as_view(template_name='core/base.html'),
        name='base'),
    # ex: /about
    url(r'^about/$',
        TemplateView.as_view(template_name='core/about.html'),
        name='about'),
    # ex: /faq
    url(r'^faq/$',
        TemplateView.as_view(template_name='core/faq.html'),
        name='faq'),
)