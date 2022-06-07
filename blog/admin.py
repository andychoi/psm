from django.contrib import admin
from django.contrib import messages
from .models import Post    #, Comment
from django.utils.translation import ngettext

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'featured', 'private', 'date_posted')
    list_display_links = ('id', 'title')
    list_filter = ('featured', 'private', 'category', 'author', 'date_posted')
    search_fields = ('id', 'title', 'content', 'author__profile__name')    
    list_per_page = 20

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



admin.site.register(Post, PostAdmin)




# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'author', 'post',
#                     'approved_comment', 'created_date')
#     list_display_links = ('id', 'author', 'post')
#     list_filter = ('author', 'created_date')
#     list_editable = ('approved_comment', )
#     search_fields = ('author', 'post')
#     list_per_page = 20


# admin.site.register(Comment, CommentAdmin)
