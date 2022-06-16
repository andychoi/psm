from urllib.request import Request
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import ProjectSerializer

# how to permission?? https://docs.djangoproject.com/en/4.0/topics/auth/default/#permission-caching
# https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-permission-required-decorator
from django.contrib.auth.decorators import permission_required
# permission check to class-based views
from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.core.paginator import Paginator
from rest_framework import generics
from django.urls import reverse_lazy
from django.urls import reverse

from django.views import generic, View
from django.http import QueryDict
from django.shortcuts import render
from pyparsing import common

# import logging   
from django.views.generic.edit import FormView
from django_filters.views import FilterView

# Create your views here.
# importing models and libraries
from common.models import Div, Dept, CBU
from common.utils import PHASE, PRIORITIES, PRJTYPE, VERSIONS
from .models import Project, Program, ProjectPlan
from .tables import ProjectPlanTable
# from .forms import ProjectPlanForm

class ProjectListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        projects = Project.objects.filter(pm = request.user.id)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Project with given todo data
        '''
        data = {
            'task': request.data.get('task'), 
            'completed': request.data.get('completed'), 
            'user': request.user.id
        }
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# from django_tables2 import SingleTableView, SingleTableMixin

# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views

class IndexView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'psm.view_project'
    template_name = 'project/index.html'
    context_object_name = 'latest_project_list'

    def get_queryset(self):
        """Return the last five project."""
        return Project.objects.order_by('-updated_on')[:5]

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

# While DjangoModelPermissions limits the user's permission for interacting with a model (all the instances), 
# DjangoObjectPermissions limits the interaction to a single instance of the model (an object). 
# To use DjangoObjectPermissions you'll need a permission backend that supports object-level permissions. We'll look at django-guardian.


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

class projectList1View(PermissionRequiredMixin, generic.ListView):
    permission_required = 'psm.view_project'

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
		"key": "YEAR", "text": "Year", "qId": "year", "selected": self.request.GET.get('year', '')
		, "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct().order_by('-year') )
        } )
        context['filterItems'].append( {
		"key": "DIV", "text": "Div", "qId": "div", "selected": self.request.GET.get('div', '')
		, "items": Div.objects.all()
        } )

        context['filterItems'].append( {
            "key": "DEP", "text": "Dept.", "qId": "dep", "selected": self.request.GET.get('dep', '')
        	, "items": Dept.objects.all()
        } )
		
        context['filterItems'].append( {
            "key": "PHASE", "text": "Phase", "qId": "phase", "selected": self.request.GET.get('phase', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PHASE)]
        } )
	
        context['filterItems'].append( {
            "key": "CBU", "text": "CBU", "qId": "cbu", "selected": self.request.GET.get('cbu', '')
            , "items": CBU.objects.filter(is_active=True)
        } )

        context['filterItems'].append( {
            "key": "TYP", "text": "Type", "qId": "type", "selected": self.request.GET.get('type', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRJTYPE)]
        } )
	# context['filterItems'].append( {
	#     "key": "PRI", "text": "Priority", "qId": "pri", "selected": self.request.GET.get('pri', '')
	#     , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRIORITIES)]
	# } )
		
        context['filterItems'].append( {
            "key": "PRG", "text": "Program", "qId": "prg", "selected": self.request.GET.get('prg', '')
            # , "items": Project.objects.values('program').distinct()
            , "items": Program.objects.filter(is_active=True)  # all()
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
        queryset = []
        if (Project.objects.count() > 0):
            # queryset = Project.objects.all()
            queryset = Project.objects.filter(is_internal=False)    #exclude internal
            ltmp = self.request.GET.get('year', '')
            if ltmp:
                queryset = queryset.filter(year=ltmp)

            ltmp = self.request.GET.get('div', '')
            if ltmp:
                queryset = queryset.filter(dept__div__id=ltmp)

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

    # django-tables2
    # class FilteredProjectPlanView(SingleTableMixin, FilterView):
    #     model = Project
    #     table_class = ProjectPlanTable
    #     template_name = 'project/project_plan.html'
    #     filterset_class = ProjectFilter
    #     table_pagination = {"per_page": 10}
    
# class based view for each Project
class projectDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'psm.view_projectplan'

    model = Project
    template_name = "project/project_detail.html"
    context_object_name = 'project'


class projectCreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'psm.add_projectplan'
    model = Project
    template_name = "project/project_detail.html"
    context_object_name = 'project'
    # fields = ['title', 'description']

# class projectUpdateView(generic.UpdateView):
# 	model = Project
# 	template_name = "project/project_detail.html"
# 	context_object_name = 'project'
#     # fields = ['title', 'description'] 

#https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms
# TODO for customer to submit project request
# @login_required
# @permission_required('psm.change_project', raise_exception=True)
# def project_update(request, id):
#     project = Project.objects.get(id=id)

#     if request.method == 'POST':
#         form = ProjectPlanForm(instance=project)  # prepopulate the form with an existing project
#         print(form.errors)
#         if form.is_valid():
#             # update the existing `project` in the database
#             form.save()
# 	    # redirect to the detail page of the `project` we just updated
#             return redirect('project_detail', pk=project.id)
#         else:
#             form = ProjectPlanForm(instance=project)
    
#     context = {
# 	"form":form
#     }
#     return render(request, "project/project_update.html", context)
    

class projectPlanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'psm.view_projectplan'

    template_name = 'project/project_plan.html'
    model = ProjectPlan
    paginate_by = 500    #FIXME
    context_object_name = 'project_list'    
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filterItems'] = []

        context['filterItems'].append( {
            "key": "YEAR", "text": "Year", "qId": "year", "selected": self.request.GET.get('year', '')
             , "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct().order_by('-year') )
        } )

        context['filterItems'].append( {
        	"key": "DIV", "text": "Div", "qId": "div", "selected": self.request.GET.get('div', '')
	    , "items": Div.objects.all()
        } )

        context['filterItems'].append( {
		"key": "DEP", "text": "Dept.", "qId": "dep", "selected": self.request.GET.get('dep', '')
		, "items": Dept.objects.all()
        } )
			
        context['filterItems'].append( {
		"key": "VERSION", "text": "Version", "qId": "version", "selected": self.request.GET.get('version', '')
		, "items": [{"id": i, "name": x[1]} for i, x in enumerate(VERSIONS)]
        } )

        context['filterItems'].append( {
		"key": "CBU", "text": "CBU", "qId": "cbu", "selected": self.request.GET.get('cbu', '')
		, "items": CBU.objects.filter(is_active=True)
        } )

        context['filterItems'].append( {
		"key": "TYP", "text": "Type", "qId": "type", "selected": self.request.GET.get('type', '')
		, "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRJTYPE)]
        } )

        # context['filterItems'].append( {
        #     "key": "PRI", "text": "Priority", "qId": "pri", "selected": self.request.GET.get('pri', '')
        #     , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRIORITIES)]
        # } )

        context['filterItems'].append( {
        	"key": "PRG", "text": "Program", "qId": "prg", "selected": self.request.GET.get('prg', '')
        	, "items": Program.objects.filter(is_active=True)  # all()
        } )

        #https://stackoverflow.com/questions/59972694/django-pagination-maintaining-filter-and-order-by
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy
			
        return context

    def get_queryset(self):
        queryset = []
        if (ProjectPlan.objects.count() > 0):
            queryset = ProjectPlan.objects.all()
        ltmp = self.request.GET.get('year', '')
        if ltmp:
            queryset = queryset.filter(year=ltmp)

        ltmp = self.request.GET.get('div', '')
        if ltmp:
            queryset = queryset.filter(dept__div__id=ltmp)

        ltmp = self.request.GET.get('dep', '')
        if ltmp:
            queryset = queryset.filter(dept__id=ltmp)

        ltmp = self.request.GET.get('version', '')
        if ltmp:
            queryset = queryset.filter(version=VERSIONS[int(ltmp)][0])

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
	
        return queryset

class projectPlanDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'psm.view_projectplan'
    model = ProjectPlan
    template_name = "project/project_plan_detail.html"
    context_object_name = 'project'

