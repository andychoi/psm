from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


phones_tr = _("phones")


class CBU(models.Model):
    """
    CBU: Client business unit, A CBU can be a customer, a provider, a contact, you should
    extend this model to add business logic related with your
    CBU's relationship
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("CBU")
        verbose_name_plural = _("CBUs")

    name = models.CharField(_("name"), max_length=10, db_index=True)
    fullname = models.CharField(_("full name"), max_length=200)
    email = models.EmailField(_("email"), blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True)
    is_tier1 = models.BooleanField(_("is Tier-1"), default=False)
    is_company = models.BooleanField(_("is company"), default=True)
#    phone = models.CharField(_("phone"), max_length=40, null=True, blank=True)
#    mobile = models.CharField(_("mobile"), max_length=40, null=True, blank=True)
#    address = models.CharField(_("address"), max_length=128, null=True, blank=True)
    comment = models.TextField(_("notes"), max_length=2000, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='CBU_created', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    def __str__(self):
        return self.name

    # @property
    # def phones(self):
    #     return ", ".join(filter(None, (self.phone, self.mobile)))
