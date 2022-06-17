from django.contrib import admin
from django.contrib import messages
from .models import Post, Tag     #, Comment
from django.utils.translation import ngettext
from django.shortcuts import redirect
from django.contrib.admin import helpers

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'slug' )
    search_fields = ('id', 'tag', 'slug')    
    prepopulated_fields = {"slug": ("tag",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'tags_', 'author', 'status', 'featured', 'private', )
    list_display_links = ('id', 'title')
    list_filter = ('featured', 'private', 'category', 'author', 'date_posted')
    list_editable = ( 'status', 'featured', 'private')
    search_fields = ('id', 'title', 'content', 'author__profile__name')    
    list_per_page = 20
    autocomplete_fields = ('tags',)
    prepopulated_fields = {"slug": ("title",)}  # as type in Title, slug is populated

    def save_model(self, request, obj, form, change):
        if change is False: #create
            if not obj.author:  
                obj.author = request.user
        # default from content...
        # if not obj.excerpt: #if blank, then fill from content
        #     obj.excerpt = obj.content.strip()[:300] + ' ...'

        super().save_model(request, obj, form, change)

    actions = ['make_published', 'duplicate_post']
    @admin.action(description='Mark selected as published', permissions=['change'])
    def make_published(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d  was successfully marked as published.',
            '%d  were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Duplicate selected record", permissions=['change'])
    def duplicate_post(self, request, queryset):
        for object in queryset:
            object.id = None
            object.title = object.title + " copied"
            object.save()
            messages.add_message(request, messages.INFO, ' is copied/saved')


# Image copy & paste
# https://stackoverflow.com/questions/43481931/how-to-upload-an-image-through-copy-paste-using-django-modelform
# https://stackoverflow.com/questions/66846390/django-admin-save-image-like-base64

# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'author', 'post',
#                     'approved_comment', 'created_date')
#     list_display_links = ('id', 'author', 'post')
#     list_filter = ('author', 'created_date')
#     list_editable = ('approved_comment', )
#     search_fields = ('author', 'post')
#     list_per_page = 20


#TIP conditional read-only
    # def get_readonly_fields(self, request, obj=None):
    #     if obj is not None:  # You may have to check some other attrs as well
    #         # Editing an object
    #         return ('comment', 'created_by')
    #     else:
    #         # Creating a new object
    #         return ('created_by',)


from .models import Ticket, TicketComment
from django.db import models

# refer this technique: https://stackoverflow.com/questions/5619120/readonly-for-existing-items-only-in-django-admin-inline
# class TicketCommentHistInline(admin.TabularInline):
#     model = TicketComment
#     extra = 0
#     readonly_fields = ['comment', 'created_by', ]

#     def has_add_permission(self, request, obj=None):
#         return False
        
class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    readonly_fields=('created_by',)
    fields = [ "comment", "created_by"] 
    extra = 0
    class Media:
        css = {"all": ("blog/css/custom_admin.css",)}

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    model = Ticket

    inlines = [
        # TicketCommentHistInline, TicketCommentInline,
        TicketCommentInline,
    ]    

    search_fields = ('id', 'title', 'description', )
    list_display = ('title', 'short_desc', 'ticket_type', 'priority', 'state', 'updated_on'  )
    list_display_links = ('title',)
    # list_editable = ("state", )
    list_filter = ('ticket_type', 'priority', 'state',)
    
    # readonly_fields = ('created_at', 'updated_on', 'created_by', )
    custom_fields = [ ('ticket_type', 'priority',  ), 
                    ('title',), ('description', ), 
                    ('state',), ]
    fieldsets = (               # Edition form
        (None,  {'fields': custom_fields 
                , "classes": ("stack_labels",)}),
        ('More...', {'fields': ( ('created_at', 'updated_on'), ('created_by', 'updated_by') ), 'classes': ('collapse',)}),
    )

    def short_desc(self, obj):
        return obj.description[:100]


    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.custom_fields  }), )

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # update on related object - comment
    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            if formset.model == TicketComment:
                for formline in formset.forms:
                    comment = formline.instance
                    if comment.id is None: # formline["id"] is None:     #create
                        comment.created_by = request.user            
                
                instances = formset.save(commit=False)

        super(TicketAdmin, self).save_related(request, form, formsets, change)

    # default filter to exclude closed ticket
    def changelist_view(self, request, extra_context=None):
        if len(request.GET) == 0:
            get_param = "state__exact=UN"
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(TicketAdmin, self).changelist_view(request, extra_context=extra_context)

    # If you wanted to manipulate the inline forms, to make one of the fields read-only:
    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(
                inline, formset, fieldsets, prepopulated, readonly,
                model_admin=self,
            )

            if isinstance(inline, TicketCommentInline):
                for form in inline_admin_formset.forms:
                #Here we change the fields read only.  widget.attrs - class
                    if not form.instance.id is None:
                        # form.fields['comment'].widget.attrs['readonly'] = True
                        form.fields['comment'].disabled = True
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets

