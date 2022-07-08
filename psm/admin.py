import sys
import inspect
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from import_export.admin import ImportExportMixin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from datetime import date

from adminfilters.multiselect import UnionFieldListFilter
from django.contrib.admin import FieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from django import forms

from django.utils.html import format_html
from django.utils.html import mark_safe
from pyparsing import null_debug_action
from common.dates import previous_business_day, add_business_days

from common.models import Action3, ReqTypes, Versions, CBU, State, Phase, Dept, Team
from .models import Project, ProjectRequest,  ProjectDeliverable, ProjectDeliverableType, Strategy, Program
from reviews.models import  Review
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.contrib.auth import get_user_model, get_permission_codename
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ngettext
from django.shortcuts import redirect

from users.models import Profile

# README issue with import/export https://github.com/crccheck/django-object-actions/issues/67
from django_object_actions import DjangoObjectActions
from dal import autocomplete    #https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#overview

# https://stackoverflow.com/questions/54514324/how-to-register-inherited-sub-class-in-admin-py-file-in-django
# GOOD: https://stackoverflow.com/questions/241250/single-table-inheritance-in-django
# READ: https://chelseatroy.com/2018/08/26/proxy-models-in-django-an-example-and-a-use-case/

@admin.register(Strategy)
class StrategyAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'updated_on','is_active', 'goto_project')
    list_display_links = ('name',)
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_on', 'created_by')

    class Meta:
        model = Strategy
        import_id_fields = ('id',)

    change_actions = ('goto_project', )
    def goto_project(self, obj):
        return mark_safe(f'<a href="{reverse("admin:psm_project_changelist")}?strategy__id__exact={obj.id}"> Links </a>')

@admin.register(Program)
class ProgramAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'lead', 'startyr', 'is_active', 'goto_project')
    list_display_links = ('name', 'lead')
    search_fields = ('name',)
    ordering = ('-startyr', 'name',)
    autocomplete_fields = ( 'lead', )
    class Meta:
        model = Program
        import_id_fields = ('id',)

    # object-function in object admin page
    change_actions = ('goto_project', )
    # object-function
    def goto_project(self, obj):
        return mark_safe(f'<a href="{reverse("admin:psm_project_changelist")}?program__id__exact={obj.id}"> Links </a>')

    changelist_actions = ['redirect_to_export', 'redirect_to_import']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"

# to make textarea format
class ProjectDeliverableModelForm( forms.ModelForm ):
    desc = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = ProjectDeliverableType
        fields = '__all__'

@admin.register(ProjectDeliverableType)
class ProjectDeliverableTypeAdmin(ImportExportMixin, admin.ModelAdmin):
    form = ProjectDeliverableModelForm
    class Meta:
        import_id_fields = ('id',)

class ProjectDeliverableInline(admin.TabularInline):
    model = ProjectDeliverable
    extra = 0
    class Media:
        css = {"all": ("psm/css/custom_admin.css",)}

# ----------------------------------------------------------------------------------------------------------------
class ProjectRequestResource(resources.ModelResource):
    pm_name     = fields.Field(attribute='pm',     widget=ForeignKeyWidget(model=Profile, field='name'))
    CBUpm_name  = fields.Field(attribute='CBUpm',  widget=ForeignKeyWidget(model=Profile, field='name'))
    cbu_names       = fields.Field(attribute='CBUs',    widget=ManyToManyWidget(model=CBU, separator=',', field='name'), )
    dept_name  = fields.Field(attribute='dept', widget=ForeignKeyWidget(model=Dept, field='name'), )
    team_name  = fields.Field(attribute='team', widget=ForeignKeyWidget(model=Team, field='name'), )    
    strategy_names  = fields.Field(attribute='strategy',widget=ManyToManyWidget(model=Strategy, separator=',', field='name'), )
    class Meta:
        model = ProjectRequest
        fields = ( 'id', 'year', 'version', 'code', 'title', 'asis', 'tobe', 'objective', 'consider', 'quali', 'quant',
            # 'pm', 'pm__name',  
            # 'CBUpm', 'CBUpm__name',  
            # 'CBU', 'cbu_names', 
            'pm_name', 'CBUpm_name', 'cbu_names',  
            'strategy_names', 'program__name', 
            'est_cost', 'resource', 'type', 'size', 'priority', 'dept', 'dept_name', 'team', 'team_name', 'dept__div', 'dept__div__name',  
            'p_ideation','p_plan_b','p_kickoff','p_design_b','p_dev_b','p_uat_b','p_launch','p_close',
        )
        export_order = fields

class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ('__all__')
        widgets = {
            'pm': autocomplete.ModelSelect2(url='profile-staff-autocomplete')    # common.adminfilters.py
        }

    # https://stackoverflow.com/questions/41613079/how-to-give-the-information-about-request-user-to-clean-method
    # def __init__(self, request=None, *args, **kwargs):
    #     self.user = request.user
    #     super().__init__(*args, **kwargs)
        
    # validation logic here in admin form -> check version field access
    def clean_version(self):
        super().clean()

        #TODO how to get requestor???
        # ver = self.cleaned_data.get("version")
        # if ver == Versions.V20.value and not self.user.has_perm('access_projectrequest_v20') or \
        #     ver == Versions.V21.value and not self.user.has_perm('access_projectrequest_v21'):
        #     # messages.add_message(self.request, messages.ERROR, f"You don't have permission to change on version {ver}" )
        #     raise ValidationError(_('No access to this version'), code='invalid')

# ----------------------------------------------------------------------------------------------------------------
@admin.register(ProjectRequest)
class ProjectRequestAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    form = ProjectRequestForm
    resource_class = ProjectRequestResource
    class Meta:
        import_id_fields = ('id',)
        exclude = ()
    class Media:
        css = { 'all': ('psm/css/custom_admin.css',), }

    search_fields = ('id', 'code', 'title', 'asis', 'tobe', 'objective', 'consider', 'pm__name', 'CBUpm__name', 'CBUs__name')
    list_display = ('version', 'code',  'title', 'pm', 'dept', 'CBU_names', 'est_cost', 'view' )    #CBU many to many
    list_display_links = ('code', 'title')
    list_editable = ("version", )
    list_filter = (
        ('year',        DropdownFilter),
        ('version',     UnionFieldListFilter),
        ('CBUs',        RelatedDropdownFilter),   
        ('dept',        RelatedDropdownFilter),
        ('dept__div',   RelatedDropdownFilter),
        ('team',        RelatedDropdownFilter),
        ('priority',    UnionFieldListFilter),
    )
    ordering = ['version', '-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by',  'image_tag_asis', 'image_tag_tobe', 'released' )
    autocomplete_fields = ['pm', 'CBUs', 'strategy', 'CBUpm', 'program', 'team']
    plan_fields = [ ('title', 'year', 'version' ), 
                    ('type', 'size', 'priority'), 
                    ('strategy', 'program', 'is_agile'),
                    ('pm', 'team'),
                    ('CBUs', 'CBUpm'),
                    ('asis', 'img_asis', 'image_tag_asis'),
                    ('tobe', 'img_tobe', 'image_tag_tobe'),
                    ('objective', 'consider'),
                    ('quali', 'quant'),
                    ('est_cost', 'resource'),
                    ('p_ideation','p_plan_b','p_kickoff','p_design_b','p_dev_b','p_uat_b','p_launch','p_close'), ('released',)
                ]
    fieldsets = (               # Edition form
        (None,  {'fields': plan_fields 
                , "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'),  ), 'classes': ('collapse',)}),
    )

    def view(self, obj):
        return mark_safe(f"<a class='btn btn-outline-success p-1 btn-sm adminlist' style='color:#000' href='/project-plan/{obj.id}'>View</a>")

    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.plan_fields  }), )

    # tip initial default version set
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectRequestAdmin, self).get_form(request, obj, **kwargs)
        #FIXME if read-only due to permission
        if hasattr(form, 'base_fields') and len(form.base_fields) != 0:
            if obj is None:
                form.base_fields['version'  ].initial = Versions.V10.value
            form.base_fields['asis'     ].widget.attrs.update({'rows':7,'cols':80})
            form.base_fields['tobe'     ].widget.attrs.update({'rows':7,'cols':80})
            form.base_fields['objective'].widget.attrs.update({'rows':5,'cols':30})
            form.base_fields['consider' ].widget.attrs.update({'rows':5,'cols':30})
            form.base_fields['quali'    ].widget.attrs.update({'rows':3,'cols':30})
            form.base_fields['quant'    ].widget.attrs.update({'rows':3,'cols':30})
            form.base_fields['resource' ].widget.attrs.update({'rows':2,'cols':30})

            # cols - not working
            form.base_fields['asis'     ].widget.attrs['style'] = 'width: 35em;'
            form.base_fields['tobe'     ].widget.attrs['style'] = 'width: 35em;'
            form.base_fields['objective'].widget.attrs['style'] = 'width: 25em;'
            form.base_fields['consider' ].widget.attrs['style'] = 'width: 25em;'
            form.base_fields['quali'    ].widget.attrs['style'] = 'width: 25em;'
            form.base_fields['quant'    ].widget.attrs['style'] = 'width: 25em;'
            form.base_fields['resource' ].widget.attrs['style'] = 'width: 35em;'
        return form


    # TODO - permission override
    def has_change_permission(self, request, obj=None):
        # if obj :
        #     # return True
        #     #check permission on version
        #     if obj.version == Versions.V20.value and not request.user.has_perm('access_projectrequest_v20') or \
        #        obj.version == Versions.V21.value and not request.user.has_perm('access_projectrequest_v21'):
        #         return False    # You do not have access to version 21 (Unplanned approved') 
        #     return True

        return super(ProjectRequestAdmin, self).has_change_permission(request, obj)

    # TODO - limit access to list for specific user group?? like CBU
    def get_queryset(self, request):
        return ProjectRequest.objects.all()
        # if request.user.is_superuser:
        #     return ProjectRequest.objects.all()
        
        # try:
        #     return ProjectRequest.objects.filter(pm = request.user.profile)
        # except:
        #     return ProjectRequest.objects.none()        


    actions = ['move_to_final_version', 'move_to_11_version', 'move_to_12_version', 'release_to_actual_batch' ]
    def queryset_update_version(self, request, queryset, version):
        updated = queryset.update(version=version)
        self.message_user(request, ngettext(
            '%d  was successfully moved to version %s',
            '%d  were successfully moved to version %s',
            updated,
        ) % (updated, version), messages.SUCCESS)        
        messages.add_message(request, messages.INFO, ' moved to final version')

    @admin.action(description="Move to final version", permissions=['change'])
    def move_to_final_version(self, request, queryset):
        self.queryset_update_version(request, queryset, Versions.V20.value)

    @admin.action(description="Move to working version 11", permissions=['change'])
    def move_to_11_version(self, request, queryset):
        self.queryset_update_version(request, queryset, Versions.V11.value)

    @admin.action(description="Move to working version 12", permissions=['change'])
    def move_to_12_version(self, request, queryset):
        self.queryset_update_version(request, queryset, Versions.V12.value)

    def has_approve_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('approve', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    @admin.action(description="Release to Actual Project", permissions=['approve'])
    def release_to_actual_batch(self, request, queryset):
        for obj in queryset:
            if obj.version in [ Versions.V20.value, Versions.V21.value ]:
                self.copy_to_project(request, obj)
            else:
                messages.add_message(request, messages.ERROR, "You can release from BAP or UPN" )

    # object action FIXME
    change_actions = ('release_to_actual',)
    def release_to_actual(self, request, obj):
        self.copy_to_project(request, obj)
    release_to_actual.label = "Release to Actual"  

    # 
    def copy_to_project(self, request, obj):
        if not request.user.has_perm('psm.approve_projectrequest'):
            messages.add_message(request, messages.ERROR, "You don't have permission to release project" )
            return
        else:
            # allow only source verion from 20,21
            if not obj.version in [ Versions.V20.value, Versions.V21.value ]:
                messages.add_message(request, messages.ERROR, "You cannot release project from this version" )
                return

        # check if project file exist
        if Project.objects.filter(title=obj.title).exists():
            messages.add_message(request, messages.ERROR, mark_safe(u"Project name: %s has already exist." % obj.title))
        else:
            # check if actual prj is created
            prj = Project.objects.filter(ref_plan=obj)
            if prj.exists():
                messages.add_message(request, messages.ERROR, mark_safe(f'Project already exist <a href="{reverse("admin:psm_project_change", args=(prj[0].id,))}"> {prj[0].pjcode} </a>'))
            else:
                new_proj = Project.objects.create()
                for field in ProjectRequest._meta.fields:
                    if (not field.name == 'id') and (not field.name == 'code'): 
                        setattr(new_proj, field.name, getattr(obj, field.name))
                new_proj.description = "##As-Is\n%s \n##To-Be\n%s" % (obj.asis, obj.tobe) 
                # new_proj.p_plan_e   = obj.p_plan_e
                new_proj.p_plan_b   = obj.p_plan_b
                new_proj.p_kickoff  = obj.p_kickoff
                new_proj.p_design_b = obj.p_design_b 
                new_proj.p_design_e = previous_business_day(obj.p_dev_b)
                new_proj.p_dev_b    = obj.p_dev_b
                new_proj.p_dev_e    = previous_business_day(obj.p_uat_b)
                new_proj.p_uat_b    = obj.p_uat_b
                new_proj.p_uat_e    = previous_business_day(obj.p_launch)
                new_proj.ref_plan   = obj
                new_proj.save()
                obj.released = new_proj
                obj.save()
                messages.add_message(request, messages.INFO, mark_safe(f"released to actual project to <a href='{reverse('admin:psm_project_change', args=(new_proj.id,))}'> {new_proj.pjcode} </a>") )


    # fix conflict issue with two package: import/export, obj-action
    changelist_actions = ['redirect_to_export', 'redirect_to_import']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser :
            del actions['delete_selected']
        return actions

    # list with default filter
    def changelist_view(self, request, extra_context=None):
        if len(request.GET) == 0:
            get_param = "version_filter=10-Initial"
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(ProjectRequestAdmin, self).changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        # if self.code is None:
        prefix = 'BAP-' if obj.version == Versions.V20.value else ('UNP-' if obj.version == Versions.V21.value else 'REQ-')
        next_code = Project.objects.filter(year = obj.year).count() + 1
        obj.code = prefix + f'{obj.year % 100}-{"{:04d}".format(next_code)}'    
        # self.save()

        # validation check in admin, not possible -> https://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-custom-validation-to-the-admin

        super().save_model(request, obj, form, change)



# ===================================================================================================
# @admin.register(ProjectSet)
# class ProjectSetAdmin(admin.ModelAdmin):
#     search_fields = ('id', 'title', 'code')     
#     list_display = ('id', 'proxy_name', 'year', 'version', 'code', 'title', 'ref_plan') 
#     list_display_links = ('title',)

# ----------------------------------------------------------------------------------------------------------------
class ProjectResource(resources.ModelResource):
    pm_name    = fields.Field(attribute='pm',   widget=ForeignKeyWidget(model=Profile, field='name'))
    CBUpm_name = fields.Field(attribute='CBUpm',widget=ForeignKeyWidget(model=Profile, field='name'))
    dept_name  = fields.Field(attribute='dept', widget=ForeignKeyWidget(model=Dept, field='name'), )
    team_name  = fields.Field(attribute='team', widget=ForeignKeyWidget(model=Team, field='name'), )    
    cbu_names       = fields.Field(attribute='CBUs',    widget=ManyToManyWidget(model=CBU, separator=',', field='name'), )
    strategy_names  = fields.Field(attribute='strategy',widget=ManyToManyWidget(model=Strategy, separator=',', field='name'), )
    class Meta:
        model = Project
        fields = ( 'id', 'year', 'code', 'cf', 'title', 'description', 'objective', 'phase', 'state', 'progress', 'ref_plan__code',
            'pm', 'pm_name',  'CBUs', 'cbu_names', 'CBUpm_name', 'strategy', 'strategy_names', 'program', 'program__name','type', 'size', 'priority', 
            'est_cost', 'budget', 'dept', 'dept_name', 'dept__div', 'dept__div__name', 'team', 'team_name', 'pm__dept__name', 'pm__team__name', 'gmdm',
            'p_ideation','p_plan_b','p_kickoff','p_design_b', 'p_design_e', 'p_dev_b', 'p_dev_e', 'p_uat_b','p_uat_e','p_launch','p_close',
                         'a_plan_b','a_kickoff','a_design_b', 'a_design_e', 'a_dev_b', 'a_dev_e', 'a_uat_b','a_uat_e','a_launch','a_close',
            'wbs__wbs', 'es', 'ref', 'cbu_req','cbu_sow','cbu_po', 'status_o', 'status_t', 'status_b', 'status_s', 'pm_memo'
        )
        export_order = fields

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('__all__')
        widgets = {
            'pm': autocomplete.ModelSelect2(url='profile-staff-autocomplete')    # common.adminfilters.py
        }
# ----------------------------------------------------------------------------------------------------------------
@admin.register(Project)
class ProjectAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    form = ProjectForm
    resource_class = ProjectResource
    class Meta:
        import_id_fields = ('id',)
        exclude = ()
    class Media:
        css = {
        'all': ('psm/css/custom_admin.css',),
    }    
    search_fields = ('id', 'title', 'description', 'objective', 'pm_memo', 'code', 'wbs__wbs', 'es', 'ref', 'program__name', 'strategy__name', 'pm__name', 'CBUpm__name', 'CBUs__name')     #FIXME many to many
    list_display = ('year', 'pjcode', 'title', 'dept', 'progress', 'phase', 'pm_link', 'CBU_names', 'view', 'ITPC' )    #CBU many to many
    list_display_links = ('pjcode', 'title')
    list_editable = ("phase", )
    list_filter = ('pm', 'dept', 'phase', 'state', 'CBU_names', )    #CBU many to many
    list_filter = (
        ('status_o', UnionFieldListFilter),
        ('year', DropdownFilter),
        ('phase', UnionFieldListFilter),
        ('state', UnionFieldListFilter),
        ('CBUs', RelatedDropdownFilter),   #FIXME many to many
        ('dept', RelatedDropdownFilter),
        ('dept__div', RelatedDropdownFilter), #FIXME dept__div not working
        ('program', RelatedDropdownFilter),
        ('priority', UnionFieldListFilter),
        # ('req_pro', DropdownFilter),
        ('cf',          DropdownFilter),
        ('is_internal', DropdownFilter),
        # ('req_sec', DropdownFilter),
        # ('req_sec', DropdownFilter),
        
#        'deadline'
    )
    ordering = ['-year', '-code', ]  #Project_PRIORITY_FIELDS
    readonly_fields = ('cf', 'created_at', 'updated_on', 'created_by', 'updated_by', 'lstrpt',  'link', )
    autocomplete_fields = ['pm', 'CBUs', 'strategy', 'CBUpm', 'program', 'ref_plan', 'gmdm', 'wbs']

    fieldsets = (               # Edition form
        (None,  {'fields': (('title', 'type', 'size', 'year', 'cf' ), 
                            ('state', 'phase', 'progress', 'priority'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', 'lstrpt', 'pm_memo'), 
                            ), "classes": ("stack_labels",)}),
        (_('Detail...'),  {'fields': (('strategy', 'program', 'is_agile'), ('CBUs', 'CBUpm', 'ref'),('pm', 'dept', 'team' ), 
                            ( 'est_cost', 'budget', 'wbs', 'es', 'is_internal' ), ('description', 'objective'),  ('ref_plan', 'gmdm'),
                                       ), 'classes': ('collapse',)}),
        (_('Schedule...'),  {'fields': (('p_ideation',),('p_plan_b','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                                        ('a_plan_b','a_kickoff','a_design_b','a_design_e','a_dev_b','a_dev_e','a_uat_b','a_uat_e','a_launch','a_close'),
                                        ('cbu_req','cbu_sow','cbu_po',),
                                       ), 'classes': ('collapse',)}),
        (_('Communication...'),  {'fields': (('email_active'), ('recipients_to',), ), 'classes': ('collapse',)}),
        (_('More...'), {'fields': ( ('created_at', 'created_by', 'updated_on', 'updated_by'), ('attachment'), ), 'classes': ('collapse',)}),
        # (None, {'fields': (('link',),) }) 'req_sec','req_inf'
    )

    def ITPC(self, obj):
        count = Review.objects.filter(project=obj).count()
        return mark_safe(f"<a class='btn btn-outline-success p-1 btn-sm adminlist' style='color:#000' target='_blank' href='{reverse('admin:reviews_review_changelist')}?project__id__exact={obj.id}'>{count}</a>")
    ITPC.short_description = 'ITPC'

    def view(self, obj):
        # count = Report.objects.filter(project=obj).count()
        return mark_safe(f"<a class='btn btn-outline-success p-1 btn-sm adminlist' style='color:#000' href='{reverse('project_detail', args=(obj.id,))}'>View</a>")

    def pm_link(self, obj):
        # FIXME
        # url = reverse('admin:psm_project') + f'?pm={[obj.id]}'
        return mark_safe(f"<a href='{reverse('admin:psm_project_changelist')}?pm={obj.pm_id}'>{obj.pm}</a>")
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('title', 'type', 'size', 'year'), ('strategy', 'program','is_agile'), 
                            ('CBUs', 'CBUpm', 'ref', ), ('pm', 'dept', 'team'), 
                            ( 'est_cost', 'budget', 'wbs', 'es',  ),
                            ('state', 'phase', 'progress', 'priority'), ('description', 'objective'),  ('ref_plan',),
                            ('p_ideation', 'p_plan_b','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                            # ('req_pro','req_sec','req_inf'), 
                            # 'attachment'
                        )}),
            )
        return fieldsets

    inlines = [ProjectDeliverableInline]
    
    # easier option for admin-actions: https://pypi.org/project/django-object-actions/
    # https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#overriding-vs-replacing-an-admin-template
    # object actions - method #1
    # change_form_template = 'admin/psm/project/change_form.html'
    # object-function
    # 
    change_actions = ('project_view','report_add', 'report_list', 'risk_add', 'risk_list', 'itpc')

    def project_view(self, request, obj):
        return HttpResponseRedirect(reverse('project_detail', args=(obj.id, )))
    project_view.label = 'View'
    def report_add(self, request, obj):
        return HttpResponseRedirect(f'{reverse("admin:reports_report_add")}?project__id={obj.id}')
    report_add.label = '++Report'
    def report_list(self, request, obj):
        return HttpResponseRedirect(f'{reverse("admin:reports_report_changelist")}?project__id={obj.id}')
    report_list.label = 'Report list'
    def risk_add(self, request, obj):
        return HttpResponseRedirect(f'{reverse("admin:reports_reportrisk_add")}?project__id={obj.id}')
    risk_add.label = '++Risk'
    def risk_list(self, request, obj):
        return HttpResponseRedirect(f'{reverse("admin:reports_reportrisk_changelist")}?project__id={obj.id}')
    risk_list.label = 'Risk list'
    def itpc(self, request, obj):
        return HttpResponseRedirect(f'{reverse("admin:reviews_review_changelist")}?project__id={obj.id}')
    itpc.label = 'ITPC'

    # https://stackoverflow.com/questions/19542295/overridding-django-admins-object-tools-bar-for-one-model
    # change_list_template = 'admin/psm/project/change_list.html'

    # admin/base_site.html - field-link { display: none;}    
    def link(self, obj):
        return mark_safe(f"<a class='btn btn-outline-success p-1 my-admin-link' style='color:fff' href='{reverse('admin:reports_report_changelist')}?project__id__exact={obj.id}'> GO TO project report list </a>")
    link.short_description = 'Links'        
    # the following is necessary if 'link' method is also used in list_display
    # link.allow_tags = True

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'

    def cbu_list(self, obj):
        return " ,".join(p.name for p in obj.CBUs.all())
    cbu_list.short_description = 'CBU'

    #not working...https://stackoverflow.com/questions/46892851/django-simple-history-displaying-changed-fields-in-admin
    # formfield_overrides = {
    #     models.TextField: {
    #         'widget': Textarea(attrs={'rows': 4, 'cols': 80})
    # 'get_form' is working 
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if hasattr(form, 'base_fields'):
            form.base_fields['description'].widget.attrs.update({'rows':5,'cols':80})
            form.base_fields['objective'].widget.attrs.update({'rows':5,'cols':80})
            form.base_fields['ref_plan'].widget.attrs['style'] = 'width: 550px'
            if  obj:    #change
                form.base_fields['pm_memo'].widget.attrs.update({'rows':5,'cols':40})
                form.base_fields['recipients_to'].widget.attrs.update({'rows':6,'cols':800})
                # form.base_fields['recipients_cc'].widget.attrs.update({'rows':5,'cols':120})      #not yet implemented
                form.base_fields["recipients_to"].help_text = 'Use semi-colon to add multiple. Example: "Johnny Test" <johnny@test.com>; Jack <another@test.com>; "Scott Summers" <scotts@test.com>; noname@test.com'
                # form.base_fields["is_agile"].help_text = 'Mark if the project requires multiple launches'

                #TODO for conditional field change/display
                # form.fields['comment'].disabled = True

        return form

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%m/%d/%y")
    formatted_created_at.short_description = 'Created'


    #https://stackoverflow.com/questions/10179129/filter-foreignkey-field-in-django-admin
    #https://stackoverflow.com/questions/25972112/filter-modelchoicefield-by-user-in-django-admin-form
    #select field - default selection filter
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super(ProjectAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'strategy':
            field.queryset = field.queryset.filter(is_active=True)
        # FIXME not working...
        # if db_field.name == 'pm':
        #     field.queryset = field.queryset.filter(CBU__cbu_type=0)
        return field

        # def get_form(self, request, obj=None, **kwargs):    
        #     form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        #     form.base_fields['strategy'] = forms.ModelChoiceField(queryset=is_active=True)
        #     return form
        
    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['strategy'].queryset = Strategy.objects.filter(is_active=True)
    #     return super(ProjectAdmin, self).render_change_form(request, context, *args, **kwargs)

    # (not called from admin-import-export)
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)
    
        # if not obj.code: #not migration 
        #     obj.code = f'{obj.year % 100}-{"{:04d}".format(obj.pk+2000)}'
        #     obj.save()    


    # def get_queryset(self, request):
    #     return super(ProjectAdmin, self).get_queryset(request)
        # original qs
        # qs = super(ProjectAdmin, self).get_queryset(request)
        # filter by a variable captured from url, for example -> to enhance
        # return qs.filter(title__startswith='Project2')


    # https://stackoverflow.com/questions/15196313/django-admin-override-delete-method
    actions = ['delete_model']
    def delete_queryset(self, request, queryset):
        queryset.delete()
        # pass

    def delete_model(self, request, obj):
        obj.delete()
        # pass


    actions = ['carryfoward', 'duplicate_project', 'create_review']
    @admin.action(description="Carryforward to next year", permissions=['change'])
    def carryfoward(self, request, queryset):
        for obj in queryset:

            if Project.objects.filter(year=(obj.year+1), code=obj.code).exists():
                messages.add_message(request, messages.ERROR, f'{obj.code} "{obj.title}" is already carryfoward done')
                continue
            if obj.a_close and obj.a_close.year == obj.year:
                messages.add_message(request, messages.ERROR, f'{obj.code} "{obj.title}" is already closed in {obj.year}')
                continue
            if obj.p_close.year <= obj.year:
                messages.add_message(request, messages.ERROR, f'{obj.code} "{obj.title}" is planned to complete in {obj.year}. Please check project planned schedule')
                continue
            if obj.state in [State.CANCEL.value, State.DONE.value ]:
                messages.add_message(request, messages.ERROR, f'{obj.code} "{obj.title}" is cancel/complete state')
                continue
            if obj.phase in [ Phase.COMPLETED.value, Phase.CLOSED.value ]: 
                messages.add_message(request, messages.ERROR, f'{obj.code} "{obj.title}" is completed/closed phase')
                continue
            
            old = Project.objects.get(pk=obj.pk) 
            
            obj.id = None   #same project code
            obj.year = obj.year + 1
            obj.cf = True   #carryforward 
            obj.save()

            # many-to-many copy object... this is the way to do
            obj.CBUs.set(old.CBUs.all())    
            obj.strategy.set(old.strategy.all())    
            obj.save() 
            # new.CBUs =obj.CBUs mark_safe("released to actual project to <a href='/admin/psm/project/%s'>%s</a>" % (new_proj.id, new_proj.pjcode) )
            messages.add_message(request, messages.INFO, mark_safe(f"released to actual project to <a href='{reverse('admin:psm_project_change', args=(obj.id,))}'>{obj.pjcode}</a>"))

    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_project(self, request, queryset):
        for obj in queryset:
            # new = Project.objects.get(pk=obj.pk)
            obj.id = None
            obj.title += " (copy)"
            obj.save()      #FIXME CBU - many-to-many is empty... why??
            messages.add_message(request, messages.INFO, ' is copied/saved')

    @admin.action(description="Request procurement(ITPC)", permissions=['change'])
    def create_review(self, request, queryset):
        for obj in queryset:
            new_review = Review.objects.create(title='New Request', project=obj)
            messages.add_message(request, messages.SUCCESS, mark_safe(f"New review is requested. <a href='{reverse('admin:reviews_review_change', args=(new_review.id,))}'> review #{new_review.id}</a>"))

    changelist_actions = ['redirect_to_export', 'redirect_to_import']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser :
            del actions['delete_selected']
        return actions
    
# https://adriennedomingus.medium.com/adding-custom-views-or-templates-to-django-admin-740640cc6d42

# FIXME - TODO
    # default filter to exclude closed ticket
    def changelist_view(self, request, extra_context=None):
        if len(request.GET) == 0:
            get_param = f"year={ date.today().year }"   #state_filter=30-on_hold%2C20-doing%2C10-to-do%2C00-backlog"
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(ProjectAdmin, self).changelist_view(request, extra_context=extra_context)

