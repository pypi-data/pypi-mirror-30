# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django_szuprefix_saas.saas.models import Party

def auto_code(n):
    from unidecode import unidecode
    return "".join([a[0] for a in unidecode(n).split(" ") if a]).upper()

class CodeMixin(object):
    def save(self, **kwargs):
        if not self.code:
            self.code = auto_code(self.name)
        return super(CodeMixin, self).save(**kwargs)

class Manufacturer(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "厂家"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_manufacturers",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.name


class Vendor(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "卖家"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_vendors",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.name


class Product(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "产品"
        ordering = ('-create_time',)
        unique_together = ('party', 'manufacturer', 'name', 'number')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_products",
                              on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=Manufacturer._meta.verbose_name, null=True, blank=True,
                                     related_name="products", on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=255)
    code = models.CharField("代码", max_length=64, blank=True, default="")
    number = models.CharField("型号", max_length=255)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.name, self.number)


class Quote(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "报价"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="quote_quotes",
                              on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor, verbose_name=Vendor._meta.verbose_name, related_name="quotes",
                               on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=Product._meta.verbose_name, related_name="quotes",
                                on_delete=models.PROTECT)
    unit_price = models.DecimalField("单价", decimal_places=2, max_digits=10)
    delivery = models.CharField("货期", max_length=32)
    delivery_days_from = models.PositiveIntegerField("货期最短天数", blank=True, default=0)
    delivery_days_to = models.PositiveIntegerField("货期最长天数", blank=True, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        from . import helper
        self.delivery_days_from, self.delivery_days_to = helper.split_delivery_days(self.delivery)
        return super(Quote, self).save(**kwargs)