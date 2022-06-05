"""psmprj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.http import HttpResponseRedirect
from django.conf.urls.static import static
from django.views.generic.base import TemplateView # new

# Rest API
from rest_framework import routers
from mtasks.serializers import TaskViewSet
# auth, user
from django.contrib.auth import views as auth_views
from users import views as user_views
# private media
# import private_storage.urls

router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet)

#https://stackoverflow.com/questions/67709529/django-admin-site-nav-sidebar-messed-up
# admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    re_path(r'^api/v1/', include(router.urls)),

    # Blog urls
    # path('api-blog/', include('blog.api.urls')),
    path('', include('blog.urls')),

    # Authentication Urls
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    # Resete Password Urls
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    # Change Password Urls
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'), name='password_change_done'),

    # urls handling report app  routes
    path('', include('reports.urls')),
    path('', include('psm.urls')),
    # path('', include('resources.urls')),

    # private media files
    # path('^media-private/', include(private_storage.urls)),

    # path('djrichtextfield/', include('djrichtextfield.urls')),
    # path('^markdown/', include( 'django_markdown.urls')),
#    path('oauth2/', include('django_auth_adfs.urls')),
#    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    
]

#file upload
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ADMIN:
    urlpatterns = [
#        re_path(r'^$', lambda r: HttpResponseRedirect('admin/')),   # Remove this redirect if you add custom views
        path('admin/', admin.site.urls, name="admin"),
    ] + urlpatterns

admin.site.site_title = admin.site.site_header = settings.SITE_HEADER
admin.site.index_title = settings.INDEX_TITLE

#https://levelup.gitconnected.com/django-customize-404-error-page-72c6b6277317
handler404 = 'psmprj.views.error_404'
handler500 = 'psmprj.views.error_500'
handler403 = 'psmprj.views.error_403'
handler400 = 'psmprj.views.error_400'