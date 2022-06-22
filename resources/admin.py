from django import forms
from django.contrib import admin
from import_export.admin import ImportExportMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import mark_safe

from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from import_export.admin import ImportExportMixin

from .models import ResourcePlan, ResourcePlanItem
# Register your models here.


class ResourcePlanFormSet(forms.models.BaseInlineFormSet):
    model = ResourcePlan

class ResourcePlanInline(admin.TabularInline):
    model = ResourcePlanItem
    formset = ResourcePlanFormSet  
    extra = 3


# Register your models here.
@admin.register(ResourcePlan)
class ResourcePlanAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ( 'staff', 'year', 'status','preview_link')
    list_display_links = ('staff',)
    list_editable = ('status',)
    ordering = ('staff',)
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('staff', )     #TO-RE search line item

    fieldsets = (      # Edition form
        (None,  {'fields': ( ('staff', 'year', 'status', ) )  }),
            (_('More...'), {'fields': (('created_at', 'created_by'), ('updated_on', 'updated_by'),), 'classes': ('collapse',)}),
    )
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': ( ('staff', 'year' ) , ( 'status', ) )}),
            )
        return fieldsets

    list_filter = (
        ('staff', RelatedDropdownFilter),
        ('div', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('status', RelatedDropdownFilter),
    )
    inlines = [ResourcePlanInline]

    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d  was successfully marked as published.',
            '%d  were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

