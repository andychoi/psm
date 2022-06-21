import json
from django.http import JsonResponse
from urllib.request import Request
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.db.models import Count, F, Q, Sum, Avg, Subquery, OuterRef, When, Case, IntegerField
from django.db.models.functions import ExtractYear, ExtractMonth, Coalesce
from django.core.exceptions import FieldError, FieldDoesNotExist

from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework import routers, serializers, viewsets
from .serializers import ProjectSerializer
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required

# how to permission?? https://docs.djangoproject.com/en/4.0/topics/auth/default/#permission-caching
# https://docs.djangoproject.com/en/4.0/topics/auth/default/#the-permission-required-decorator
from django.contrib.auth.decorators import permission_required
# permission check to class-based views
from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.core.paginator import Paginator

from django.urls import reverse_lazy, reverse

from django.views import generic, View
from django.http import QueryDict

# import logging   
from django.views.generic.edit import FormView
from django_filters.views import FilterView

# Create your views here.
# importing models and libraries
from common.models import Div, Dept, CBU
from common.utils import PHASE, PHASE_OPEN, PHASE_CLOSE, PHASE_BACKLOG, PHASE_WORK, STATE_ACTIVE, PRIORITIES, PRJTYPE, VERSIONS
from .models import Project, Program, ProjectPlan
from .tables import ProjectPlanTable
from reports.models import Report
# from .forms import ProjectPlanForm

from common.models import Status, STATUS, PrjType, PRJTYPE, State, STATES, Phase, PHASE, Priority, PRIORITIES, State3, STATE3, WBS, VERSIONS, Versions
# for charting
from .utils.charts import get_year_dict, generate_color_palette, colorPalette, colorPrimary, colorSuccess, colorDanger, months

#----------------------------------------------------------------------------------------------------
class ProjectListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, id=None, year=2022, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        if id:
            projects = Project.objects.get(id=id)
        else:
            if year:
                projects = Project.objects.filter(pm = request.user.id)
            else:
                projects = Project.objects.filter(year = request.user.id)
        
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        # data = {
        #     'task': request.data.get('task'), 
        #     'completed': request.data.get('completed'), 
        #     'user': request.user.id
        # }
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

# from django_tables2 import SingleTableView, SingleTableMixin

# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views


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


# @staff_member_required
def get_year_options(request):
    qs = Project.objects.values('year').order_by('-year').distinct()
    options = [project['year'] for project in qs]

    return JsonResponse({
        'options': options,
    })


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
        
        # default year
        get_def_year = date.today().year if not self.request.GET.get('year', '') else self.request.GET.get('year', '') 
        context['filterItems'].append( { "key": "YEAR", "text": "Year", "qId": "year", "selected": get_def_year
		, "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct().order_by('-year') )
        } )

        context['filterItems'].append( {
		"key": "DIV", "text": "Div", "qId": "div", "selected": self.request.GET.get('div', ''), "items": Div.objects.all()
        } )

        context['filterItems'].append( {
            "key": "DEP", "text": "Dept.", "qId": "dept", "selected": self.request.GET.get('dept', ''), "items": Dept.objects.all()
            # "key": "DEP", "text": "Dept.", "qId": "dept__name", "selected": self.request.GET.get('dept__name', ''), "items": [{ "id": x[0], "name":x[0]} for i, x in Dept.objects.all().values_list('name') ]
        } )
		
        context['filterItems'].append( {
            "key": "PHASE", "text": "Phase", "qId": "phase", "selected": self.request.GET.get('phase', '')
            # , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PHASE)]
            , "items": [{"id": x[0], "name" : x[1]} for i, x in enumerate(PHASE)]
        } )
	
        context['filterItems'].append( {
            "key": "CBU", "text": "CBU", "qId": "cbu", "selected": self.request.GET.get('cbu', '')
            , "items": CBU.objects.filter(is_active=True)
        } )

        context['filterItems'].append( {
            "key": "TYP", "text": "Type", "qId": "type", "selected": self.request.GET.get('type', '')
            , "items": [{"id": x[0], "name" : x[1]} for i, x in enumerate(PRJTYPE)]
            # , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRJTYPE)]
        } )
        context['filterItems'].append( {
            "key": "PRI", "text": "Priority", "qId": "priority", "selected": self.request.GET.get('priority', '')
            , "items": [{"id": x[0], "name": x[1]} for i, x in enumerate(PRIORITIES)]
        } )
		
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

        # generic way to get dict, filter non-existing fields in model, foreign key attribute
        q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

        if not 'year' in q.keys():
            q[ "year" ] = date.today().year

        if q: 
            qs = Project.objects.filter( **q )
                # qs = Project.objects.filter(year=self.kwargs['year']).filter( **q )
        else:
            qs = Project.objects.all()

        qs = qs.filter(is_internal=False)    #exclude internal
        if qs.count() == 0:
            return  qs      # return empty queryset

        # ltmp = self.request.GET.get('year', '')
        # if ltmp:
        #     queryset = queryset.filter(year=ltmp)

        ltmp = self.request.GET.get('div', '')
        if ltmp:
            qs = qs.filter(dept__div__id=ltmp)

        # ltmp = self.request.GET.get('dept', '')
        # if ltmp:
        #     qs = qs.filter(dept__id=ltmp)

        # ltmp = self.request.GET.get('phase', '')
        # if ltmp:
        #     qs = qs.filter(phase=PHASE[int(ltmp)][0])

        ltmp = self.request.GET.get('cbu', '')
        if ltmp:
            qs = qs.filter(CBUs__id=ltmp)

        # ltmp = self.request.GET.get('pri', '')
        # if ltmp:
        #     qs = qs.filter(priority=PRIORITIES[int(ltmp)][0])

        ltmp = self.request.GET.get('prg', '')
        if ltmp:
            qs = qs.filter(program__id=ltmp)

        # ltmp = self.request.GET.get('type', '')
        # if ltmp:
        #     qs = qs.filter(type=PRJTYPE[int(ltmp)][0])

	    # pagenation http://localhost:8000/project/?page=3
	    # https://stackoverflow.com/questions/43544701/django-pagination-from-page-to-page
	    # https://stackoverflow.com/questions/29071312/pagination-in-django-rest-framework-using-api-view
	    # req_page = self.request.GET.get('page', '')
	    # page = self.paginate_qs(qs, req_page)
	    # if req_page:
	    #     return self.paginate_qs(qs, req_page)
	
        return qs

    # def paginator(self):
    # def paginate_queryset(self, queryset, page_size):

# why not class...
# def project_list2(request):
#     project_list = Project.objects.all()
#     project_filter = ProjectFilter(request.GET, queryset=project_list)
#     return render(request, 'project/project_list2.html', {'filter': project_filter })    

class projectList2View(projectList1View): #FIXME year=date.today().year):
    template_name = 'project/project_list2.html'

class projectList3View(projectList1View):
    template_name = 'project/project_list1-new.html'

class projectChartView(projectList1View):
    template_name = 'project/project_chart.html'
class projectChartView2(projectList1View):
    template_name = 'project/project_chart2.html'

class projectChartView3(projectList1View):
    template_name = 'project/project_chart3.html'

class projectIndexView(projectList1View):
    template_name = 'project/index.html'

    # django-tables2
    # class FilteredProjectPlanView(SingleTableMixin, FilterView):
    #     model = Project
    #     table_class = ProjectPlanTable
    #     template_name = 'project/project_plan.html'
    #     filterset_class = ProjectFilter
    #     table_pagination = {"per_page": 10}


"""
이거 어떨지...
https://django-plotly-dash.readthedocs.io/en/latest/index.html


"""
# -----------------------------------------------------------------------------------------------
# https://simpleisbetterthancomplex.com/tutorial/2018/04/03/how-to-integrate-highcharts-js-with-django.html
# https://testdriven.io/blog/django-charts/
def project_json_sample2(request):
    dataset = Dept.objects \
        .values('name') \
        .annotate(completed     =Count('project', filter=Q(project__phase__gte='6')),
                  not_completed =Count('project', filter=Q(project__phase__lte='5'))) \
        .order_by('name')

    categories = list()
    completed = list()
    not_completed = list()

    for entry in dataset:
        categories.append('%s Class' % entry['name'])
        completed.append(entry['completed'])
        not_completed.append(entry['not_completed'])

    return render(request, 'project/project_chart3.html', {
        'categories': json.dumps(categories),
        'completed': json.dumps(completed),
        'not_completed': json.dumps(not_completed)
    })
    # return render(request, 'project/project_chart3.html', {'dataset': dataset})

# -----------------------------------------------------------------------------------------------
# def project_chart_sample1(request):
#     return render(request, 'project/project_chart3.html')

@login_required
# @permission_required('psm.change_project', raise_exception=True)
def project_chart_sample1_json(request):

    q =  {k:v for k, v in request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

    dataset = Dept.objects \
        .values('name') \
        .annotate(completed     =Count('project', filter=Q(project__phase__gte='6')),
                  not_completed =Count('project', filter=Q(project__phase__lte='5'))) \
        .order_by('name')
        
        
    categories = list()
    completed = list()
    not_completed = list()
    for entry in dataset:
        categories.append('%s Class' % entry['name'])
        completed.append(entry['completed'])
        not_completed.append(entry['not_completed'])

    series_completed    = {'name': 'completed',     'data': completed,      'color': 'green' }
    series_not_completed= {'name': 'not_completed', 'data': not_completed,  'color': 'red'   }

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Completion by Dept'},
        'xAxis': {'categories': categories },
        'series': [series_completed, series_not_completed]
        }
    return JsonResponse(chart)

"""
# samples: https://betterprogramming.pub/django-annotations-and-aggregations-48685994d149
# https://blog.logrocket.com/querysets-and-aggregations-in-django/
# README: https://stackoverflow.com/questions/33775011/how-to-annotate-count-with-a-condition-in-a-django-queryset
# README: https://stackoverflow.com/questions/50930002/django-annotate-sum-case-when-depending-on-the-status-of-a-field
# README: https://stackoverflow.com/questions/57524903/django-annotate-taking-a-dictionary
- django 2.0+ : The Count object has a filter parameter
    qs = LicenseType.objects.annotate(
        rel_count=Count(
            'licenserequest',
            filter=Q(licenserequest__created_at__range=(start_date, end_date))
        )
    )
- django 1.1
    qs = LicenseType.objects.annotate(
        rel_count=Sum(Case(
            When(
                licenserequest__created_at__range=(start_date, end_date),
                then=1
            ),
            default=0,
            output_field=IntegerField()
        ))
    )
# queryset to list[], tuple(), dict{},  set{}
    # qs_list = list(qs)            queryset to list -> is it okay?
    # [dict(q) for q in qs]             queryset to list
    # https://stackoverflow.com/questions/39702538/python-converting-a-queryset-in-a-list-of-tuples
"""

#-----------------------------------------------------------------------------------
# example: groupby = CBUs__name,
# return in qs or json
#-----------------------------------------------------------------------------------
def get_project_metrics(request, year=date.today().year, groupby='year' ):

    # check groupby exist
    if groupby:
        try:
            Project._meta.get_field( groupby.split('__')[0] )
        except FieldDoesNotExist:
            groupby = 'year'   #default_field

    qs = Project.objects.filter(year=year)  #, state__in=STATE_ACTIVE)

    # readme: https://docs.djangoproject.com/en/4.0/ref/models/conditional-expressions/
    # string gte, lte... not working -> use "in" instead
    # sequence is important for F calculation
    # zero if None
    # caution: many-to-many, count/sum/avg per each, CBUs__name
    metrics = {
        'completed'    : Count('pk', filter=Q(phase__in=PHASE_CLOSE)),
        # 'completed'    : Count(Case( When(phase__in=PHASE_CLOSE, then=1), output_field=IntegerField(), default=0)), -> not working
        'not_complete' : Count('pk', filter=~Q(phase__in=PHASE_CLOSE) & ~Q(state=State.CANCEL.value)),
        'in_progress'  : Count('pk', filter=~Q(phase__in=PHASE_WORK) & ~Q(state=State.CANCEL.value)),
        'not_started'  : Count('pk', filter=~Q(phase__in=PHASE_BACKLOG) & ~Q(state=State.CANCEL.value)),
        'canceled'     : Count('pk', filter=Q(state=State.CANCEL.value), default=0),
        'total'        : Count('pk'),
        'total_net'    : F('total') - F('canceled'),
        'complete_pct' : Case(When(total_net=0, then=0), default=F('completed') * 100 / F('total_net') ),
        'progress_avg' : Coalesce( Avg(  'progress', output_field=IntegerField()), 0 ),
        # 'est_cost_sum' : Coalesce( Case(When(~Q(state=State.CANCEL.value), then=F('est_cost')), output_field=IntegerField(), default=0), 0),
        'est_cost_sum' : Coalesce( Sum('est_cost', filter=~Q(state=State.CANCEL.value), output_field=IntegerField(), default=0), 0),
        'cnc_cost_sum' : Coalesce( Sum('est_cost', filter=Q(state=State.CANCEL.value),  output_field=IntegerField(), default=0), 0),  
        # for same field, causing another line
        'app_budg_sum' : Coalesce( Sum('app_budg', filter=~Q(state=State.CANCEL.value), output_field=IntegerField(), default=0), 0),
        # 'app_budg_sum' : Coalesce( Sum(  'app_budg', output_field=IntegerField()), 0 ),
    }

    # generic way - Filter the request for non-empty values and then use dictionary expansion to do the query.
    q =  {k:v for k, v in request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

    #     try:    # GET string may have wrong fields - FIXME
    #         Project._meta.get_field( item )
    #     except FieldDoesNotExist:

    if q:
        qs_result = qs.filter(**q).values( groupby ).annotate(**metrics).order_by( groupby )
    else:
        qs_result = qs.values( groupby ).annotate(**metrics).order_by( groupby )
    return qs_result
    # return qs_result | qs_cancel if qs_cancel else qs_result      # merge querysets ...error 

#-----------------------------------------------------------------------------------
@login_required
# @staff_member_required
# @permission_required('psm.change_project', raise_exception=True)
#-----------------------------------------------------------------------------------
def get_project_stat_api(request, year=date.today().year, groupby='year', mstr=None, res='json'):
    """
        Example: 
        http://localhost:8000/project/json/get_project_stat_api/2022/CBUs__name/?dept__name=ERP
        http://localhost:8000/project/json/get_project_stat_api/2023/phase/total,completed/
        http://localhost:8000/project/json/get_project_stat_api/2022/year/?dept__name=ERP
        http://localhost:8000/project/json/get_project_stat_api/2022/year/
        http://localhost:8000/project/json/get_project_stat_api/2022/
    """

    # obtain project metrics
    # dataset = get_project_metrics(request, year, groupby)

    if mstr:
        # value_str = ', '.join(['"{}"'.format(e) for e in mstr.split(',')])
        vs = [groupby, ] + mstr.split(',')
        qs = get_project_metrics(request, year, groupby).values( *tuple(vs)  ) 
    else:
        qs = get_project_metrics(request, year, groupby)

    return JsonResponse({'results': list(qs)}) if res == 'json' else qs

#-----------------------------------------------------------------------------------
@staff_member_required
#-----------------------------------------------------------------------------------
def get_project_stat_pd(request, year=date.today().year):

    import pandas as pd
    q =  {k:v for k, v in request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }
    items = Project.objects.filter(**q).values()
    df = pd.DataFrame(items)
    myDict = {
        "df": df.to_html()
    }
    return render(request, 'project/test-pandas.html', context=myDict)

#-----------------------------------------------------------------------------------
@login_required
# @staff_member_required
# @permission_required('psm.change_project', raise_exception=True)
def get_project_highchart(request, year=date.today().year, groupby='year', mstr='total_net,completed'):

    # example: http://localhost:8000/project/json/get_project_chart/2023/year/total,completed,est_cost_sum/

    dataset = get_project_stat_api(request, year, groupby, mstr, res='qs')
    if not dataset:
        return  JsonResponse( {} )

    # categories = list(dataset.values_list('dept__name', flat=True))
    categories = [ (q[groupby]) for q in dataset ]

    series = []
    for m in mstr.split(','):
        data = {
            'label': m,
            'data': [(q[ m ]) for q in dataset],
            'backgroundColor': 'green',
        }
        series.append(data)

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': f'{mstr} by {groupby}'},
        'xAxis': {'categories': categories },
        'series': series
        }

    return JsonResponse(chart)

@login_required
# @staff_member_required
# @permission_required('psm.change_project', raise_exception=True)
def get_project_chartjs(request, year=date.today().year, groupby='year', mstr='total_net,completed'):

    # example: http://localhost:8000/project/json/get_project_chart/2023/year/total,completed,est_cost_sum/

    dataset = get_project_stat_api(request, year, groupby, mstr, res='qs')
    if not dataset:
        return  JsonResponse( {} )

    # categories = list(dataset.values_list('dept__name', flat=True))
    categories = [ (q[groupby]) for q in dataset ]

    series = []
    for m in mstr.split(','):
        data = {
            'label': m,
            'data': [(q[ m ]) for q in dataset],
            'backgroundColor': 'green',
        }
        series.append(data)

    return JsonResponse({
        'title': f'Completed in {year} by {groupby}',
        'data': {
            'labels': categories,
            'datasets': [{
                'label': 'Count',
                'backgroundColor': colorPrimary,
                'data': series,
                    # [
                    # {'label': 'Completed',      'data': [(q['completed']) for q in dataset],     'backgroundColor': 'green' },
                    # {'label': 'Not Complete',   'data': [(q['not_complete']) for q in dataset],  'backgroundColor': 'red' },
                    # ]
            }]
        }
    })
        #highcharts
        # 'title': {'text': f'Completion by Dept in {year}'},
        # 'xAxis': {'categories': categories },
        # 'series': [completed, not_completed]

@staff_member_required
def get_kickoff_chart(request, year=date.today().year):
    ps = Project.objects.filter(year=year)
    grouped_ps = ps.annotate(month=ExtractMonth('a_kickoff'))\
        .values('month').annotate(count=Count('code')).values('month', 'count').order_by('month')

    data_dict = get_year_dict()

    for group in grouped_ps:
        if not group['month'] is None:
            data_dict[months[group['month']-1]] = group['count']

    return JsonResponse({
        'title': f'Kickoff in {year}',
        'data': {
            'labels': list(data_dict.keys()),
            'datasets': [{
                'label': 'Amount ($)',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(data_dict.values()),
            }]
        },
    })

# -----------------------------------------------------------------------------------
# class based view for each Project
class projectDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'psm.view_projectplan'

    model = Project
    template_name = "project/project_detail.html"
    
    # context_object_name = 'project'
    def get_context_data(self, **kwargs):
        reports = Report.objects.filter(project__in=Project.objects.filter(code=self.object.code))
        planprj = ProjectPlan.objects.filter(id=self.object.ref_plan.id) if self.object.ref_plan else None
        context = {"reports": reports, "planprj" : planprj }
        return super().get_context_data(**context)


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
    

# -----------------------------------------------------------------------------------
class projectPlanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'psm.view_projectplan'

    template_name = 'project/project_plan.html'
    model = ProjectPlan
    paginate_by = 500    #FIXME
    context_object_name = 'project_list'    
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filterItems'] = []

        get_def_year = date.today().year if not self.request.GET.get('year', '') else self.request.GET.get('year', '') 
        context['filterItems'].append( { "key": "YEAR", "text": "Year", "qId": "year", "selected": get_def_year
            , "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct().order_by('-year') )
        } )

        context['filterItems'].append( {
        	"key": "DIV", "text": "Div", "qId": "div", "selected": self.request.GET.get('div', '')
	        , "items": Div.objects.all()
        } )

        context['filterItems'].append( {
            "key": "DEPT", "text": "Dept.", "qId": "dept", "selected": self.request.GET.get('dept', '')
            , "items": Dept.objects.all()
        } )
			
        context['filterItems'].append( {
            "key": "VERSION", "text": "Version", "qId": "version", "selected": self.request.GET.get('version', '')
            , "items": [{"id": x[0], "name" : x[1]} for i, x in enumerate(VERSIONS)]
        } )

        context['filterItems'].append( {
            # "key": "CBU", "text": "CBU", "qId": "cbu", "selected": self.request.GET.get('cbu', '')
            "key": "CBU", "text": "CBU", "qId": "CBUs__name", "selected": self.request.GET.get('CBUs__name', '')
            , "items": CBU.objects.filter(is_active=True)
        } )

        context['filterItems'].append( {
            "key": "TYP", "text": "Type", "qId": "type", "selected": self.request.GET.get('type', '')
            , "items": [{"id": x[0], "name" : x[1]} for i, x in enumerate(PRJTYPE)]
        } )

        context['filterItems'].append( {
            "key": "PRI", "text": "Priority", "qId": "priority", "selected": self.request.GET.get('priority', '')
            , "items": [{"id": x[0], "name": x[1]} for i, x in enumerate(PRIORITIES)]
        } )

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
        # generic way to get dict, filter non-existing fields in model, foreign key attribute
        q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

        if not 'year' in q.keys():      # default to current year
            q[ "year" ] = date.today().year

        if q: 
            qs = Project.objects.filter( **q )
                # qs = Project.objects.filter(year=self.kwargs['year']).filter( **q )
        else:
            qs = Project.objects.all()

        if (qs.objects.count() == 0):
            return qs   # return empty qs

        ltmp = self.request.GET.get('div', '')
        if ltmp:
            qs = qs.filter(dept__div__id=ltmp)

        ltmp = self.request.GET.get('prg', '')
        if ltmp:
            qs = qs.filter(program__id=ltmp)

        # ltmp = self.request.GET.get('dept', '')
        # if ltmp:
        #     qs = qs.filter(dept__id=ltmp)
        # ltmp = self.request.GET.get('year', '')
        # if ltmp:
        #     qs = qs.filter(year=ltmp)
        # ltmp = self.request.GET.get('version', '')
        # if ltmp:
        #     qs = qs.filter(version=VERSIONS[int(ltmp)][0])
        # ltmp = self.request.GET.get('cbu', '')
        # if ltmp:
        #     qs = qs.filter(CBUs__id=ltmp)
        # ltmp = self.request.GET.get('pri', '')
        # if ltmp:
        #     qs = qs.filter(priority=PRIORITIES[int(ltmp)][0])
        # ltmp = self.request.GET.get('type', '')
        # if ltmp:
        #     qs = qs.filter(type=PRJTYPE[int(ltmp)][0])
	
        return qs


# -----------------------------------------------------------------------------------
class projectPlanChartView(projectPlanListView):
    template_name = 'project/project_chart.html'


class projectPlanDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'psm.view_projectplan'
    model = ProjectPlan
    template_name = "project/project_plan_detail.html"

    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # reports = Report.objects.filter(project=self.object)
        try:
            actual = Project.objects.get(id=self.object.released.id) if self.object.released else None
        except:
            actual = None
        context = {"actual" : actual }
        return super().get_context_data(**context)
