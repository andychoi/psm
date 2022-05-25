from django.shortcuts import render

# Create your views here.
from .models import TicketSecurity
from django.http import HttpResponse

def index(request):
    tickets = TicketSecurity.objects.order_by('-created_at')[:5]
    return render(request,'ticketsecurity/index.html', {'tickets': tickets})

def ticket_by_id(request, ticket_id):
    ticket = TicketSecurity.objects.get(pk=ticket_id)
    return render(request, 'ticketsecurity/ticket_by_id.html', {'ticket':ticket})