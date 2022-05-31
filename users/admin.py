from django.contrib import admin
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from common.models import CBU, Div, Dept, Team

#for RAW query
from django.db import connection

# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user')
#     list_display_links = ('id', 'user')
#     list_filter = ('user', )
#     list_per_page = 20
# admin.site.register(Profile, ProfileAdmin)



@admin.register(Profile)
class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
    # list_display = ('id', 'user', 'username', 'email', 'u_team', 'u_dept', 'u_div', 'is_active')
    list_display = ('id', 'user', 'username', 'email', 'is_active')
    list_display_links = ('id', 'user', 'username')
    search_fields = ('id', 'username', 'email', 'user__id', 'user__username') #, 'manager__name') -> dump... why? circular??
    ordering = ('username',)
    readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')

    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'username', 'email') , ('manager', 'is_psmadm', 'is_active'), 
                            # ('u_team','u_dept', 'u_div'), 
                            ('is_external', 'CBU'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',), ('image',), )}),
        (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('username', 'email') , ('manager', 'is_psmadm', 'is_active'), 
                            # ('u_team','u_dept', 'u_div'), 
                            ('is_external', 'CBU'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',), ('image',), ('id_auto') )}),
            )
        return fieldsets

    # validation check
    def clean(self):
        if not self.email and not User.objects.filter(email=self.email).exists():
            raise ValidationError("Email is already registered in User table")

    # use signals.py to sync between User and Profile        
    # def save_model(self, request, obj, form, change):
        # if change is False:     # create
        #     obj.created_by = request.user
        # super().save_model(request, obj, form, change)

    actions = ['sync_user_master']

    @admin.action(description='Migration - create User, link user with email', permissions=['change'])
    def sync_user_master(self, request, queryset):
        
        for obj in queryset:
            #check user with same email
            try:
                found = User.objects.get(email=obj.email) if not obj.email is None else None
            except:
                found = None

            if found and obj.user is None:
                # one-to-one save/update: https://stackoverflow.com/questions/70622890/how-to-assign-value-to-one-to-one-field-in-django
                # 3 methods available
                obj.user = found                  
                obj.save(update_fields=['user'])    
                # Profile.objects.filter(pk=obj.id).update(user=found)   #method 2
                # with connection.cursor() as cursor:                    #method 3
                #     cursor.execute("UPDATE users_profile SET user_id = %s WHERE id = %s", ( found.id, obj.id ) )
                                
                messages.add_message(request, messages.INFO, obj.username + 'is linked with user using email')

            elif not found and obj.user is None:
                user_with_email = False
                try:
                    found = User.objects.get(username=obj.email) if not obj.email is None else None
                except:
                    found = None

                if found:
                    obj.user = found
                    obj.save(update_fields=['user'])    
                    messages.add_message(request, messages.INFO, obj.username + ' already exists with email address as username: ' + obj.email)
                else:
                    #email as username, if not username from profile
                    if obj.email:
                        new_user = User.objects.create_user( username=obj.email, password='demo', email=obj.email )
                        if new_user:
                            obj.user = new_user
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, obj.username + ' is created to user as username: ' + username)
                    else:
                        # causing duplicate key... signal User -> Profile (different username) -> don't create
                        # username = obj.username.lower().replace(" ", "").replace(",",".")
                        # user = User.objects.create_user( username=username, password='demo' )
                        try:
                            found = User.objects.get( username=obj.username )
                        except:
                            found = None
                        # breakpoint()
                        if found:
                            obj.user = found
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, obj.username + ' found in user, linked now')
                        else:
                            messages.add_message(request, messages.INFO, obj.username + ' not found in user, cannot create user without email')


    def __str__(self):
        return self.id if self.username is None else self.username

    class Meta:
        model = Profile
        import_id_fields = ('id',)