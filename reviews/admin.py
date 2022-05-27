from ast import Or
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter

from django.urls import reverse
from django.utils.html import mark_safe

# Register your models here.
from .models import Review, ReviewLog
from psm.models import Project, STATE3, State3
from common.models import ReviewTypes, REVIEWTYPES

class ReviewInline(admin.TabularInline):
    model = ReviewLog
    extra = 0
    class Media:
        css = {"all": ("psm/css/custom_admin.css",)}


@admin.register(Review)
class ReviewAdmin(ImportExportMixin, admin.ModelAdmin):


    list_display = ('reviewtype', 'project_link', 'title', 'formatted_updated', 'is_escalated', 'CBU', 'dept', 'state')
    list_display_links = ('title', 'formatted_updated')
    ordering = ('-id',)
    readonly_fields = ('project_link', 'created_on', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('title', 'project__title', 'content', )

    fieldsets = (               # Edition form
                (None, {'fields':   (('project', 'title', 'reviewtype', 'priority'), ('status', 'is_escalated'), ('content',), ('proc_start', 'onboaddt', 'state'), 
                            ), "classes": ("stack_labels",)}),
                (_('More...'), {'fields': (('CBU', 'div', 'dept'), ('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields':  (('project', 'title', 'reviewtype', 'priority'), ('status', 'is_escalated'), ('content',), ('proc_start', 'onboaddt', 'state' ) 
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


    #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        # form.base_fields['related'].widget.attrs.update({'rows':3,'cols':40})
        form.base_fields['content'].widget.attrs.update({'rows':5,'cols':40})
        return form

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'

    def save_model(self, request, obj, form, change):
        #permission check per request type
        breakpoint()
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



        # if obj.status == 1:  #if published, update project master info
        #     obj.project.status_o = obj.status_o
        #     obj.project.lstrpt = obj.updated_on   #update to project last report date
        #     obj.project.save()


