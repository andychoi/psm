from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from import_export.admin import ImportExportMixin
from django.http import HttpResponseRedirect
# from django.conf import settings
from psmprj import env

import datetime
from django.urls import reverse
from django.utils.html import mark_safe

from django.forms import formsets, formset_factory
from django.forms.models import BaseInlineFormSet


# README issue with import/export https://github.com/crccheck/django-object-actions/issues/67
from django_object_actions import DjangoObjectActions

# Register your models here.
from .models import Report, Milestone, ReportRisk
from psm.models import Project

# for duplicate https://stackoverflow.com/questions/437166/duplicating-model-instances-and-their-related-qrs-in-django-algorithm-for
from django.db.models.deletion import Collector
from django.db.models.fields.related import ForeignKey


#queryset filter with list of values: https://stackoverflow.com/questions/9304908/how-can-i-filter-a-django-query-with-a-list-of-values

# Register your models here.
# @admin.register(ReportDist)
# class ReportDistAdmin(admin.ModelAdmin):
#     list_display = ('id', 'project', 'is_active')
#     list_display_links = ('id', 'project')
#     pass

# class MilestoneFormSet(forms.models.BaseInlineFormSet):
class MilestoneFormSet(forms.models.BaseInlineFormSet):
    model = Milestone

    def __init__(self, *args, **kwargs):
        super(MilestoneFormSet, self).__init__(*args, **kwargs)
        # breakpoint()
        if not self.instance.pk: 
            self.initial = [
            # {'no': 1,  'stage': 'Overall', 'description': 'Overall project status', },
            {'no': 2,  'stage': '1.Plan & Define',  'description': 'Requirements gathering', },
            {'no': 3,  'stage': '1.Plan & Define',  'description': 'Validate requirement expectations', },
            {'no': 4,  'stage': '1.Plan & Define',  'description': 'Architectural,Technical and Security Design', },
            {'no': 5,  'stage': '1.Plan & Define',  'description': 'Project Planning', },
            {'no': 6,  'stage': '1.Plan & Define',  'description': 'SOW / Contract', },
            {'no': 7,  'stage': '1.Plan & Define',  'description': 'Project Kickoff', },
            {'no': 8,  'stage': '2.Implement',      'description': 'Detail design', },
            {'no': 9,  'stage': '2.Implement',      'description': 'Development', },
            {'no': 10, 'stage': '2.Implement',      'description': 'Integration', },
            {'no': 11, 'stage': '2.Implement',      'description': 'User acceptance testing', },
            {'no': 12, 'stage': '3.Deployment',     'description': 'Go-live preparation', },
            {'no': 13, 'stage': '3.Deployment',     'description': 'Deployment', },
            {'no': 14, 'stage': '4.Post Support',   'description': 'Hyper care', },
            {'no': 15, 'stage': '4.Post Support',   'description': 'Signoff,closure', },
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
            extra = 14 #defined in __init__
        return extra

    def has_changed(self):
        """ Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will get validated and saved."""
        return True

#https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields
@admin.register(Report)
class ReportAdmin(DjangoObjectActions, admin.ModelAdmin):
    class Media:
        css = { 'all': ('reports/css/custom_admin.css',), }

    # form = ReportAdminForm  

    list_display = ('project_link', 'title', 'cbu_list', 'get_dept','formatted_updated', 'status', 'is_monthly','preview_link')
    list_display_links = ('title', 'formatted_updated')
    list_editable = ('status',)
    ordering = ('-id',)
    autocomplete_fields = [ 'project' ]
    readonly_fields = ('project_link', 'created_on', 'updated_on', 'created_by', 'updated_by')
    #'CBUs', 'dept', 
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
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),
                        # ('CBUs','dept',)
            ), 'classes': ('collapse',)}),
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
        ('project__CBUs', RelatedDropdownFilter),
        ('project__dept', RelatedDropdownFilter),
        ('project__dept__div', RelatedDropdownFilter),
        # ('div', RelatedDropdownFilter),
        # ('dept', RelatedDropdownFilter),
        ('status', UnionFieldListFilter),
        'updated_on'
    )

    inlines = [MilestoneInline]

    # inline initial force to save -> FIXME... 
    #https://stackoverflow.com/questions/50175561/initial-data-for-django-admin-inline-formset-is-not-saved
    #     # def save_related(self, request, form, formsets, change):
    #     for formset in formsets:
    #         if formset.model == Milestone:
    #             instances = formset.save(commit=False)
    #             report = form.instance
    #             # for added_milestone in formset.new_objects:
    #             # for deleted_milestone in formset.deleted_objects:
    #     super(ReportAdmin, self).save_related(request, form, formsets, change)
    # def save_formset(self, request, form, formset, change):
    #     if formset == formset_factory(MilestoneFormSet):
    #         instances = formset.save(commit=False)
    #         for idx, instance in instances:
    #             if instance.pk == None: # add
    #                 instance.no = idx
    #             else:
    #                 # check `change` for is changed or deleted
    #                 pass
    #         formset.save_m2m()

        # for idx, inline_form in formset.forms:
        #     # if inline_form.has_changed():
        # super().save_formset(request, form, formset, change)

    #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['content_a'].widget.attrs.update({'rows':5,'cols':40})
        form.base_fields['content_p'].widget.attrs.update({'rows':5,'cols':40})
        form.base_fields['issue'].widget.attrs.update({'rows':5,'cols':40})
        form.base_fields['project'].widget.attrs.update({'style': 'width: 400px'})
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

    def cbu_list(self, obj):
        return " ,".join(p.name for p in obj.project.CBUs.all())
    cbu_list.short_description = 'CBUs'

    def get_dept(self, obj):
        return obj.project.dept
    get_dept.short_description = 'Dept'

    # object-function
    def send_report(self, request, obj):
        from psmprj.utils.mail import send_mail_async as send_mail, split_combined_addresses, combine_to_addresses
        # to display name: from_email = "Name <info@domain.com>"

        from django.template import Context
        from django.template.loader import get_template
        from django.core.mail import EmailMultiAlternatives
        from .views import reportDetail

        email_receiver = [ combine_to_addresses( split_combined_addresses(obj.project.recipients_to) ) ]
        # email_receiver = env("EMAIL_TEST_RECEIVER", "test@localhost.localdomain,").split(",")
        
        if obj.project.email_active and email_receiver:  
            # converted HTML rendering using https://templates.mailchimp.com/resources/inline-css/
            htmly = get_template('reports/report_email.html')
            context = { 
                'object'    : obj, 
                'milestone' : Milestone.objects.filter(report=obj.pk).order_by('no') }

            # Bootstrap Email https://bootstrapemail.com/docs/introduction    
            html_content = htmly.render(context)
            # msg.attach_alternative(html_content, "text/html")
            # breakpoint()
            email_sender   = obj.project.pm.email if (obj.project.pm.email) else env("EMAIL_TEST_SENDER", "test@localhost.localdomain")
            no_mails = send_mail(
                subject=obj.title,
                message='The report is in HTML format.',
                html_message=html_content,
                from_email=email_sender, 
                recipient_list=email_receiver,
                fail_silently=False,
            )
            # breakpoint()
            messages.add_message(request, messages.INFO, 'Email job running!')

    send_report.label = "Send Email"  

    # object-function
    def goto_project(self, request, obj):
        return HttpResponseRedirect(f'/admin/psm/project/{obj.project.id}')
        # from django.shortcuts import redirect
        # redirect('/admin/psm/project/%s' % obj.project.pk)

    def preview(self, request, obj):
        return HttpResponseRedirect(reverse('report_detail', args=[obj.pk]))
    preview.attrs = {'target': '_blank'}

    def email(self, request, obj):
        return HttpResponseRedirect(reverse('report_email', args=[obj.pk]))
    email.attrs = {'target': '_blank'}

    def past_reports(self, request, obj):
        return HttpResponseRedirect(f'/admin/reports/report/?project__id__exact={obj.project.id}')

    def clone(self, request, obj):
        old_id = obj.id     #obj.id = new.id
        new = obj
        new.id = None
        new.title = '<new report>' 
        new._state.adding = True           
        new.save()  #adding
        # update many-to-many after save
        # new.CBUs.set(obj.project.CBUs.all())
        new.save()
        # clone milestones
        old_ms = Milestone.objects.filter(report=old_id)
        for m in old_ms:
            m.report = new
            m.pk = None
            m.save()
        messages.add_message(request, messages.INFO, "Report is cloned to #%i with title %s" % (new.id, new.title))
        return HttpResponseRedirect(f'/admin/reports/report/{new.id}')
    clone.label = "Clone+"  


    change_actions = ('preview', 'send_report', 'email', 'clone', 'past_reports', 'goto_project')
    
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        #redundant, but need for filtering in admin list
        # obj.dept = obj.project.dept

        super().save_model(request, obj, form, change)

        #FIXME manytomany : queryset list(q1) == list(q2)
        #needs to have "id" before many-to-many relations can be used
        # if (not obj.CBUs.exists()): 
        #     obj.CBUs.set(obj.project.CBUs.all())
        #     obj.save()


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
    list_display = ('project_link', 'title', 'cbu_list', 'get_dept','formatted_reporton', 'state', 'status')
    list_display_links = ('title', 'formatted_reporton')
    list_editable = ("state", 'status',)
    ordering = ('-id',)
    readonly_fields = ('project_link', 'updated_on', 'updated_by', 'created_on', 'created_by', 'cbu_list', 'get_dept')
    search_fields = ('title', 'project__title', 'risk', 'plan', 'owner')
    autocomplete_fields = [ 'project' ]

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    fieldsets = (               # Edition form
        (None, {'fields': (('project', 'status'), ('report_on', 'title', ), 
                                ('risk', 'plan', ), ('deadline', 'owner', 'state', ) ),  "classes": ("stack_labels",)}),
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by'),('cbu_list', 'get_dept',)), 'classes': ('collapse',)}),
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
        ('project__CBUs', RelatedDropdownFilter),  #FIXME many to many OK
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
        form.base_fields['project'].widget.attrs.update({'style': 'width: 400px'})
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

    def cbu_list(self, obj):
        return " ,".join(p.name for p in obj.project.CBUs.all())
    cbu_list.short_description = 'CBUs'

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

    # FIXME TODO
    # return to callback URL if page comes from project
    # https://stackoverflow.com/questions/1339845/redirect-on-admin-save
    # http://localhost:8000/admin/psm/project/953/
    # def response_add(self, request, obj, post_url_continue="../%s/"):
    #     if '_continue' not in request.POST:
    #         return HttpResponseRedirect("%s%s" % ("/admin/psm/project/?project__id__exact=",obj.project.pk))
    #     else:
    #         return super(ReportRiskAdmin, self).response_add(request, obj, post_url_continue)

    # def response_change(self, request, obj):
    #     if '_continue' not in request.POST:
    #         return HttpResponseRedirect("/")
    #     else:
    #         return super(ReportRiskAdmin, self).response_change(request, obj)
