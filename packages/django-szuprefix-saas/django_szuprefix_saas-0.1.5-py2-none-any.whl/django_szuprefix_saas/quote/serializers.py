# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from rest_framework import serializers
from . import models
from ..saas.mixins import PartySerializerMixin


class ManufacturerSerializer(PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Manufacturer
        fields = ('name', 'id')


class VendorSerializer(PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Vendor
        fields = ('name', 'id')


class ProductSerializer(PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('name', 'number', 'manufacturer', 'id')


class QuoteSerializer(PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Quote
        fields = ('product', 'vendor', 'unit_price', 'delivery', 'id')


class QuoteListSerializer(PartySerializerMixin, serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField()
    class Meta:
        model = models.Quote
        fields = ('product', 'vendor', 'unit_price', 'delivery', 'id')
