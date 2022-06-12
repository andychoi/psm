from django.shortcuts import render
from django.template import RequestContext

#https://stackoverflow.com/questions/17662928/django-creating-a-custom-500-404-error-page

def error_404(request, exception):
        data = { 'custom_page_not_found' }
        return render(request,'errors/404.html', status=404)

def error_500(request, exception=None):
        data = { 'bad_request' }
        return render(request,'errors/404.html', status=500)

def error_403(request, exception=None):
        data = { 'permission_denied' }
        return render(request,'errors/403.html', status=403)

def error_400(request, exception=None):
        data = { 'bad_request' }
        return render(request,'errors/404.html', status=400)

