from urllib.request import Request
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.db.models import Q
from django.http import Http404
# from django.core.paginator import Paginator
from rest_framework import generics

# import logging   
# Create your views here.


# importing models and libraries
from django.shortcuts import render
from pyparsing import common
from .models import Project, Program
from common.models import Div, Dept, CBU
from common.utils import PHASE, PRIORITIES, PRJTYPE
from django.views import generic
from django.http import QueryDict

# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views

class IndexView(generic.ListView):
    template_name = 'project/index.html'
    context_object_name = 'latest_project_list'

    def get_queryset(self):
        """Return the last five project."""
        return Project.objects.order_by('-last_modified')[:5]

# https://django-filter.readthedocs.io/ -> error, don't use
# https://django-tables2.readthedocs.io/ -> this is better, but...
# https://mattsch.com/2021/05/28/django-django_tables2-and-bootstrap-table/
# https://bootstrap-table.com/
#https://stackoverflow.com/questions/57085070/using-django-filter-with-class-detailview
#https://stackoverflow.com/questions/24305854/simple-example-of-how-to-use-a-class-based-view-and-django-filter
#https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/#dynamic-filtering
#https://stackoverflow.com/questions/51121661/django-filter-multiple-values
# class based views for project -> for selected project

# https://stackoverflow.com/questions/57050000/how-to-return-pagination-with-django-framework
# class projectListView(generic.ListView):


# https://django-filter.readthedocs.io/en/stable/guide/usage.html#declaring-filters
# https://stackoverflow.com/questions/59480402/how-to-use-django-filter-with-a-listview-class-view-for-search
# https://velog.io/@daylee/Django-filter-function-based-views

from django_filters.views import FilterView
from .filters import ProjectFilter
# class projectList2View(FilterView):
# class projectList2View(generic.ListView):
#     model = Project
#     template_name = 'project/project_list2.html'
#     context_object_name = 'project_list2'
#     # filterset_class = ProjectFilter

#     def get_queryset(self):
#         # return Project.objects.all()[:25]
#         qs = self.model.objects.all()
#         project_filtered_list = ProjectFilter(self.request.GET, queryset=qs)
#         return project_filtered_list.qs

class projectList1View(generic.ListView):
    template_name = 'project/project_list1.html'
    model = Project
    paginate_by = 500    #FIXME
    context_object_name = 'project_list'    
    
    # def get(self, request, *args, **kwargs):
    #     form = self.form_class(initial=self.initial)
    #     return render(request, self.template_name, {'form': form})    
    # pagination fix: https://stackoverflow.com/questions/61090168/why-is-my-pagination-not-working-django
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filterItems'] = []

        context['filterItems'].append( {
            "key": "YEAR", "text": "Year", "qId": "year"
            , "selected": self.request.GET.get('year', '')
            , "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct().order_by('-year') )
        } )

        context['filterItems'].append( {
            "key": "DIV", "text": "Div", "qId": "div"
            , "selected": self.request.GET.get('div', '')
            , "items": Div.objects.all()
        } )

        context['filterItems'].append( {
            "key": "DEP", "text": "Dept.", "qId": "dep"
            , "selected": self.request.GET.get('dep', '')
            , "items": Dept.objects.all()
        } )
    
        context['filterItems'].append( {
            "key": "PHASE", "text": "Phase", "qId": "phase"
            , "selected": self.request.GET.get('phase', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PHASE)]
        } )

        context['filterItems'].append( {
            "key": "CBU", "text": "CBU", "qId": "cbu"
            , "selected": self.request.GET.get('cbu', '')
            , "items": CBU.objects.all()
        } )

        context['filterItems'].append( {
            "key": "TYP", "text": "Type", "qId": "type"
            , "selected": self.request.GET.get('type', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRJTYPE)]
        } )

        context['filterItems'].append( {
            "key": "PRI", "text": "Priority", "qId": "pri"
            , "selected": self.request.GET.get('pri', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRIORITIES)]
        } )
        
        context['filterItems'].append( {
            "key": "PRG", "text": "Program", "qId": "prg"
            , "selected": self.request.GET.get('prg', '')
            # , "items": Project.objects.values('program').distinct()
            , "items": Program.objects.all()
        } )

        #https://stackoverflow.com/questions/59972694/django-pagination-maintaining-filter-and-order-by
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy
        
        return context


        # queryset = self.get_queryset().annotate(
        #     first_name_len=Length('user__first_name'),
        #     last_name_len=Length('user__last_name')
        # ).filter(
        #     first_name_len__gt=0,
        #     last_name_len__gt=0,
        # ).filter(
        #     **parameters
        # ).order_by(
        #     '-created'
        # )


    def get_queryset(self):
        # self.request has GET parameter
        # # self.year = get_object_or_404(self.year, name=self.kwargs['year'])
        # # return Project.objects.filter(year=self.year).order_by('dept')
        # queryset = Project.objects.filter(year=self.kwargs['year'])

        queryset = Project.objects.all()
        ltmp = self.request.GET.get('year', '')
        if ltmp:
            queryset = queryset.filter(year=ltmp)

        ltmp = self.request.GET.get('div', '')
        if ltmp:
            queryset = queryset.filter(div__id=ltmp)

        ltmp = self.request.GET.get('dep', '')
        if ltmp:
            queryset = queryset.filter(dept__id=ltmp)

        ltmp = self.request.GET.get('phase', '')
        if ltmp:
            queryset = queryset.filter(phase=PHASE[int(ltmp)][0])

        ltmp = self.request.GET.get('cbu', '')
        if ltmp:
            queryset = queryset.filter(CBUs__id=ltmp)

        ltmp = self.request.GET.get('pri', '')
        if ltmp:
            queryset = queryset.filter(priority=PRIORITIES[int(ltmp)][0])

        ltmp = self.request.GET.get('prg', '')
        if ltmp:
            queryset = queryset.filter(program__id=ltmp)

        ltmp = self.request.GET.get('type', '')
        if ltmp:
            queryset = queryset.filter(type=PRJTYPE[int(ltmp)][0])

        # pagenation http://localhost:8000/project/?page=3
        # https://stackoverflow.com/questions/43544701/django-pagination-from-page-to-page
        # https://stackoverflow.com/questions/29071312/pagination-in-django-rest-framework-using-api-view
        # req_page = self.request.GET.get('page', '')
        # page = self.paginate_queryset(queryset, req_page)
        # if req_page:
        #     return self.paginate_queryset(queryset, req_page)
        
        return queryset

    # def paginator(self):
    # def paginate_queryset(self, queryset, page_size):

# why not class...
# def project_list2(request):
#     project_list = Project.objects.all()
#     project_filter = ProjectFilter(request.GET, queryset=project_list)
#     return render(request, 'project/project_list2.html', {'filter': project_filter })    

class projectList2View(projectList1View):
    template_name = 'project/project_list2.html'

class projectChartView(projectList1View):
    template_name = 'project/project_chart.html'

class projectChartView2(projectList1View):
    template_name = 'project/project_chart2.html'

class projectChartPlanView(projectList1View):
    template_name = 'project/project_chart.html'

# class based view for each Project
class projectDetail(generic.DetailView):
	model = Project
	template_name = "project/project_detail.html"
	context_object_name = 'project_detail'

	# def get_context_data(self, **kwargs): --> SSG??
	# 	context = super().get_context_data(**kwargs)    
	# 	context['milestone'] = Milestone.objects.filter(Project=self.object).order_by('no')
	# 	return context

# how to pass multiple object
# -> https://stackoverflow.com/questions/42250375/django-passing-multiple-objects-to-templates-but-nothing-in-there

