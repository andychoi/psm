# importing django routing libraries
from . import views
from django.urls import path,  re_path,  include
from .views import *
# from psm.views import projectList3View
#from .feeds import blogFeed

from django.contrib.auth.decorators import login_required

urlpatterns = [

	path('sap/opex-summary/', login_required(views.opex_summary.as_view()), 	name='sap_opex_summary'),

]
