# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *
#from .feeds import blogFeed

urlpatterns = [
	# home page
	#path('', views.IndexView.as_view(), name='index'),
	path('reports/', views.reportList.as_view(), name='report_list'),
	path('reports/<pk>/', views.reportDetail.as_view(), name='report_detail'),
]
