# importing django routing libraries
from . import views
from django.urls import path,  re_path,  include
from rest_framework import routers

from .views import *

# app_name="psm"

urlpatterns = [
	# home page 
	path('project/', views.IndexView, name='project_index'),
	re_path(r'project/stat/(?P<year>\d{4})?', views.get_project_chartss, name='get_project_chartss'),

	path('project/year-options/', views.get_year_options, 	name='project_year_options'),
	
    # path('project/json/', 						views.project_json_view1, 	name='project_json_view1'),
    re_path(r'project/json/get_project_charts/(?P<year>[0-9]{4})/(?P<groupby>[\w-]+)/$', 	views.get_project_charts,	name='get_project_charts'),
    # re_path(r'project/json/get_kickoff_chart/(?P<year>\d{4})?', 	views.get_kickoff_chart,	name='get_kickoff_chart'),
    # re_path(r'project/json/get_launch_chart/(?P<year>\d{4})?', 		views.get_launch_chart,		name='get_launch_chart'),
	
	
	path('project/list1', views.projectList1View.as_view(), name='project_list1'),
	path('project/list2', views.projectList2View.as_view(), name='project_list2'),
	# path('project-list2/', views.project_list2, name='project_list2'),
	path('project/list', projectList3View.as_view(), 		name="project_list"),

	path('project/chart1/', views.projectChartView.as_view(), 	name='project_chart_1'),
	path('project/chart2/', views.projectChartView2.as_view(), 	name='project_chart_2'),
	path('project/chart3/', views.project_data_view, 			name='project_chart_3'),
	

	re_path(r'^project/(?P<pk>\d+)/$', views.projectDetail.as_view(), name='project_detail'),

	# TODO for customer to submit project request
	# path('project/<int:id>/update', views.project_update, name='project-update'),
	# path('project/<int:id>/delete', views.projectDeleteView.as_view(), name='project-delete'),

   	path('project-api/1.0/', ProjectListApiView.as_view()),
	path('api/1.0/', include('apis.urls')),

	path('project-plan/', views.projectPlanListView.as_view(), 		name='project_plan_index'),
	path('project-plan/chart1/', views.projectPlanChartView.as_view(), 	name='project_plan_chart_1'),

	re_path(r'^project-plan/(?P<pk>\d+)/$', views.projectPlanDetailView.as_view(), name='project_plan_detail'),

]
