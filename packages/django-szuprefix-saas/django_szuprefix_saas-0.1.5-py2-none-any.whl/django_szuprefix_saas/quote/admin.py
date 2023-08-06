from django.contrib import admin

from . import models


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)


admin.site.register(models.Manufacturer, ManufacturerAdmin)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)


admin.site.register(models.Vendor, VendorAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'manufacturer')
    raw_id_fields = ('party', 'manufacturer',)


admin.site.register(models.Product, ProductAdmin)


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('product', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("product.name",)
    # readonly_fields = ('party',)


admin.site.register(models.Quote, QuoteAdmin)
