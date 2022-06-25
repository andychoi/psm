from django.urls import path
from data import views

urlpatterns = [
    path('data/', views.Dashboard.as_view(), name='dashboard')
]