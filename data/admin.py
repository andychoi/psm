from django.contrib import admin
from import_export.admin import ImportExportMixin

from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(ImportExportMixin, admin.ModelAdmin):

    class Meta:
        model = Purchase
        import_id_fields = ('id',)