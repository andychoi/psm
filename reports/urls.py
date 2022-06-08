# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *
#from .feeds import blogFeed

from django.contrib.auth.decorators import login_required

urlpatterns = [
	# home page
	#path('', views.IndexView.as_view(), name='index'),
	path('reports/', login_required(views.reportList.as_view()), name='report_list'),
	path('report-email/<pk>/', login_required(views.reportEmail.as_view()), name='report_email'),
	path('reports/<pk>/', login_required(views.reportDetail.as_view()), name='report_detail'),
	path('report-risks/', login_required(views.reportRisks.as_view()), name='report_risks'),
]
