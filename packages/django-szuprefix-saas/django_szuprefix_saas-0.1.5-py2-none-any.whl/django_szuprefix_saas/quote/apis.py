# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.decorators import list_route, detail_route
from .apps import Config
from rest_framework.response import Response

__author__ = 'denishuang'
from . import models, serializers
from rest_framework import viewsets
from django_szuprefix.api import register
from ..saas.mixins import PartyMixin

class ManufacturerViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer


register(Config.label, 'manufacturer', ManufacturerViewSet)

class VendorViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer


register(Config.label, 'vendor', VendorViewSet)



class ProductViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


register(Config.label, 'product', ProductViewSet)

class QuoteViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer


register(Config.label, 'quote', QuoteViewSet)
