from django.urls import path
from django.contrib import admin

from . import views
from .views import *


urlpatterns = [
    path('resource/', views.ResourcePlanView.as_view(), name='resource'),

]