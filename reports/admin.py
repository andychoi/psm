from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from import_export.admin import ImportExportMixin

from django.urls import reverse
from django.utils.html import mark_safe

from django.forms import formsets
from django.forms.models import BaseInlineFormSet

# Register your models here.
from .models import Report, Milestone
# from djrichtextfield.widgets import RichTextWidget

# class MilestoneFormSet(BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         kwargs['initial'] = [
#             {'stage': 'Overall', 'description': 'Overall project status', },
#             {'stage': '1.Plan & Define', 'description': 'Requirements gathering', },
#             {'stage': '1.Plan & Define', 'description': 'Validate requirement expectations', },
#             {'stage': '1.Plan & Define', 'description': 'Architectural,Technical and Security Design', },
#             {'stage': '1.Plan & Define', 'description': 'Project Planning', },
#             {'stage': '1.Plan & Define', 'description': 'SOW / Contract', },
#             {'stage': '1.Plan & Define', 'description': 'Project Kickoff', },
#             {'stage': '2.Implement', 'description': 'Detail design', },
#             {'stage': '2.Implement', 'description': 'Development', },
#             {'stage': '2.Implement', 'description': 'Integration', },
#             {'stage': '2.Implement', 'description': 'User acceptance testing', },
#             {'stage': '3.Deployment', 'description': 'Go-live preparation', },
#             {'stage': '3.Deployment', 'description': 'Deployment', },
#             {'stage': '4.Post Support', 'description': 'Hyper care', },
#             {'stage': '4.Post Support', 'description': 'Signoff,closure', },
#         ]
#         super(MilestoneFormSet, self).__init__(*args, **kwargs)

class MilestoneInline(admin.TabularInline):
    model = Milestone
    # formset = MilestoneFormSet  #not working... init form... in change mode stil...
    extra = 0   # You said you need 3 rows
    ordering = ('no',)
    # readonly_fields = ('title', 'url', 'display_score')
    # fields = ('title', 'url', 'display_score')
    class Media:
        css = {"all": ("psm/css/style-hide.css",)}


@admin.register(Report)
class ReportAdmin(ImportExportMixin, admin.ModelAdmin):
    class Media:
        css = {
        'all': ('reports/css/custom_admin.css',),
    }

    list_display = ('project_link', 'title', 'CBU', 'updated_by','updated_on', 'status','preview_link')
    list_display_links = ('title', 'updated_on')
    ordering = ('-id',)

    readonly_fields = ('project_link', 'created_on', 'updated_on', 'created_by', 'updated_by')

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:psm_project_change", args=(obj.project.pk,)), obj.project.title ))
    project_link.short_description = 'Project'

    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    fieldsets = (               # Edition form
        (None, {'fields': (('project', 'title', 'CBU', 'status'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', ), 
                            ('content_a', 'content_p', 'issue'), ),  "classes": ("stack_labels",)}),
            (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    list_filter = (
        ('project', UnionFieldListFilter),
        ('updated_by', RelatedDropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('status', UnionFieldListFilter),
        'updated_on'
    )

    inlines = [MilestoneInline]

    #https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['content_a'].widget.attrs.update({'rows':5,'cols':80})
        form.base_fields['content_p'].widget.attrs.update({'rows':5,'cols':80})
        form.base_fields['issue'].widget.attrs.update({'rows':5,'cols':80})
        return form

    # def formatted_created_at(self, obj):
    #     return obj.created_at.strftime("%m/%d/%y")
    # formatted_created_at.short_description = 'Created'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('project', 'title', 'CBU', 'status'), 
                                    ('status_o', 'status_t', 'status_b', 'status_s', ), 
                                    ('content_a', 'content_p', 'issue'),)}),
            )
        return fieldsets


    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

        if obj.status == 1:
            obj.project.status_o = obj.status_o
            obj.project.status_t = obj.status_t
            obj.project.status_b = obj.status_b
            obj.project.status_s = obj.status_s
            obj.project.resolution = obj.issue
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

