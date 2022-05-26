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
# from mtasks.serializers import TaskViewSet

router = routers.DefaultRouter()
# router.register(r'tasks', TaskViewSet)


urlpatterns = [
    re_path(r'^api/v1/', include(router.urls)),
#    path('oauth2/', include('django_auth_adfs.urls')),
#    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    path("accounts/", include("django.contrib.auth.urls")),  # new
    path('', TemplateView.as_view(template_name='home.html'), name='home'), # new
    # urls handling report app  routes
    path('', include('reports.urls')),
    path('', include('psm.urls')),
    path('', include("ticketSecurity.urls")),
    # path('djrichtextfield/', include('djrichtextfield.urls')),
    # path('^markdown/', include( 'django_markdown.urls')),
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
