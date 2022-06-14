from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify  # new
from django.conf import settings
from common.utils import PUBLISH
from common.utils import md2
import enum
from django.utils.translation import gettext_lazy as _
import markdown2    #https://github.com/trentm/python-markdown2
# from common.proxy import ProxyManager, ProxySuper

class Category(enum.Enum):
    DEFAULT = '00-Default'

CATEGORIES = (
    (Category.DEFAULT.value, Category.DEFAULT.value[3:]),
)

FEATURED = (
	(0, "Default"),
	(1, "Sticky"),
	(2, "Featured"),
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

class Tag(models.Model):
    tag = models.CharField(_("Category"), max_length=20, blank=True, unique=True)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.tag.upper()


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    category = models.CharField(_("Category"), max_length=50, choices=CATEGORIES, default=Category.DEFAULT.value)
    tags  = models.ManyToManyField(Tag, blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)

    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.IntegerField(choices=PUBLISH, default=0) 
    date_posted = models.DateTimeField(default=timezone.now)
    private =  models.BooleanField(default=False)
    featured = models.IntegerField(choices=FEATURED, default=0)
    image = models.ImageField(null=True, blank=True, upload_to='posts//%Y/%m') #default='posts/default.jpg'
    # excerpt = models.TextField(blank=True, null=True)

    # liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    objects = PostManager()

    updated_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-featured', '-date_posted', )

    @property
    def tags_(self):
        return " ,".join(p.tag for p in self.tags.all())

    @property
    def content_md2(self):
        return md2(self.content)
    def content_short_md2(self):
        return md2(self.content[:300] + '...')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.updated_on = timezone.now()
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("post_slug_detail", kwargs={"slug": self.slug})



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

BUG_PRIORITY = (('critical', 'Critical'),
                    ('major', 'Major'),
                    ('medium', 'Medium'),
                    ('minor', 'Minor'),
                    ('trivial', 'Trivial'))
BUG_TYPE = (('bug', 'Bug'),
                ('feature', 'Feature'))
STATE_CHOICES = [
    ('RE','Resolved'),
    ('UN', 'Unresolved')
]

class Ticket(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=64, default=' ', blank=False)
    description = models.TextField(blank=False)
    priority = models.CharField(max_length=8, choices=BUG_PRIORITY, default='trivial')
    ticket_type = models.CharField(max_length=7, choices=BUG_TYPE, default='bug')
    state = models.CharField(max_length=2, choices = STATE_CHOICES, default='UN', blank=True, null=True)
    # state = models.CharField(max_length=2, choices = STATE_CHOICES, default=0, blank=True, null=True)

    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_created_by", editable=False, null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_updated_by", editable=False, null=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.title

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    comment = models.CharField(max_length=512, null=True, blank=True)

    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_comment_created_by", editable=False, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.comment
