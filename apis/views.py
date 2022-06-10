from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from psm.models import Project
from common.utils import PHASE, PRIORITIES, PRJTYPE
from .serializers import ProjectSerializer

from datetime import datetime, date
import json

def _project_list(request):
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

        ltmp = request.GET.get('cbu', '')
        if len(projects) > 0 and ltmp:
            projects = projects.filter(CBUs__id=ltmp)

        ltmp = request.GET.get('pri', '')
        if ltmp:
            projects = projects.filter(priority=PRIORITIES[int(ltmp)][0])

        ltmp = request.GET.get('prg', '')
        if ltmp:
            projects = projects.filter(program__id=ltmp)

        ltmp = request.GET.get('type', '')
        if ltmp:
            projects = projects.filter(type=PRJTYPE[int(ltmp)][0])
    return projects

@csrf_exempt
def project_list(request):
    if request.method == 'GET':        
        serializer = ProjectSerializer(_project_list(request), many=True)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse(data={"RET": "E", "MSG": "unsupported method"})

@csrf_exempt
def project_detail(request, pk):
    try:
        projects = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse(status=404)        
    serializer = ProjectSerializer(projects)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def projects_update_period(request):
    tRet = {"RET": "S", "MSG": ""}
    if request.method == 'POST':
        updatedItems = 0
        try:
            body_unicode = request.body.decode('utf-8')
            print(body_unicode)
            for tObj in json.loads(body_unicode):
                print(tObj)
                try:
                    if ('id' in tObj) and ('p_plan_b' in tObj) and ('p_close' in tObj):
                        tStart = datetime.strptime(tObj['p_plan_b'], '%Y-%m-%d')
                        tClose = datetime.strptime(tObj['p_close'], '%Y-%m-%d')
                        Project.objects.filter(id=tObj['id']).update(p_plan_b=tStart, p_close=tClose)
                        updatedItems = updatedItems + 1
                except Exception as e:
                    pass
            tRet['MSG'] = "{} item(s) updated".format(updatedItems)
        except:
            tRet['MSG'] = 'Invalid request'
    else:
        tRet['MSG'] = 'Not supported method'
    return JsonResponse(data= tRet, safe=False)