# importing django routing libraries
from . import views
from django.urls import path,  re_path,  include
from rest_framework import routers

from .views import *

# app_name="psm"

urlpatterns = [
	# home page to blog
	#path('', views.IndexView.as_view(), name='project_index'),
	path('project/', views.projectList1View.as_view(), name='project_list1'),
	path('project/list2/', views.projectList2View.as_view(), name='project_list2'),
	# path('project-list2/', views.project_list2, name='project_list2'),

	path('project/chart1/', views.projectChartView.as_view(), 	name='project_chart_1'),
	path('project/chart2/', views.projectChartView2.as_view(), 	name='project_chart_2'),
	
	re_path(r'^project/(?P<pk>\d+)/$', views.projectDetail.as_view(), name='project_detail'),

	# TODO for customer to submit project request
	# path('project/<int:id>/update', views.project_update, name='project-update'),
	# path('project/<int:id>/delete', views.projectDeleteView.as_view(), name='project-delete'),

   	path('project-api/1.0/', ProjectListApiView.as_view()),
	path('api/1.0/', include('apis.urls')),

	path('project-plan/', views.projectPlanListView.as_view(), name='project_plan_index'),
	re_path(r'^project-plan/(?P<pk>\d+)/$', views.projectPlanDetailView.as_view(), name='project_plan_detail'),

]
