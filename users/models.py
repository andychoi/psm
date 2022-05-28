from django.db import models
from django.contrib.auth.models import User
# https://pillow.readthedocs.io
# from PIL import Image  #performance issue https://placeholder.com/900x300
from django.utils.translation import gettext_lazy as _
from common.utils import *

#avoid circular import, use full name in model with ''. example='common.Team'
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from common.models import Team, Dept, Div
# from common.models import Team, Dept, Div

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
    manager = models.ForeignKey(User, verbose_name=_('manager'), related_name='report_to', on_delete=models.CASCADE, null=True, blank=True)
    u_team = models.ForeignKey('common.Team', verbose_name=_('Team'), on_delete=models.SET_NULL, blank=True, null=True)
    u_dept = models.ForeignKey('common.Dept', verbose_name=_('Dept'), on_delete=models.SET_NULL, blank=True, null=True)
    u_div = models.ForeignKey('common.Div', verbose_name=_('Div'), on_delete=models.SET_NULL, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES, default="USER")
    is_external = models.BooleanField(_("External user?"), default=False)
    is_active = models.BooleanField(default=True)

    #multi-select... FIXME
    is_pro_reviewer = models.BooleanField(_("Procurement reviewer?"), default=False)
    is_sec_reviewer = models.BooleanField(_("Security reviewer?"), default=False)
    is_inf_reviewer = models.BooleanField(_("Infrastructure reviewer?"), default=False)
    is_app_reviewer = models.BooleanField(_("App_Architect?"), default=False)
    is_mgt_reviewer = models.BooleanField(_("Management reviewer?"), default=False)

    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    created_on = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name="profile_created", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last modified"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(User, related_name="profile_updated", null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        if getattr(self, 'user'):
            return self.user.username 
        else:
            return self.name

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        # img = Image.open(self.image.path)
        # if img.height > 150 or img.width > 150:
        #     output_size = (150, 150)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)

    # def __str__(self):
    #     # FIXME
    #     return getattr(self.user, 'username', self.name)
