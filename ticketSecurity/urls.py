from django.urls import path
from . import views

urlpatterns = [
    path('security/', views.index, name='ticketsecurity_index'),
    path('security/<int:ticket_id>', views.ticket_by_id, name='ticket_by_id')
]