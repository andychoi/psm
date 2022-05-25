# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *
#from .feeds import blogFeed

urlpatterns = [
	# home page
	path('', views.IndexView.as_view(), name='project_index'),
	path('project/', views.projectListView.as_view(), name='project_list'),
	path('project/cbu/<CBU>/', views.projectListCBUView.as_view()),	
	path('project/year/<year>', views.projectListYearView.as_view()),	
	path('project/<pk>/', views.projectDetail.as_view(), name='project_detail'),
]
