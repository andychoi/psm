from django.db import models
from common.models import CBU, Div, Dept, Team, ExtendUser

# Create your models here.

class TicketStatus(models.TextChoices):
 TO_DO = 'To Do'
 IN_PROGRESS = 'In Progress'
 IN_REVIEW = 'In Review'
 APPROVE = 'Approved'
 REJECT = 'Rejected'


class TicketSecurity(models.Model):
    title = models.CharField(max_length=100)
    assignee = models.ForeignKey(ExtendUser, null=True, blank = True, on_delete=models.PROTECT)
    status = models.CharField(max_length=25, choices=TicketStatus.choices, default=TicketStatus.TO_DO)
    description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)


