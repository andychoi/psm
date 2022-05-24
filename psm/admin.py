from adminfilters.multiselect import UnionFieldListFilter
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from .models import Project, Item, CheckItem, Project_PRIORITY_FIELDS, Strategy, Program

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from django import forms

from django.utils.html import format_html

class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified','is_active')
    list_display_links = ('name',)
    search_fields = ('name', 'description')

    ordering = ('name',)

    readonly_fields = ('created_at', 'last_modified', 'created_by')

    # def get_queryset(self, request):



@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified','is_active')
    list_display_links = ('name',)
    search_fields = ('name', 'description')

    ordering = ('name',)

    readonly_fields = ('created_at', 'last_modified', 'created_by')

    # def get_queryset(self, request):
    #     # original qs
    #     qs = super(StrategyAdmin, self).get_queryset(request)
    #     # filter by a variable captured from url, for example -> to enhance
    #     return qs.filter(is_active=True)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead', 'startyr', 'is_active')
    list_display_links = ('name', 'lead')
    search_fields = ('name',)
    ordering = ('-startyr', 'name',)

# checklist form
class CheckItemModelForm( forms.ModelForm ):
    desc = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = CheckItem
        fields = '__all__'

@admin.register(CheckItem)
class AdminCheckItem(admin.ModelAdmin):
    form = CheckItemModelForm
    pass

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    class Media:
        css = {"all": ("psm/css/custom_admin.css",)}

@admin.register(Project)
class ProjectAdmin(ImportExportMixin, admin.ModelAdmin):
    class Media:
        css = {
        'all': ('psm/css/custom_admin.css',),
    }    
    list_display = ('PJcode', 'title', 'user', 'CBU', 'formatted_created_at', 'team', 'dept', 'div', 'priority', 'state')
    list_display_links = ('PJcode', 'title')
    search_fields = ('id', 'title', 'item__item_description',
                     'user__name', 
                     'CBU__name', 'CBU__email')
    list_filter = (
        ('status_o', UnionFieldListFilter),
        ('div', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
#        'deadline'
    )
    ordering = ['-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'last_modified', 'created_by', 'lstrpt',)
    autocomplete_fields = ['user', 'CBU']

    fieldsets = (               # Edition form
        (None,                   {'fields': (('title', 'type', 'year'), ('strategy', 'program'), ('CBU', 'CBUpm'),('user', 'team', 'dept', 'div'), 
                                             ( 'est_cost', 'app_budg', 'wbs', 'is_internal' ),
                                             ('state', 'complete', 'priority'), 
                                             ('status_o', 'status_t', 'status_b', 'status_s', 'lstrpt', 'resolution'), 
                                             ('p_pre_planning','p_kickoff','p_design_b','p_design_e','p_develop_b','p_develop_e','p_uat_b','p_uat_e','p_launch','p_close'),
                                             ('a_pre_planning','a_kickoff','a_design_b','a_design_e','a_develoa_b','a_develoa_e','a_uat_b','a_uat_e','a_launch','a_close'), 
                                             ('attachment')), "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ('description', ('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('title', 'type', 'year'), ('strategy', 'program'), ('CBU', 'CBUpm'), ('user', 'team', 'dept', 'div'), 
                    ( 'est_cost', 'app_budg', 'wbs', 'is_internal' ),
                    ('state', 'complete', 'priority'), 'description', 
                    ('p_pre_planning','p_kickoff','p_design_b','p_design_e','p_develop_b','p_develop_e','p_uat_b','p_uat_e','p_launch','p_close'),
                    'attachment')}),
            )
        return fieldsets

    inlines = [ItemInline]

    #not working...https://stackoverflow.com/questions/46892851/django-simple-history-displaying-changed-fields-in-admin
    # history_list_display = ["changed_fields","list_changes"]
    
    # def changed_fields(self, obj):
    #     if obj.prev_record:
    #         delta = obj.diff_against(obj.prev_record)
    #         return delta.changed_fields
    #     return None

    # def list_changes(self, obj):
    #     fields = ""
    #     if obj.prev_record:
    #         delta = obj.diff_against(obj.prev_record)

    #         for change in delta.changes:
    #             fields += str("<strong>{}</strong> changed from <span style='background-color:#ffb5ad'>{}</span> to <span style='background-color:#b3f7ab'>{}</span> . <br/>".format(change.field, change.old, change.new))
    #         return format_html(fields)
    #     return None

    # formfield_overrides = {
    #     models.TextField: {
    #         'widget': Textarea(attrs={'rows': 4, 'cols': 80})
    #     }
    # }
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['description'].widget.attrs.update({'rows':5,'cols':80})
        if  obj:
            form.base_fields['resolution'].widget.attrs.update({'rows':5,'cols':40})
        return form

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%m/%d/%y")
    formatted_created_at.short_description = 'Created'


    #https://stackoverflow.com/questions/10179129/filter-foreignkey-field-in-django-admin
    #https://stackoverflow.com/questions/25972112/filter-modelchoicefield-by-user-in-django-admin-form
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super(ProjectAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'strategy':
            field.queryset = field.queryset.filter(is_active=True)
        return field

        # def get_form(self, request, obj=None, **kwargs):    
        #     form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        #     form.base_fields['strategy'] = forms.ModelChoiceField(queryset=is_active=True)
        #     return form
        
    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['strategy'].queryset = Strategy.objects.filter(is_active=True)
    #     return super(ProjectAdmin, self).render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # def get_queryset(self, request):
    #     return super(ProjectAdmin, self).get_queryset(request)
        # original qs
        # qs = super(ProjectAdmin, self).get_queryset(request)
        # filter by a variable captured from url, for example -> to enhance
        # return qs.filter(title__startswith='Project2')



        