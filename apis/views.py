from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from psm.models import Project
from common.utils import PHASE, PRIORITIES, PRJTYPE
from .serializers import ProjectSerializer

@csrf_exempt
def project_list(request):

    projects = []
    
    if (Project.objects.count() > 0):
        projects = Project.objects.all()

        ltmp = request.GET.get('year', '')
        if ltmp:
            projects = projects.filter(year=ltmp)

        ltmp = request.GET.get('div', '')
        if ltmp:
            projects = projects.filter(dept__div__id=ltmp)

        ltmp = request.GET.get('dep', '')
        if ltmp:
            projects = projects.filter(dept__id=ltmp)

        ltmp = request.GET.get('phase', '')
        if ltmp:
            projects = projects.filter(phase=PHASE[int(ltmp)][0])

        # ltmp = request.GET.get('cbu', '')
        # if len(projects) > 0 and ltmp:
        #     projects = projects.filter(CBU__id=ltmp)

        ltmp = request.GET.get('pri', '')
        if ltmp:
            projects = projects.filter(priority=PRIORITIES[int(ltmp)][0])

        ltmp = request.GET.get('prg', '')
        if ltmp:
            projects = projects.filter(program__id=ltmp)

        ltmp = request.GET.get('type', '')
        if ltmp:
            projects = projects.filter(type=PRJTYPE[int(ltmp)][0])

    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def project_detail(request, pk):
    try:
        projects = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse(status=404)        
    serializer = ProjectSerializer(projects)
    return JsonResponse(serializer.data, safe=False)
