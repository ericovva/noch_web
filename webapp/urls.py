"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from polls.views import main_page, get_post, posts_page, auth, we , blog, profile, get_blog_post,post_comment,upload_file,logout_view, oauth2login_view
from polls import views

from django.conf.urls import patterns

from django.conf import settings
#from django.views.generic.simple import redirect_to
from django.views.generic import RedirectView
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
               url(r'^post/([0-9]{1,5})', get_post),
                url(r'^$', main_page),
                       url(r'^posts/', posts_page),
                            #(r'^auth/', auth),
                                url(r'^we/', we),
                       url(r'^blog/', blog),
                       url(r'^profile/', profile),
                       url(r'^blog_post/([0-9]{1,5})', get_blog_post),
                       url(r'^register/$', views.RegisterFormView.as_view()),
                       url(r'^auth/$', views.LoginFormView.as_view()),
                       #url(r'', include('social_auth.urls')),
                       url(r'change_view_unlike/$', views.change_view_unlike, name='change_view_unlike'),
                       url(r'change_view/$', views.change_view, name='change_view'),
                       url(r'post_comment/$', views.post_comment, name='post_comment'),
                       url(r'upload_file/$', views.upload_file, name='upload_file'),
                       url(r'logout/$', views.logout_view, name='logout_view'),
                       #url(r'', include('social_auth.urls')),
                       # url(r'^login/$', RedirectView.as_view(url='/login/vk-oauth/')),
                       # url(r'^private/$', profile),
                       #url(r'^app/', include('social.apps.django_app.urls', namespace='social')),
                       #url(r'^app/oauth2login$', views.oauth2login_view),  # views for auth
                       url('', include('social.apps.django_app.urls', namespace='social')),
                       url(r'^vk/', views.vk, name = 'vk'),
                       # eta xuinya xz che
                       # url('', include('social.apps.django_app.urls', namespace='social')),
                       # url('', include('django.contrib.auth.urls', namespace='auth')),

                       
              
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
        
