from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('resources/', views.ResourcePlanView.as_view(), name='resources'),
]