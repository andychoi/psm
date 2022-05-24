from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from import_export.admin import ImportExportMixin

import datetime
from django.urls import reverse
from django.utils.html import mark_safe

from django.forms import formsets
from django.forms.models import BaseInlineFormSet

# Register your models here.
from .models import Report, Milestone, ReportDist

# Register your models here.
@admin.register(ReportDist)
class ReportDistAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'is_active')
    list_display_links = ('id', 'project')
    pass

class MilestoneFormSet(forms.models.BaseInlineFormSet):
    model = Milestone

    def __init__(self, *args, **kwargs):
        super(MilestoneFormSet, self).__init__(*args, **kwargs)
        # breakpoint()
        if not self.instance.pk: 
            self.initial = [
            {'no': 1,  'stage': 'Overall', 'description': 'Overall project status', },
            {'no': 2,  'stage': '1.Plan & Define', 'description': 'Requirements gathering', },
            {'no': 3,  'stage': '1.Plan & Define', 'description': 'Validate requirement expectations', },
            {'no': 4,  'stage': '1.Plan & Define', 'description': 'Architectural,Technical and Security Design', },
            {'no': 5,  'stage': '1.Plan & Define', 'description': 'Project Planning', },
            {'no': 6,  'stage': '1.Plan & Define', 'description': 'SOW / Contract', },
            {'no': 7,  'stage': '1.Plan & Define', 'description': 'Project Kickoff', },
            {'no': 8,  'stage': '2.Implement', 'description': 'Detail design', },
            {'no': 9,  'stage': '2.Implement', 'description': 'Development', },
            {'no': 10, 'stage': '2.Implement', 'description': 'Integration', },
            {'no': 11, 'stage': '2.Implement', 'description': 'User acceptance testing', },
            {'no': 12, 'stage': '3.Deployment', 'description': 'Go-live preparation', },
            {'no': 13, 'stage': '3.Deployment', 'description': 'Deployment', },
            {'no': 14, 'stage': '4.Post Support', 'description': 'Hyper care', },
            {'no': 15, 'stage': '4.Post Support', 'description': 'Signoff,closure', },
            ]

class MilestoneInline(admin.TabularInline):
    model = Milestone
    formset = MilestoneFormSet  
    #extra = 0   # default 3?
    ordering = ('no',)

    # hide title, https://stackoverflow.com/questions/41376406/remove-title-from-tabularinline-in-admin
    # width, https://stackoverflow.com/questions/12309788/how-to-fix-set-column-width-in-a-django-modeladmin-change-list-table-when-a-list
    class Media:
        css = {"all": ("reports/css/custom_admin.css",)}   

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0  #super(MilestoneInline, self).get_extra(request, obj, **kwargs)
        if not obj: #new create only
            extra = 15 #defined in __init__
        return extra


@admin.register(Report)
class ReportAdmin(ImportExportMixin, admin.ModelAdmin):
    class Media:
        css = {
        'all': ('reports/css/custom_admin.css',),
    }

    list_display = ('project_link', 'title', 'CBU', 'is_monthly','formatted_updated', 'status','preview_link')
    list_display_links = ('title', 'formatted_updated')
    ordering = ('-id',)

    readonly_fields = ('project_link', 'CBU', 'created_on', 'updated_on', 'created_by', 'updated_by')

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    fieldsets = (               # Edition form
        (None, {'fields': (('project', 'title', 'status', 'is_monthly'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', ), 
                            ('content_a', 'content_p', 'issue'), ),  "classes": ("stack_labels",)}),
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),('CBU','dept','div')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('project', 'title', 'status', 'is_monthly'), 
                                    ('status_o', 'status_t', 'status_b', 'status_s', ), 
                                    ('content_a', 'content_p', 'issue'),)}),
            )
        return fieldsets

    list_filter = (
        ('project', UnionFieldListFilter),
        ('CBU', RelatedDropdownFilter),
        ('div', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('status', UnionFieldListFilter),
        'updated_on'
    )

    inlines = [MilestoneInline]

    #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['content_a'].widget.attrs.update({'rows':5,'cols':40})
        form.base_fields['content_p'].widget.attrs.update({'rows':5,'cols':40})
        form.base_fields['issue'].widget.attrs.update({'rows':5,'cols':40})
        return form

    # default initial in form: starting work week
    def get_changeform_initial_data(self, request):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
        return {'title': 'Status Report - ' + start.strftime("%m/%d/%Y") }

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'


    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        if not obj.CBU:  #copy from project
            obj.CBU = obj.project.CBU
        if not obj.dept:  #copy from project
            obj.dept = obj.project.dept
        if not obj.div:  #copy from project
            obj.div = obj.project.div

        super().save_model(request, obj, form, change)

        if obj.status == 1:
            obj.project.status_o = obj.status_o
            obj.project.status_t = obj.status_t
            obj.project.status_b = obj.status_b
            obj.project.status_s = obj.status_s
            obj.project.resolution = obj.issue
            obj.project.lstrpt = obj.updated_on   #update to project last report date
            obj.project.save()

    actions = ['make_published', 'duplicate_event']

    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d  was successfully marked as published.',
            '%d  were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_event(self, request, queryset):
        for object in queryset:
            object.id = None
            object.save()
            messages.add_message(request, messages.INFO, 'Report is copied/saved')

