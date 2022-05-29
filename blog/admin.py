from django.contrib import admin
from .models import Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'date_posted')
    list_display_links = ('id', 'title')
    list_filter = ('author', 'date_posted')
    search_fields = ('title', 'content', 'author__profile__name')    
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if change is False and not obj.author:  #create
            obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post',
                    'approved_comment', 'created_date')
    list_display_links = ('id', 'author', 'post')
    list_filter = ('author', 'created_date')
    list_editable = ('approved_comment', )
    search_fields = ('author', 'post')
    list_per_page = 20


admin.site.register(Comment, CommentAdmin)
