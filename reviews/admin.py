from ast import Or
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter

from django.urls import reverse
from django.utils.html import mark_safe
# from django.forms import TextInput, Textarea
# from django.db import models

# Register your models here.
from .models import Review, ReviewLog
from psm.models import Project, STATE3, State3
from common.models import ReviewTypes, REVIEWTYPES

# permission https://django-guardian.readthedocs.io/en/stable/userguide/admin-integration.html
from guardian.admin import GuardedModelAdmin

# TIP: for easier custom permission change, need to change it in both places (models.py and your DB) 
# from django.contrib.auth.models import Permission
# admin.site.register(Permission)


class ReviewInline(admin.TabularInline):
    model = ReviewLog
    extra = 0
    # class Media:
        # css = {"all": ("psm/css/custom_admin.css",)}


#change base class admin.ModelAdmin into GuardedModelAdmin for object level perms.

@admin.register(Review)
class ReviewAdmin(ImportExportMixin, admin.ModelAdmin):

    list_display = ('formatted_rtype', 'project_link', 'title', 'formatted_updated', 'is_escalated', 'CBU', 'dept', 'state')
    list_display_links = ('title', 'formatted_updated')
    ordering = ('-id',)
    readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')
    Custom_fields = ('project_link', 'created_on', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('title', 'project__title', 'req_content', 'res_content', 'reviewer__profile__name' )

    fieldsets = (               # Edition form
                (None, {'fields':   (('project', 'title', 'reviewtype', ),('req_content',), ('proc_start', 'onboaddt', 'state', ), ('status', 'is_escalated', 'priority'), ( 'res_content','reviewer',),  ('attachment'),  
                            ), "classes": ("stack_labels",)}),
                (_('More...'), {'fields': (('CBU', 'div', 'dept'), ('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields':  (('project', 'title', 'reviewtype'), ('req_content',), ('proc_start', 'onboaddt', 'state', ), ('status', 'is_escalated', 'priority'), ('res_content','reviewer', ),  ('attachment'), 
                            ), "classes": ("stack_labels",)}),
            )
        return fieldsets

    list_filter = (
        ('reviewtype', DropdownFilter),
        ('priority', DropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('div', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('status', DropdownFilter),
        'updated_on',
    )

    inlines = [ReviewInline]

    def project_link(self, obj):
        if obj.project:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    def formatted_rtype(self, obj):
        return obj.reviewtype[3:]
    formatted_rtype.short_description = 'Review Type'

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'

    def save_model(self, request, obj, form, change):
        #permission check per request type.... need better way
        # breakpoint()
        if (obj.reviewtype == ReviewTypes.PRO.value and not request.user.has_perm(ReviewTypes.PRO.value, obj)) or (obj.reviewtype == ReviewTypes.SEC.value and not request.user.has_perm(ReviewTypes.SEC.value, obj)) or (obj.reviewtype == ReviewTypes.INF.value and not request.user.has_perm(ReviewTypes.INF.value, obj)) or (obj.reviewtype == ReviewTypes.APP.value and not request.user.has_perm(ReviewTypes.APP.value, obj)) or (obj.reviewtype == ReviewTypes.MGT.value and not request.user.has_perm(ReviewTypes.MGT.value, obj)):
            messages.set_level(request, messages.ERROR)
            messages.error(request, "You don't have permission on " + obj.reviewtype)
            return

        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        # if not obj.CBU and not obj.project.CBU:  #copy from project
        #     obj.CBU = obj.project.CBU
        # if not obj.div and not obj.project.div:  #copy from project
        #     obj.div = obj.project.div
        # if not obj.dept and obj.project.dept:  #copy from project
        #     obj.dept = obj.project.dept

        super().save_model(request, obj, form, change)

    # object level permission: https://www.youtube.com/watch?v=2jhQyWeEVHc&ab_channel=VeryAcademy
    # model level permission:  https://www.youtube.com/watch?v=wlYaUvfXJDc&ab_channel=VeryAcademy
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)        
        is_superuser = request.user.is_superuser
        #request.user.extenduser.<field name>
        
        if form.base_fields:    #if not read only mode
            form.base_fields['req_content'].widget.attrs.update({'rows':3,'cols':40})
            form.base_fields['res_content'].widget.attrs.update({'rows':5,'cols':40})
            form.base_fields['reviewtype'].disabled = True 

            # when creating or updating by non-reviewer (except superuser)
            conditions = ( ( obj is None ) 
                or ( request.user.profile.is_pro_reviewer and obj.reviewtype == ReviewTypes.PRO.value ) 
                or ( request.user.profile.is_sec_reviewer and obj.reviewtype == ReviewTypes.SEC.value ) 
                or ( request.user.profile.is_inf_reviewer and obj.reviewtype == ReviewTypes.INF.value ) 
                or ( request.user.profile.is_app_reviewer and obj.reviewtype == ReviewTypes.APP.value ) 
                or ( request.user.profile.is_mgt_reviewer and obj.reviewtype == ReviewTypes.MGT.value ) )
            if conditions and (not is_superuser):
                # allow only reviewer to allow updating
                form.base_fields['status'].disabled = True 
                form.base_fields['priority'].disabled = True 
                form.base_fields['is_escalated'].disabled = True 
                form.base_fields['reviewer'].disabled = True 
                form.base_fields['res_content'].disabled = True 

        return form

    # def has_add_permission(self, request):
    #     return True
    def has_change_permission(self, request, obj=None):
        if (request.user.is_superuser):
            return True 
        if obj: 
            if request.user.profile.is_pro_reviewer and obj.reviewtype == ReviewTypes.PRO.value:
                return True
            elif request.user.profile.is_sec_reviewer and obj.reviewtype == ReviewTypes.SEC.value:
                return True
            elif request.user.profile.is_inf_reviewer and obj.reviewtype == ReviewTypes.INF.value:
                return True
            elif request.user.profile.is_app_reviewer and obj.reviewtype == ReviewTypes.APP.value:
                return True
            elif request.user.profile.is_mgt_reviewer and obj.reviewtype == ReviewTypes.MGT.value:
                return True
        return False

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