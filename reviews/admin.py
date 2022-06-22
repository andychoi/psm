from ast import Or
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter

from django.urls import reverse
from django.utils.html import mark_safe
from django.http import HttpResponseRedirect
# from django.forms import TextInput, Textarea
# from django.db import models

# Register your models here.
from .models import Review, ReviewLog
from psm.models import Project, DECISION3, Decision3
from common.models import CBU, ReqTypes, REQTYPES
from users.models import Profile
# permission https://django-guardian.readthedocs.io/en/stable/userguide/admin-integration.html
# TODO
# from guardian.admin import GuardedModelAdmin

# TIP: for easier custom permission change, need to change it in both places (models.py and your DB) 
# from django.contrib.auth.models import Permission
# admin.site.register(Permission)

from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget

from django_object_actions import DjangoObjectActions

class ReviewResource(resources.ModelResource):
    # pm_name     = fields.Field(attribute='project.pm',     widget=ForeignKeyWidget(Profile, 'name'))
    cbu_names   = fields.Field(attribute='CBU',   widget=ManyToManyWidget(model=CBU, separator=',', field='name'), )

    class Meta:
        model = Review
        fields = ('id', 'title', 'status', 'priority', 'state', 'reqtype', 
            'project__code', 'project__title', 'project__phase', 'project__state', 'project__pm__name', 'project__dept__name', 'project__team__name',
            'cbu_names',
            'project__p_ideation','project__p_plan_b','project__p_kickoff',
        )
        export_order = fields


class ReviewInline(admin.TabularInline):
    model = ReviewLog
    extra = 0
    # class Media:
        # css = {"all": ("psm/css/custom_admin.css",)}

#change base class admin.ModelAdmin into GuardedModelAdmin for object level perms.

@admin.register(Review)
class ReviewAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    resource_class = ReviewResource

    def project_dept(self, obj):
        return obj.project.dept
    list_display = ('formatted_rtype', 'project_view', 'title', 'proc_start', 'onboaddt', 'priority', 'is_escalated', 'project_dept', 'pm', 'state', 'status', 'CBU_names', 'formatted_updated',)
    list_display_links = ('title', 'formatted_updated')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'created_by', 'updated_on', 'updated_by', )
    Custom_fields = ('project_link', 'created_at', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('title', 'project__title', 'req_content', 'res_content',  )
    list_editable = ("status", "is_escalated", "state")
    autocomplete_fields = ('reviewer', 'project', 'CBU')
    fieldsets = (               # Edition form
                (None, {'fields':   (('project', 'CBU'),  ('title', 'reqtype',  ),('req_content',), ('proc_start', 'onboaddt', 'state', ), ('status', 'is_escalated', 'priority'), ( 'res_content','reviewer',),   
                            ), "classes": ("stack_labels",)}),
                (_('More...'), {'fields': (('created_at', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields':  (('project',), ('title', 'reqtype'), ('req_content',), ('proc_start', 'onboaddt', 'state', ), ('status', 'is_escalated', 'priority'), ('res_content','reviewer', ), 
                            ), "classes": ("stack_labels",)}),
            )
        return fieldsets

    list_filter = (
        ('reqtype', DropdownFilter),
        ('priority', DropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('project',             RelatedDropdownFilter),
        ('project__dept__div',  RelatedDropdownFilter),
        ('project__dept',       RelatedDropdownFilter),
        # ('project__CBU',       RelatedDropdownFilter),
        ('status',              DropdownFilter),
        'updated_on',
    )

    inlines = [ReviewInline]

    # def view_project(self, obj):
    #     # count = Review.objects.filter(project=obj).count()
    #     return mark_safe(f"<a class='btn btn-outline-success p-1 btn-sm adminlist' style='color:#000' href='/project/{obj.project.id}'>{obj.project}</a>")

    def pm(self, obj):
        return obj.project.pm.name if obj.project.pm else "not assigned"

    def project_view(self, obj):
        if obj.project:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("project_detail", args=(obj.project.pk,)), obj.project ))
    # project_link.short_description = 'Project'

    def formatted_rtype(self, obj):
        return obj.reqtype[3:]
    formatted_rtype.short_description = 'Review Type'

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'

    def save_model(self, request, obj, form, change):
        #permission check per request type.... need better way
        # if (obj.reqtype == ReqTypes.PRO.value and not request.user.has_perm(ReqTypes.PRO.value, obj)) or (obj.reqtype == ReqTypes.SEC.value and not request.user.has_perm(ReqTypes.SEC.value, obj)) or (obj.reqtype == ReqTypes.INF.value and not request.user.has_perm(ReqTypes.INF.value, obj)) or (obj.reqtype == ReqTypes.APP.value and not request.user.has_perm(ReqTypes.APP.value, obj)) or (obj.reqtype == ReqTypes.MGT.value and not request.user.has_perm(ReqTypes.MGT.value, obj)):
        #     messages.set_level(request, messages.ERROR)
        #     messages.error(request, "You don't have permission on " + obj.reqtype)
        #     return

        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)

    # object level permission: https://www.youtube.com/watch?v=2jhQyWeEVHc&ab_channel=VeryAcademy
    # model level permission:  https://www.youtube.com/watch?v=wlYaUvfXJDc&ab_channel=VeryAcademy
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)        
        is_superuser = request.user.is_superuser
        #request.user.extenduser.<field name>
        
        # if hasattr(form, 'base_fields'):
        if form.base_fields:    #if not read only mode
            form.base_fields['req_content'].widget.attrs.update({'rows':3,'cols':40})
            form.base_fields['res_content'].widget.attrs.update({'rows':5,'cols':40})
            form.base_fields['reqtype'].disabled = True 

            # when creating or updating by non-reviewer (except superuser)
            conditions = ( ( obj is None ) 
                or ( request.user.profile.is_pro_reviewer and obj.reqtype == ReqTypes.PRO.value ) )
                # or ( request.user.profile.is_sec_reviewer and obj.reqtype == ReqTypes.SEC.value ) 
                # or ( request.user.profile.is_inf_reviewer and obj.reqtype == ReqTypes.INF.value ) 
                # or ( request.user.profile.is_app_reviewer and obj.reqtype == ReqTypes.APP.value ) 
                # or ( request.user.profile.is_mgt_reviewer and obj.reqtype == ReqTypes.MGT.value ) )
            if conditions and (not is_superuser):
                # allow only reviewer to allow updating
                form.base_fields['status'].disabled = True 
                form.base_fields['priority'].disabled = True 
                form.base_fields['is_escalated'].disabled = True 
                form.base_fields['reviewer'].disabled = True 
                form.base_fields['res_content'].disabled = True 

            form.base_fields['project'     ].widget.attrs['style'] = 'width: 40em;'
        return form

    # def has_add_permission(self, request):
    #     return True
    # def has_change_permission(self, request, obj=None):
    #     if (request.user.is_superuser):
    #         return True 
    #     if obj.pk:  #change 
    #         if request.user.profile.is_pro_reviewer and obj.reqtype == ReqTypes.PRO.value:
    #             return True
    #     return super(ReviewAdmin, self).has_change_permission(request, obj)

    # def has_delete_permission(self, request, obj=None):
    #     return True
    # def has_view_permission(self, request, obj=None):
    #     return True

        # example
        # if request.user.groups.filter(name='editors').exists():
        # if request.POST.get('action') == 'delete_selected':
        # return False


   #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin -> dump... why??? FIXME
    # def get_form(self, request, obj=None, change=False, **kwargs):
    #     form = super().get_form(request, obj, change, **kwargs)
    #     # form.base_fields['related'].widget.attrs.update({'rows':3,'cols':40})
    #     form.base_fields['content'].widget.attrs.update({'rows':5,'cols':40})
    #     return form        

       # object action FIXME
    change_actions = ('goto_project',)
    # object-function
    def goto_project(self, request, obj):
        return HttpResponseRedirect(f'/admin/psm/project/{obj.project.id}')

    #FIX conflict with DjangoObjectActions, import/export
    changelist_actions = ['redirect_to_export', 'redirect_to_import']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_export.label = "Import"