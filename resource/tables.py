# resource/tables.py
import django_tables2 as tables

from psm.models import Project
from .models import ResourcePlan, RPPlanItem

class ResourcePlanTable(tables.Table):
    mm_value = tables.Column(orderable=False, verbose_name='M/M')
    action = tables.TemplateColumn(
        '<a href="{{ record.get_edit_url }}" class="btn btn-info"><i class="fa fa-edit"></i></a>', orderable=False)

    class Meta:
        model = ResourcePlan
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'tag_final_value']


# class ProjectTable(tables.Table):
#     # tag_final_value = tables.Column(orderable=False, verbose_name='Price')
#     action = tables.TemplateColumn(
#         '<button class="btn btn-info add_button" data-href="{% url "ajax_add" instance.id record.id %}">Add!</a>',
#         orderable=False
#     )

#     class Meta:
#         model = Project
#         template_name = 'django_tables2/bootstrap.html'
#         fields = ['code', 'title', 'est_cost']

class RPPlanItemTable(tables.Table):

    mm = tables.Column(orderable=False, verbose_name='M/M')
    action = tables.TemplateColumn('''
            <button data-href="{% url "ajax_modify" record.id "add" %}" class="btn btn-success edit_button"><i class="fa fa-arrow-up"></i></button>
            <button data-href="{% url "ajax_modify" record.id "remove" %}" class="btn btn-warning edit_button"><i class="fa fa-arrow-down"></i></button>
            <button data-href="{% url "ajax_modify" record.id "delete" %}" class="btn btn-danger edit_button"><i class="fa fa-trash"></i></button>
    ''', orderable=False)

    class Meta:
        model = RPPlanItem
        template_name = "django_tables2/bootstrap.html"
        fields = ("rp", "project", "w01", "w02", )




