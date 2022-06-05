from django.shortcuts import render
from django_tables2 import SingleTableView
from django.views.generic import ListView

# Create your views here.

from .models import ResourcePlanItem
from .tables import ResourcePlanItemTable

class ResourcePlanView(SingleTableView):
    model = ResourcePlanItem
    template_name = 'resources/res_plan.html'