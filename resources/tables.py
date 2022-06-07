# resources/tables.py

import django_tables2 as tables
from .models import ResourcePlanItem

class ResourcePlanItemTable(tables.Table):
    class Meta:
        model = ResourcePlanItem
        template_name = "django_tables2/bootstrap.html"
        fields = ("rp", "project", "w01", "w02", )