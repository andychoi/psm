from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from psm.models import Project
from .serializers import ProjectSerializer

@csrf_exempt
def project_list(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def project_detail(request, pk):
    try:
        projects = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse(status=404)        
    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse(serializer.data, safe=False)
