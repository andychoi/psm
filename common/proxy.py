import sys
from django.db import models

# https://stackoverflow.com/questions/241250/single-table-inheritance-in-django
#   proxy model -> this is choice here 
#   unmanaged is like a view in database
#   https://stackoverflow.com/questions/7625674/utility-of-managed-false-option-in-django-models
class ProxySuper(models.Model):
    class Meta:
        abstract = True

    proxy_name = models.CharField(max_length=20, default="Project")

    def save(self, *args, **kwargs):
        """ automatically store the proxy class name in the database """
        self.proxy_name = type(self).__name__
        super().save(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        """ create an instance corresponding to the proxy_name """
        proxy_class = cls
        try:
            field_name = ProxySuper._meta.get_fields()[0].name
            proxy_name = kwargs.get(field_name)
            if proxy_name is None:
                proxy_name_field_index = cls._meta.fields.index(
                    cls._meta.get_field(field_name))
                proxy_name = args[proxy_name_field_index]
            proxy_class = getattr(sys.modules[cls.__module__], proxy_name)
        finally:
            return super().__new__(proxy_class)


class ProxyManager(models.Manager):
    def get_queryset(self):
        """ only include objects in queryset matching current proxy class """
        return super().get_queryset().filter(proxy_name=self.model.__name__)

    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, but
        applying the filters passed in "kwargs".
        """
        return self.exclude(pk=pk).filter(**kwargs)

"""
    General purpose object manager
    
    class object_model(models.Model)
        objects = ObjectManager
"""
class ObjectManager(models.Manager):
    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, but
        applying the filters passed in "kwargs".
        """
        return self.exclude(pk=pk).filter(**kwargs)
