from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from common.utils import *
# from psm.models import Project
from common.proxy import ProxySuper,  ProxyManager
# https://pillow.readthedocs.io
# from PIL import Image  #performance issue https://placeholder.com/900x300

#avoid circular import, use full name in model with ''. example='common.Team'

class Profile(ProxySuper): #models.Model):
    proxy_name = models.CharField(max_length=20, default='Profile', blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True) #FIXME - dump during User creation, unique=True)
    email = models.EmailField(max_length=150, blank=True, null=True, unique=False)
    # is_active = models.BooleanField(default=True)
    pm_count    = models.SmallIntegerField(_('PM counts'), default=0)
    # report_to   = models.ForeignKey('Profile', verbose_name=_('manager'), related_name='report_to', on_delete=models.CASCADE, null=True, blank=True)

    # extra attribute from AD
    job         = models.CharField(max_length=50, null=True, blank=True)
    department  = models.CharField(max_length=50, null=True, blank=True)
    manager     = models.CharField(max_length=50, null=True, blank=True)
    mobile      = models.CharField(max_length=16, null=True, blank=True)
    
    #FIXME circular dependency...??
    team = models.ForeignKey('common.Team', verbose_name=_('Team'), on_delete=models.SET_NULL, blank=True, null=True)
    dept = models.ForeignKey('common.Dept', verbose_name=_('Dept'), on_delete=models.SET_NULL, blank=True, null=True)
    CBU    = models.ForeignKey('common.CBU',  verbose_name=_('CBU'),  on_delete=models.SET_NULL, blank=True, null=True)

    is_external = models.BooleanField(_("External user?"), default=False)
    is_psmadm   = models.BooleanField(_("PSM Admin?"), default=False)

    #multi-select... FIXME
    is_pro_reviewer = models.BooleanField(_("Procurement reviewer?"), default=False)
    # is_sec_reviewer = models.BooleanField(_("Security reviewer?"), default=False)
    # is_inf_reviewer = models.BooleanField(_("Infrastructure reviewer?"), default=False)
    # is_app_reviewer = models.BooleanField(_("App_Architect?"), default=False)
    # is_mgt_reviewer = models.BooleanField(_("Management reviewer?"), default=False)

    image = models.ImageField(upload_to='profile_pics', null=True, blank=True)  #default='default.jpg', 
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name="profile_created", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(User, related_name="profile_updated", null=True, on_delete=models.SET_NULL)
    id_auto = models.BooleanField(_("User create from Profile"), default=False )    #auto creation of user from profile creation

    notes      = models.CharField(_("notes"), max_length=500, null=True, blank=True)
    migrated   = models.CharField(_("migrated"), max_length=10, null=True, blank=True)

    def __str__(self):
        if getattr(self, 'user') and not self.name :
            return "%s [%s]" % ("%s %s" % (self.user.first_name, self.user.last_name), self.CBU) 
        else:
            return "%s [%s]" % (self.name, self.CBU)    #preferred

    class Meta:
        # app_label = 'auth'  #circular dependency... FIXME
        # ordering = ['-CBU', 'name']
        permissions = [ ('admin', 'Can admin user'),
        ]        

    # @property
    # def username(self):
    #     return self.name
    @property
    def sname(self):
        return self.name.split(',')[1] if len(self.name.split(','))>1 else self.name

    @property
    def u_div(self):
        return self.dept.div if (self.dept.div) else None

    # def create_user_profile(sender, instance, created, **kwargs):
    #     Profile.objects.get_or_create(user=instance)
    # post_save.connect(create_user_profile, sender=User)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def save(self, *args, **kwargs):
        # self.pm_count = Project.objects.filter(pm=self).count()
        super(Profile, self).save(*args, **kwargs)

    # models.FileField(upload_to=wrapper)
    # def wrapper(user, filename):
    #     file_upload_dir = os.path.join(settings.MEDIA_ROOT, 'file_upload')
    #     if os.path.exists(file_upload_dir):
    #         import shutil
    #         shutil.rmtree(file_upload_dir)
    #     return os.path.join(file_upload_dir, filename)


        # img = Image.open(self.image.path)
        # if img.height > 150 or img.width > 150:
        #     output_size = (150, 150)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)

class ProfileCBU(Profile):
    class Meta:
        proxy = True
        # app_label = 'auth'   # admin menu location
        verbose_name = _("Profile CBU")
        verbose_name_plural = _("Profile CBU")

    objects = ProxyManager()

# class ProfileEmp(Profile):
#     class Meta:
#         proxy = True

#     objects = ProxyManager()
