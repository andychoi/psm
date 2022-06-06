from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from common.utils import PUBLISH
import enum
from django.utils.translation import gettext_lazy as _
import markdown2    #https://github.com/trentm/python-markdown2

class Category(enum.Enum):
    DEFAULT = '00-Default'

CATEGORIES = (
    (Category.DEFAULT.value, Category.DEFAULT.value[3:]),
)

class PostManager(models.Manager):
    pass
    # def like_toggle(self, user, post_obj):
    #     if user in post_obj.liked.all():
    #         is_liked = False
    #         post_obj.liked.remove(user)
    #     else:
    #         is_liked = True
    #         post_obj.liked.add(user)
    #     return is_liked


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    category = models.CharField(_("Category"), max_length=50, choices=CATEGORIES, default=Category.DEFAULT.value)

    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.IntegerField(choices=PUBLISH, default=0) 
    date_posted = models.DateTimeField(default=timezone.now)
    private =  models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True, upload_to='posts') #default='posts/default.jpg'
    # excerpt = models.TextField(blank=True, null=True)

    # liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    objects = PostManager()

    updated_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-date_posted', )

    @property
    def md2(self):
        return "<div class='psm-md2'>" + markdown2.markdown(self.content) + "</div>"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.updated_on = timezone.now()
        super(Post, self).save(*args, **kwargs)


# class Comment(models.Model):
#     post = models.ForeignKey(
#         Post, related_name='comments', on_delete=models.CASCADE)
#     author = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_date = models.DateTimeField(default=timezone.now)
#     approved_comment = models.BooleanField(default=True)

#     def approve(self):
#         self.approved_comment = True
#         self.save()

#     def get_absolute_url(self):
#         return reverse("post_list")

#     def __str__(self):
#         return self.author
