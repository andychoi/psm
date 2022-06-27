import urllib
from datetime import date
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import mark_safe
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from import_export.admin import ImportExportMixin
from django_object_actions import DjangoObjectActions

from .models import Skill, Resource, ResourcePlan, ProjectPlan, RPPlanItem
from common.dates import workdays_us
# Register your models here.

@admin.register(Skill)
class SkillAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ( 'name', 'level', 'group', 'description', 'is_active')
    list_display_links = ('name',)
    list_editable = ('is_active',)
    ordering = ('name',)
    search_fields = ('name','group', 'description')


@admin.register(Resource)
class ResourceAdmin(ImportExportMixin, DjangoObjectActions, admin.ModelAdmin):
    list_display = ( 'staff', 'year', 'active', 'm01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12', 'skill_names')
    list_display_links = ('staff',)
    list_editable = ('active','m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12')
    readonly_fields = ('created_at', 'created_by', 'updated_on', 'updated_by', )
    ordering = ('staff',)
    autocomplete_fields = ('skills',)

    class Media:
        css = {"all": ("resource/css/custom_admin.css",)}

    fieldsets = (      # Edition form
                (None,  {'fields': ( ('staff', 'year',), ('skills', 'active',),  
                ('m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12') )}),
                (_('More...'), {'fields': ( ('created_at', 'created_by', 'updated_on', 'updated_by' )), 'classes': ('collapse',)}),
            )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None,  {'fields': ( ('staff', 'year',), ('skills', 'active',),  
                ('m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12') )  }),
            )
        return fieldsets

    list_filter = (
        ('year',            DropdownFilter),
        ('staff__dept',   RelatedDropdownFilter),
        ('staff__team',   RelatedDropdownFilter),
        ('staff__dept__div',   RelatedDropdownFilter),
    )

    change_actions = ('fill_default_workdays',)
    # object-function
    def fill_default_workdays(self, request, obj):
        months = [ [m, f'm{m:02d}'] for m in range(1, 13)]
        for m, f in months:
            days = workdays_us(m, y=obj.year)    # if m <= 12 else obj.year+1)
            setattr(obj, f, days)  # overwriting the old value        pass
        obj.save()

    # list function
    actions = ['fill_default_workdays_batch', 'copy_to_next_year']
    
    @admin.action(description='Fill from company calendar')
    def fill_default_workdays_batch(self, request, queryset):
        for obj in queryset:
            months = [ [m, f'm{m:02d}'] for m in range(1, 13)]
            for m, f in months:
                days = workdays_us(m, y=obj.year)    # if m <= 12 else obj.year+1)
                setattr(obj, f, days)  # overwriting the old value
            obj.save()            
            messages.add_message(request, messages.INFO, 'Capacity days are filled with company calendar')

    @admin.action(description="Copy to next year", permissions=['change'])
    def copy_to_next_year(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.year = obj.year + 1
            obj.save()
            messages.add_message(request, messages.INFO, ' is copied/saved')

    #FIX conflict with DjangoObjectActions, import/export
    changelist_actions = ['redirect_to_export', 'redirect_to_import']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_export.label = "Import"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser :
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

"""
    This is for admin only, not intended for staff access
    
"""
@admin.register(RPPlanItem)
class RPPlanItemAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ( 'r_no', 'r_staff', 'project', 'p_no', 'p_proj', 'staff', 'year', 'm01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12')
    list_display_links = ('year',)

    readonly_fields = ('r_staff', 'p_proj', 'created_at', 'created_by', 'updated_on', 'updated_by', )
    autocomplete_fields = ('pp', 'pr', 'project', 'staff')
    extra_field = forms.CharField()

    fieldsets = (      # Edition form
                (None,  {'fields': ( ('r_staff', 'project',), ('p_proj', 'staff',), ( 'year',  ), 
                # (None,  {'fields': ( ('project',), ('staff',), ( 'year', 'status', ), 
                ('m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12') )}),
                (_('More...'), {'fields': ( ('created_at', 'created_by', 'updated_on', 'updated_by' )), 'classes': ('collapse',)}),
            )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None,  {'fields': ( ('pr', 'pp'), ( 'year', ), 
                ('m01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08', 'm09', 'm10', 'm11', 'm12') )  }),
            )
        return fieldsets

    # tip save_model
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# https://stackoverflow.com/questions/61424405/django-query-set-for-sums-records-each-month
"""
    Project resource capacity planning by PM
    1. validate resource's total capacity
    2. 
"""
class ProjectPlanInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super(ProjectPlanInlineFormSet, self).clean()
        
        # totals = list(0 for m in range(1, 13))
        # for form in self.forms:
        #     if not form.is_valid():
        #         return #other errors exist, so don't bother
        #     if form.cleaned_data and not form.cleaned_data.get('DELETE'):

        #         # only check for future month
        #         months = [ [m, f'm{m:02d}'] for m in range(date.today().month+1, 13)]
        #         for k, v in months:
        #             totals[k-1] += form.cleaned_data[v]

        # for v in totals:
        #     if v > Resource.MAX_MM:
        #         raise forms.ValidationError('Capacity exceed 100%')


class ProjectPlanForm(forms.ModelForm):
    class Meta:
        model = RPPlanItem
        exclude = ()
    
    # def clean_<field_name>(self):
    def clean(self):
        if not self.cleaned_data.get('pr') is None and self.cleaned_data and not self.cleaned_data.get('DELETE'):
        # check for old period change
            months = [ [m, f'm{m:02d}'] for m in range(1, date.today().month+1)]
            for k, v in months:
                if v in self.changed_data:
                    raise forms.ValidationError('You cannot change past period')
        return self.cleaned_data                     


class ProjectPlanInline(admin.TabularInline):
    model = RPPlanItem
    form = ProjectPlanForm
    formset = ProjectPlanInlineFormSet  
    extra = 3
    autocomplete_fields = [ 'staff',]
    exclude = ['project', 'year', 'created_by', 'updated_by']

    class Media:
        css = {"all": ("resource/css/custom_admin.css",)}


@admin.register(ProjectPlan)
class ProjectPlanAdmin(admin.ModelAdmin):
    list_display = ( 'project', 'year', 'status','preview_link')
    list_display_links = ('project',)
    list_editable = ('status',)
    ordering = ('project',)
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('project', )     #TO-RE search line item
    autocomplete_fields = [ 'project',]

    fieldsets = (      # Edition form
        (None,  {'fields': ( ('project', 'year', 'status', ) )  }),
            (_('More...'), {'fields': (('created_at', 'created_by'), ('updated_on', 'updated_by'),), 'classes': ('collapse',)}),
    )
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': ( ('project', 'year' ) , ( 'status', ) )}),
            )
        return fieldsets

    list_filter = (
        ('year',            DropdownFilter),
        ('project__pm',     RelatedDropdownFilter),
        ('project__dept',   RelatedDropdownFilter),
        ('project__team',   RelatedDropdownFilter),
        ('project__CBUs',   RelatedDropdownFilter),
        ('project__dept__div', RelatedDropdownFilter),
    )
    inlines = [ProjectPlanInline]

    # TODO
    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectPlanAdmin, self).get_form(request, obj, **kwargs)
        if hasattr(form, 'base_fields'):
            # form.base_fields['staff'  ].initial = request.user.profile
            form.base_fields['project'].widget.attrs.update({'style': 'width: 400px'})
        return form

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)

    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)
    
    # tip access to own data, queryset - TODO for manager/HOD
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.profile.is_psmadm:
            return qs
        return qs.filter(created_by=request.user)

    # tip save_model save_related
    # https://stackoverflow.com/questions/14931865/what-is-the-diff-between-save-model-and-save-formset-in-django-admin
    # def save_related(self, request, form, formsets, change):

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_formset
    # tip save_form save_formset - should be in parent model, not child
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)  # this will save the children
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:  # child
            if change is False:     # create
                instance.created_by = request.user
                instance.updated_by = request.user
            else:
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()
        formset.save()        

"""
    Staff's available allocation plan
"""
class ResourcePlanInlineFormSet(forms.models.BaseInlineFormSet):

    def clean(self):
        super(ResourcePlanInlineFormSet, self).clean()
        
        # https://stackoverflow.com/questions/61424405/django-query-set-for-sums-records-each-month
        totals = list(0 for m in range(1, 13))
        for form in self.forms:
            if not form.is_valid():
                return #other errors exist, so don't bother
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):

                # only check for future month
                months = [ [m, f'm{m:02d}'] for m in range(date.today().month+1, 13)]
                for k, v in months:
                    totals[k-1] += form.cleaned_data[v]

        for v in totals:
            if v > Resource.MAX_MM:
                raise forms.ValidationError('Capacity exceed 100%')


class ResourcePlanForm(forms.ModelForm):
    class Meta:
        model = RPPlanItem
        exclude = ()
    
    # def clean_m07(self):
    #     if self.cleaned_data.get('pr').pk:     # chekc change mode
    #         rp = ResourcePlan.objects.get(pk=self.cleaned_data.get('pr').id)
    #         if 'm07' in self.changed_data and ( date.today().year > rp.year or int(date.today().month) > 7):
    #             raise forms.ValidationError('You cannot change past period')
    #     return self.cleaned_data.get('m07')

    def clean(self):
        if not self.cleaned_data.get('pr') is None and self.cleaned_data and not self.cleaned_data.get('DELETE'):
        # check for old period change
            months = [ [m, f'm{m:02d}'] for m in range(1, date.today().month+1)]
            for k, v in months:
                if v in self.changed_data:
                    raise forms.ValidationError('You cannot change past period')
        return self.cleaned_data                     

class ResourcePlanInline(admin.TabularInline):
    model = RPPlanItem
    form = ResourcePlanForm
    formset = ResourcePlanInlineFormSet  
    extra = 3
    autocomplete_fields = [ 'project',]
    exclude = ['staff', 'year', 'created_by', 'updated_by' ]

    class Media:
        css = {"all": ("resource/css/custom_admin.css",)}

# Register your models here.
@admin.register(ResourcePlan)
class ResourcePlanAdmin(admin.ModelAdmin):
    list_display = ( 'staff', 'year', 'status','preview_link')
    list_display_links = ('staff',)
    list_editable = ('status',)
    ordering = ('staff',)
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by')
    search_fields = ('staff', )     #TO-RE search line item
    autocomplete_fields = [ 'staff',]

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
        # ('div', RelatedDropdownFilter),
        ('staff__dept', RelatedDropdownFilter),
        ('staff__team', RelatedDropdownFilter),
        # ('status', RelatedDropdownFilter),
    )
    inlines = [ResourcePlanInline]

    # TODO
    def preview_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="blank">Preview</a>' % reverse('report_detail', args=[obj.pk]))
    preview_link.short_description = _('Preview')

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)
    
    # tip access to own data, queryset - TODO for manager/HOD
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.profile.is_psmadm:
            return qs
        return qs.filter(created_by=request.user)

    # tip save_model save_related
    # https://stackoverflow.com/questions/14931865/what-is-the-diff-between-save-model-and-save-formset-in-django-admin
    # def save_related(self, request, form, formsets, change):
    #     form.save_m2m()
        # for formset in formsets:
        #     self.save_formset(request, form, formset, change=change)
        # if change is False:
        #     form.created_by, form.updated_by = request.user
        # else:
        #     form.updated_by = request.user
        # super().save_related(request, form, formsets, change)


    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_formset
    # tip save_form save_formset - should be in parent model, not child
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)  # this will save the children
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:  # child
            if change is False:     # create
                instance.created_by = request.user
                instance.updated_by = request.user
            else:
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()
        formset.save()
        # form.instance.save() # form.instance is the parent


    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d  was successfully marked as published.',
            '%d  were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

    # tip initial default version set
    # below fail... ------------------------------------------------------------------------------------------
    # initial values from GET parameters. For instance, ?name=initial_value will set the name field’s initial value to be initial_value.
    def get_changeform_initial_data(self, request):
        return {'staff': request.user.profile}
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(ResourcePlanAdmin, self).get_form(request, obj, **kwargs)
    #     if hasattr(form, 'base_fields'):
    #         # form.base_fields['staff'  ].initial = request.user.profile
    #         form.base_fields['project'].widget.attrs.update({'style': 'width: 400px'})
    #     return form
    # below fail... ------------------------------------------------------------------------------------------
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'staff':
    #         kwargs['initial'] = request.user.id
    #         # kwargs['disabled'] = True
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # list with default filter
    # TODO for manager/HOD, default to own plan (created_by)
    def changelist_view(self, request, extra_context=None):
        if not request.user.is_superuser:

            ltmp = request.GET.get('created_by__id__exact', '')
            if len(ltmp) == 0:
                q =  {k:v for k, v in request.GET.items() if v and hasattr(ResourcePlan, k.split('__')[0] ) }
                if q:    
                    get_param = f"created_by__id__exact={request.user.id}&{urllib.parse.urlencode(q)}"
                else:
                    get_param = f"created_by__id__exact={request.user.id}"
                return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        
        return super(ResourcePlanAdmin, self).changelist_view(request, extra_context=extra_context)

