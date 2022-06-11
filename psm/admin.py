import sys
import inspect
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from django import forms

from django.utils.html import format_html
from django.utils.html import mark_safe

from common.models import State3, ReviewTypes, Versions
from .models import Project, ProjectPlan, ProjectRequest, ProjectDeliverable, ProjectDeliverableType, Project_PRIORITY_FIELDS, Strategy, Program
from reviews.models import  Review
from django.contrib.admin import AdminSite
from django.http import HttpResponse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


# https://stackoverflow.com/questions/54514324/how-to-register-inherited-sub-class-in-admin-py-file-in-django
# GOOD: https://stackoverflow.com/questions/241250/single-table-inheritance-in-django
# READ: https://chelseatroy.com/2018/08/26/proxy-models-in-django-an-example-and-a-use-case/

@admin.register(Strategy)
class StrategyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'updated_on','is_active')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_on', 'created_by')

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


@admin.register(ProjectPlan)
class ProjectPlanAdmin(ImportExportMixin, admin.ModelAdmin):
    class Meta:
        import_id_fields = ('id',)
        exclude = ()
    class Media:
        css = { 'all': ('psm/css/custom_admin.css',), }

    list_display = ('version', 'pjcode',  'title', 'pm', 'dept', 'CBU_str', 'est_cost' )    #CBU many to many
    list_display_links = ('pjcode', 'title')
    list_editable = ("version", )
    search_fields = ('id', 'title', 'asis', 'tobe', 'objective', 'consider', 'code', 'pm__name', 'CBUpm__name', 'CBUs__name')
    list_filter = (
        ('version',     DropdownFilter),
        ('year',        DropdownFilter),
        ('CBUs',        RelatedDropdownFilter),   
        ('dept',        RelatedDropdownFilter),
        ('dept__div',   RelatedDropdownFilter), #FIXME dept__div not working
        ('priority',    UnionFieldListFilter),
    )
    ordering = ['version', '-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'updated_on', 'created_by', )
    autocomplete_fields = ['pm', 'CBUs', 'strategy', 'CBUpm', 'program']
    plan_fields = [ ('title', 'year', 'version' ), 
                    ('type', 'priority'), 
                    ('strategy', 'program', 'is_agile'),
                    ('CBUs', 'CBUpm'),
                    ('asis', 'img_asis'),
                    ('tobe', 'img_tobe'),
                    ('objective', 'consider'),
                    ('quali', 'quant'),
                    ('est_cost', 'resource'),
                    ('p_ideation','p_plan_b','p_kickoff','p_design_b','p_dev_b','p_uat_b','p_launch','p_close')]
    fieldsets = (               # Edition form
        (None,  {'fields': plan_fields 
                , "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'),  ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.plan_fields  }), )

    # default version set
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectPlanAdmin, self).get_form(request, obj, **kwargs)
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

    actions = ['move_to_final_version', 'move_to_11_version', 'move_to_12_version', 'transfer_to_actual' ]
    @admin.action(description="Move to final version", permissions=['change'])
    def move_to_final_version(self, request, queryset):
        for object in queryset:
            object.version = Versions.V20.value
            object.save()
            messages.add_message(request, messages.INFO, ' is moved to final version')

    @admin.action(description="Move to version 11", permissions=['change'])
    def move_to_11_version(self, request, queryset):
        for object in queryset:
            object.version = Versions.V11.value
            object.save()
            messages.add_message(request, messages.INFO, ' is moved to version 11')

    @admin.action(description="Move to version 12", permissions=['change'])
    def move_to_12_version(self, request, queryset):
        for object in queryset:
            object.version = Versions.V12.value
            object.save()
            messages.add_message(request, messages.INFO, ' is moved to version 12')

    @admin.action(description="Transfer to Actual Project", permissions=['change'])
    def transfer_to_actual(self, request, queryset):
        for object in queryset:

            if Project.objects.filter(title=object.title).exists():
                messages.add_message(request, messages.ERROR, mark_safe(u"Project name: %s has already exist." % object.title))

            else:
                new_proj = Project.objects.create()
                for field in ProjectPlan._meta.fields:
                    if (not field.name == 'id') and (not field.name == 'proxy_name') and (not field.name == 'code'):
                        setattr(new_proj, field.name, getattr(object, field.name))
                new_proj.save()
                messages.add_message(request, messages.INFO, mark_safe("transfered to actual project to <a href='/admin/psm/project/%s'>%s</a>" % (new_proj.id, new_proj.code) ))


# --------------------------------------------------------------------------------------------------
@admin.register(ProjectRequest)
class ProjectRequestAdmin(ImportExportMixin, admin.ModelAdmin):
    class Meta:
        import_id_fields = ('id',)
        exclude = ()
    class Media:
        css = { 'all': ('psm/css/custom_admin.css',), }

    list_display = ('pjcode',  'title', 'pm', 'dept', 'CBU_str', 'est_cost' )    #CBU many to many
    list_display_links = ('pjcode', 'title')
    # list_editable = ("wf_state", )
    search_fields = ('id', 'title', 'asis', 'tobe', 'objective', 'consider', 'code', 'pm__name', 'CBUpm__name', 'CBUs__name')
    list_filter = (
        ('year',        DropdownFilter),
        ('CBUs',        RelatedDropdownFilter),   
        ('dept',        RelatedDropdownFilter),
        ('dept__div',   RelatedDropdownFilter), #FIXME dept__div not working
        ('priority',    UnionFieldListFilter),
    )
    ordering = ['-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'updated_on', 'created_by', )
    autocomplete_fields = ['pm', 'CBUs', 'strategy', 'CBUpm', 'program']
    Request_fields = [ ('title', 'year',  ), 
                    ('type', 'priority'), 
                    ('strategy', 'program', 'is_agile'),
                    ('CBUs', 'CBUpm'),
                    ('asis', 'img_asis'),
                    ('tobe', 'img_tobe'),
                    ('objective', 'consider'),
                    ('quali', 'quant'),
                    ('est_cost', 'resource'),
                    ('p_ideation','p_plan_b','p_kickoff','p_design_b','p_dev_b','p_uat_b','p_launch','p_close')]
    fieldsets = (               # Edition form
        (None,  {'fields': Request_fields 
                , "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'),  ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.Request_fields  }), )

    # default version set
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectRequestAdmin, self).get_form(request, obj, **kwargs)
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

    # permission - TODO
    # https://stackoverflow.com/questions/23410306/add-permission-to-django-admin

    actions = ['approve_project_request' ]
    @admin.action(description="Approve Project Request", permissions=['approve'])
    def approve_project_request(self, request, queryset):
        for object in queryset:
            new_proj = Project.objects.create()

            for field in ProjectRequest._meta.fields:
                if (not field.name == 'id') and (not field.name == 'proxy_name') and (not field.name == 'code'):
                    setattr(new_proj, field.name, getattr(object, field.name))

            new_proj.save()
            messages.add_message(request, messages.INFO, mark_safe("transfered to actual project to <a href='/admin/psm/project/%s'>%s</a>" % (new_proj.id, new_proj.code) ))

    def has_approve_permission(self):
        user = User.objects.get(username="testuser1")
        user.has_perm('psm.approve')
        return True

    # def f_est_cost(self, instance):
    #     return '{0:,}'.format(self.est_cost)
# ===================================================================================================
@admin.register(Project)
class ProjectAdmin(ImportExportMixin, admin.ModelAdmin):
    class Meta:
        import_id_fields = ('id',)
        exclude = ()
    class Media:
        css = {
        'all': ('psm/css/custom_admin.css',),
    }    
    list_display = ('pjcode', 'title', 'pm', 'dept', 'phase', 'state', 'CBU_str', )    #CBU many to many
    list_display_links = ('pjcode', 'title')
    list_editable = ("phase", 'state',)
    search_fields = ('id', 'title', 'description', 'objective', 'resolution', 'code', 'wbs__wbs', 'es', 'ref', 'pm__name', 'CBUpm__name', 'CBUs__name')     #FIXME many to many
    list_filter = (
        ('status_o', UnionFieldListFilter),
        ('year', DropdownFilter),
        ('phase', UnionFieldListFilter),
        ('state', UnionFieldListFilter),
        ('CBUs', RelatedDropdownFilter),   #FIXME many to many
        ('dept', RelatedDropdownFilter),
        ('dept__div', RelatedDropdownFilter), #FIXME dept__div not working
        ('priority', UnionFieldListFilter),
        ('req_pro', DropdownFilter),
        # ('req_sec', DropdownFilter),
        # ('req_sec', DropdownFilter),
        
#        'deadline'
    )
    ordering = ['-id']  #Project_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'lstrpt',  'link', )
    autocomplete_fields = ['pm', 'CBUs', 'strategy', 'CBUpm', 'program']

    fieldsets = (               # Edition form
        (None,  {'fields': (('title', 'type', 'year', ), 
                            ('state', 'phase', 'progress', 'priority'), 
                            ('status_o', 'status_t', 'status_b', 'status_s', 'lstrpt', 'resolution'), 
                            ), "classes": ("stack_labels",)}),
        (_('Detail...'),  {'fields': (('strategy', 'program', 'is_agile'), ('CBUs', 'CBUpm', 'ref'),('pm', 'dept', ), 
                            ( 'est_cost', 'app_budg', 'wbs', 'es', 'is_unplanned', 'is_internal' ), ('description', 'objective'), 
                                       ), 'classes': ('collapse',)}),
        (_('Schedule...'),  {'fields': (('p_ideation','p_plan_b','p_plan_e','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                                        ('a_plan_b','a_plan_e','a_kickoff','a_design_b','a_design_e','a_dev_b','a_dev_e','a_uat_b','a_uat_e','a_launch','a_close'), 
                                       ), 'classes': ('collapse',)}),
        (_('Communication...'),  {'fields': (('email_active'), ('recipients_to',), ), 'classes': ('collapse',)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'), ('req_pro','req_sec','req_inf'), ), 'classes': ('collapse',)}),
        # (None, {'fields': (('link',),) })
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('title', 'type', 'year'), ('strategy', 'program','is_agile'), 
                            ('CBUs', 'CBUpm', 'ref', 'is_unplanned', ), ('pm', 'dept', ), 
                            ( 'est_cost', 'app_budg', 'wbs', 'es', 'is_internal' ),
                            ('state', 'phase', 'progress', 'priority'), ('description', 'objective'), 
                            ('p_ideation', 'p_plan_b','p_plan_e','p_kickoff','p_design_b','p_design_e','p_dev_b','p_dev_e','p_uat_b','p_uat_e','p_launch','p_close'),
                            # ('req_pro','req_sec','req_inf'), 
                            # 'attachment'
                        )}),
            )
        return fieldsets

    inlines = [ProjectDeliverableInline]
    
    # easier option for admin-actions: https://pypi.org/project/django-object-actions/
    # https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#overriding-vs-replacing-an-admin-template
    change_form_template = 'admin/psm/project/change_form.html'

    # https://stackoverflow.com/questions/19542295/overridding-django-admins-object-tools-bar-for-one-model
    # change_list_template = 'admin/psm/project/change_list.html'

    # admin/base_site.html - field-link { display: none;}    
    def link(self, obj):
        return mark_safe(f"<a class='btn btn-outline-success p-1 my-admin-link' style='color:fff' href='/admin/reports/report/?project__id__exact={obj.id}'> GO TO project report list </a>")
    link.short_description = 'Links'        
    # the following is necessary if 'link' method is also used in list_display
    # link.allow_tags = True

    def formatted_updated(self, obj):
        return obj.updated_on.strftime("%m/%d/%y")
    formatted_updated.short_description = 'Updated'

    def cbu_list(self, obj):
        return " ,".join(p.name for p in obj.CBUs.all())
    cbu_list.short_description = 'CBUs'

    #not working...https://stackoverflow.com/questions/46892851/django-simple-history-displaying-changed-fields-in-admin

    # formfield_overrides = {
    #     models.TextField: {
    #         'widget': Textarea(attrs={'rows': 4, 'cols': 80})
    #     }
    # }
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)

        form.base_fields['description'].widget.attrs.update({'rows':5,'cols':80})
        if  obj:    #change
            form.base_fields['resolution'].widget.attrs.update({'rows':5,'cols':40})
            form.base_fields['recipients_to'].widget.attrs.update({'rows':6,'cols':800})
            # form.base_fields['recipients_cc'].widget.attrs.update({'rows':5,'cols':120})      #not yet implemented
            form.base_fields["recipients_to"].help_text = 'Use semi-colon to add multiple. Example: "Johnny Test" <johnny@test.com>; Jack <another@test.com>; "Scott Summers" <scotts@test.com>; noname@test.com'
            # form.base_fields["is_agile"].help_text = 'Mark if the project requires multiple launches'
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
        from psmprj.utils.mail import combine_to_addresses
        if change is False:  #when create
            obj.created_by = request.user

            # if not obj.code: #not migration 
            #     obj.code = f'{obj.year % 100}-{"{:04d}".format(obj.pk+1000)}'
        # else:
            # if (obj.recipients_to):
            #     obj.recipients_to = combine_to_addresses( obj.emails_to )   #comma separated... problem

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
                    update_dic = { 'project' : obj, 'CBUs' : obj.CBUs, 'dept' : obj.dept, 'state' : upd[1] }  #FIXME many to many
                    theproc.update(**update_dic)
                    messages.add_message(request, messages.INFO, '[' + upd[0][3:] + '] review type records are updated.')

                elif upd[1] == State3.YES.value: #not exist and when target is YES only
                    new_reviews.append(upd[0]) 

        if new_reviews:
            # breakpoint()
            for new in new_reviews:
                Review.objects.create(reviewtype = new, project = obj, CBU = obj.CBU, dept = obj.dept, onboaddt = obj.p_kickoff, 
                                      state = obj.req_pro, priority = obj.priority, title = obj.title)
                messages.add_message(request, messages.INFO, '[' + new[3:] + '] review type - New review request is created' )

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


    actions = ['duplicate_project']
    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_project(self, request, queryset):
        for object in queryset:
            object.id = None
            object.title = object.title + " copied"
            object.save()
            messages.add_message(request, messages.INFO, ' is copied/saved')


    
# https://adriennedomingus.medium.com/adding-custom-views-or-templates-to-django-admin-740640cc6d42

