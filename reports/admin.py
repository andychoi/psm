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
from .models import Report, Milestone, ReportDist, ReportRisk
from psm.models import Project

# for duplicate https://stackoverflow.com/questions/437166/duplicating-model-instances-and-their-related-qrs-in-django-algorithm-for
from django.db.models.deletion import Collector
from django.db.models.fields.related import ForeignKey

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
            # {'no': 1,  'stage': 'Overall', 'description': 'Overall project status', },
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

    search_fields = ('title', 'project__title', 'content_a', 'content_p', 'issue', 'created_by__profile__name', 'updated_by__profile__name',
                    )

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    fieldsets = (               # Edition form
        (None, {'fields': (('project', 'title', 'status', 'is_monthly'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', 'progress' ), 
                            ('content_a', 'content_p', 'issue'), ),  "classes": ("stack_labels",)}),
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),('CBU','dept','div')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('project', 'title', 'status', 'is_monthly'), 
                                    ('status_o', 'status_t', 'status_b', 'status_s', 'progress'), 
                                    ('content_a', 'content_p', 'issue'),)}),
            )
        return fieldsets

    list_filter = (
        ('project', RelatedDropdownFilter),
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
    # FIXME - to-do default value from parameter (project__id)
    # https://stackoverflow.com/questions/51685472/how-to-assign-default-value-using-url-parameter-changelist-filters
    # not working randomly... trying __init__ ??
    # example: http://localhost:8000/admin/reports/report/add/?project__id=1064
    def get_changeform_initial_data(self, request):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
        project_id = request.GET.get('project__id')
        return {'title': 'Status Report - ' + start.strftime("%m/%d/%Y"),
                'project' : project_id
         }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.initial['field_name'] = 'initial_value'

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'


    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        if not obj.CBU and obj.project.CBU:  #copy from project
            obj.CBU = obj.project.CBU
        if not obj.dept and obj.project.dept:  #copy from project
            obj.dept = obj.project.dept
        if not obj.div and not obj.project.div:  #copy from project
            obj.div = obj.project.div

        super().save_model(request, obj, form, change)

        if obj.status == 1:  #if published, update project master info
            obj.project.status_o = obj.status_o
            obj.project.status_t = obj.status_t
            obj.project.status_b = obj.status_b
            obj.project.status_s = obj.status_s
            obj.project.resolution = obj.issue
            obj.project.progress = obj.progress
            obj.project.lstrpt = obj.updated_on   #update to project last report date
            obj.project.save()

    actions = ['make_published', 'duplicate_report']

    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d  was successfully marked as published.',
            '%d  were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_report(self, request, queryset):
        # https://docs.djangoproject.com/en/dev/topics/db/queries/#copying-model-instances
        # https://pypi.org/project/django-clone/#usage
        for rpt in queryset:
            old_id = rpt.id
            rpt.id = None
            rpt.title = '<new report>' 
            rpt._state.adding = True           
            rpt.save()  #adding

            old_ms = Milestone.objects.filter(report=old_id)
            # old_ms.update(report= rpt.id)     #not working, it overwrite existing.
            for m in old_ms:
                m.report = rpt
                m.pk = None
                m.save()
            messages.add_message(request, messages.INFO, rpt.title + ' - copied/saved')

    # sorting dropbox
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            kwargs["queryset"] = Project.objects.order_by('-code')
        return super(ReportAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ReportRisk)
class ReportRiskAdmin(ImportExportMixin, admin.ModelAdmin):

    # list_display = ('project_link', 'title', 'CBU', 'dept','formatted_reporton', 'state', 'status')
    list_display = ('project_link', 'title', 'get_CBU', 'get_dept','formatted_reporton', 'state', 'status')
    list_display_links = ('title', 'formatted_reporton')
    ordering = ('-id',)
    readonly_fields = ('project_link', 'updated_on', 'updated_by', 'created_on', 'created_by', 'get_CBU', 'get_dept')
    search_fields = ('title', 'project__title', 'risk', 'plan', 'owner')

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    fieldsets = (               # Edition form
        (None, {'fields': (('project', 'status'), ('report_on', 'title', ), 
                                ('risk', 'plan', ), ('deadline', 'owner', 'state', ) ),  "classes": ("stack_labels",)}),
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),('get_CBU', 'get_dept',)), 'classes': ('collapse',)}),
            # (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),('CBU','dept','div')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('project', 'status'), ('report_on', 'title',  ), 
                                ('risk', 'plan', ),('deadline', 'owner', 'state', ))}),
            )
        return fieldsets

    list_filter = (
        ('project', RelatedDropdownFilter),
        ('project__CBU', RelatedDropdownFilter),
        ('project__div', RelatedDropdownFilter),
        ('project__dept', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        'report_on'
    )

    #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['risk'].widget.attrs.update({'rows':10,'cols':40})
        form.base_fields['plan'].widget.attrs.update({'rows':10,'cols':40})
        return form

    # https://stackoverflow.com/questions/51685472/how-to-assign-default-value-using-url-parameter-changelist-filters
    # default initial in form: starting work week
    def get_changeform_initial_data(self, request):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
        project_id = request.GET.get('project__id')
        return { 'project' : project_id,
                 'title': 'Risk Report - ' + start.strftime("%m/%d/%Y")     
         }
         
    def formatted_reporton(self, obj):
        return obj.report_on.strftime("%b %Y")
    formatted_reporton.short_description = 'Report On'

    def get_CBU(self, obj):
        return obj.project.CBU.name
    get_CBU.short_description = 'CBU'

    def get_dept(self, obj):
        return obj.project.dept
    get_dept.short_description = 'Dept'


    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['duplicate_record']
    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_record(self, request, queryset):
        for qr in queryset:
            qr.id = None
            qr.title = qr.title + '..copy'
            qr.save()
            messages.add_message(request, messages.INFO, 'Report is copied/saved')

