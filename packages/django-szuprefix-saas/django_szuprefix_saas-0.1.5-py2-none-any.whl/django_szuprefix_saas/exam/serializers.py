# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from rest_framework import serializers
from . import models
from ..saas.mixins import PartySerializerMixin


class PaperSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Paper
        fields = ('title', 'content', 'content_object', 'is_active', 'create_time', 'id')



class StatSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Stat
        fields = ('detail',)

class PerformanceSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Performance
        fields = ('paper_id', 'score', 'detail')


class AnswerSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Answer
        fields = ('detail', 'performance', 'seconds')



class StatSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Stat
        fields = ('detail',)


class PerformanceSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Performance
        fields = ('paper_id', 'score', 'detail')

