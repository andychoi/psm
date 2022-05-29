from adminfilters.multiselect import UnionFieldListFilter
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from django import forms

from django.utils.html import format_html

from common.models import State3, ReviewTypes
from .models import Project, ProjectItem, ProjectItemCategory, Project_PRIORITY_FIELDS, Strategy, Program
from reviews.models import  Review

@admin.register(Strategy)
class StrategyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'last_modified','is_active')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')

    class Meta:
        model = Strategy
        import_id_fields = ('id',)

@admin.register(Program)
class ProgramAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'lead', 'startyr', 'is_active')
    list_display_links = ('name', 'lead')
    search_fields = ('name',)
    ordering = ('-startyr', 'name',)

    class Meta:
        model = Program
        import_id_fields = ('id',)

# to make textarea format
class ProjectItemModelForm( forms.ModelForm ):
    desc = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = ProjectItemCategory
        fields = '__all__'

@admin.register(ProjectItemCategory)
class ProjectItemCategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    form = ProjectItemModelForm
    class Meta:
        import_id_fields = ('id',)

class ProjectItemInline(admin.TabularInline):
    model = ProjectItem
    extra = 0
    class Media:
        css = {"all": ("psm/css/custom_admin.css",)}

@admin.register(Project)
class ProjectAdmin(ImportExportMixin, admin.ModelAdmin):
    class Media:
        css = {
        'all': ('psm/css/custom_admin.css',),
    }    
    # list_display = ('PJcode', 'title', 'user', 'CBU', 'formatted_created_at', 'dept', 'phase', 'state')
    list_display = ('PJcode', 'title', 'user', 'CBU',  'dept', 'phase', 'state')
    list_display_links = ('PJcode', 'title')
    search_fields = ('id', 'title', 'description', 'resolution', 'projectitem__item_description',
                     'wbs__wbs', 'es', 'ref', 'user__name', 'CBUpm__name')
    list_filter = (
        ('status_o', UnionFieldListFilter),
        ('year', DropdownFilter),
        ('div', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
        ('req_pro', DropdownFilter),
        ('req_sec', DropdownFilter),
        ('req_sec', DropdownFilter),
        
#        'deadline'
    )
    ordering = ['-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'last_modified', 'created_by', 'lstrpt',)
    autocomplete_fields = ['user', 'CBU']

    fieldsets = (               # Edition form
        (None,  {'fields': (('title', 'type', 'year'), 
                            ('state', 'phase', 'progress', 'priority'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', 'lstrpt', 'resolution'), 
                            ('req_pro','req_sec','req_inf'), 
                            ('attachment')), "classes": ("stack_labels",)}),
        (_('Detail...'),  {'fields': (('strategy', 'program'), ('CBU', 'CBUpm', 'ref'),('user', 'team', 'dept', 'div'), 
                            ( 'est_cost', 'app_budg', 'wbs', 'es', 'is_internal' ), ('description',), 
                                       ), 'classes': ('collapse',)}),
        (_('Schedule...'),  {'fields': (('p_pre_plan_b','p_pre_plan_e','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                                        ('a_pre_plan_b','a_pre_plan_e','a_kickoff','a_design_b','a_design_e','a_dev_b','a_dev_e','a_uat_b','a_uat_e','a_launch','a_close'), 
                                       ), 'classes': ('collapse',)}),
        (_('More...'), {'fields': ( ('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('title', 'type', 'year'), ('strategy', 'program'), ('CBU', 'CBUpm', 'ref'), ('user', 'team', 'dept', 'div'), 
                            ( 'est_cost', 'app_budg', 'wbs', 'es', 'is_internal' ),
                            ('state', 'phase', 'progress', 'priority'), 'description', 
                            ('p_pre_plan_b','p_pre_plan_e','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                            ('req_pro','req_sec','req_inf'), 
                            'attachment')}),
            )
        return fieldsets

    inlines = [ProjectItemInline]

    class Meta:
        import_id_fields = ('id',)

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

    # (not called from admin-import-export)
    def save_model(self, request, obj, form, change):
        if change is False:  #when create
            obj.created_by = request.user
            # if not obj.code: #not migration 
            #     obj.code = f'{obj.year % 100}-{"{:04d}".format(obj.pk+1000)}'
        super().save_model(request, obj, form, change)

        review_create = False
        new_reviews = []
        if change is False:  #when create
            if obj.req_pro == State3.YES.value:
                new_reviews.append(ReviewTypes.PRO.value)
            if obj.req_sec == State3.YES.value:
                new_reviews.append(ReviewTypes.SEC.value)
            if obj.req_inf == State3.YES.value:
                new_reviews.append(ReviewTypes.INF.value)

        else:   #when update      
            upd_reviews = []
            if obj._loaded_values['req_pro'] != obj.req_pro:  #when changed state only
                upd_reviews.append((ReviewTypes.PRO.value, obj.req_pro))
            if obj._loaded_values['req_sec'] != obj.req_sec:
                upd_reviews.append((ReviewTypes.SEC.value, obj.req_sec))
            if obj._loaded_values['req_inf'] != obj.req_inf:
                upd_reviews.append((ReviewTypes.INF.value, obj.req_inf))

            for upd in upd_reviews:
                # read review record
                theproc = Review.objects.filter(Q(project = obj.id) & Q(reviewtype = upd[0]))      #[:1].get()
                if theproc: #already exist
                    update_dic = { 'project' : obj, 'CBU' : obj.CBU, 'dept' : obj.dept, 'div' : obj.div, 'state' : upd[1] }
                    theproc.update(**update_dic)
                    messages.add_message(request, messages.INFO, '[' + upd[0][3:] + '] review type records are updated.')

                elif obj.req_pro == State3.YES.value: #not exist and when target is YES only
                    new_reviews.append(upd[0]) 

        if new_reviews:
            # breakpoint()
            for new in new_reviews:
                Review.objects.create(reviewtype = new, project = obj, CBU = obj.CBU, dept = obj.dept, div = obj.div, onboaddt = obj.p_kickoff, 
                                      state = obj.req_pro, priority = obj.priority, title = obj.title)
                messages.add_message(request, messages.INFO, '[' + new[3:] + '] review type - New review request is created' )

    # def get_queryset(self, request):
    #     return super(ProjectAdmin, self).get_queryset(request)
        # original qs
        # qs = super(ProjectAdmin, self).get_queryset(request)
        # filter by a variable captured from url, for example -> to enhance
        # return qs.filter(title__startswith='Project2')


    actions = ['duplicate_project']
    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_project(self, request, queryset):
        for object in queryset:
            object.id = None
            object.title = object.title + " copied"
            object.save()
            messages.add_message(request, messages.INFO, ' is copied/saved')


        