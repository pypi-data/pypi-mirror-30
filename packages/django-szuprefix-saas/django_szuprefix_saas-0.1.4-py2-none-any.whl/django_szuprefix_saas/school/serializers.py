# -*- coding:utf-8 -*-
from . import models, mixins
from rest_framework import serializers

__author__ = 'denishuang'


class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.School
        fields = ('name', 'type', 'create_time', 'url')


class TeacherSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('name', 'url')


class GradeSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Grade
        fields = ('id', 'name', 'url')


class SessionSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Session
        fields = ('id', 'name', 'url')


class ClazzSerializer(mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    # grade = serializers.SlugRelatedField(slug_field='name', queryset=models.Grade.objects.all())
    # entrance_session = serializers.SlugRelatedField(slug_field='name', queryset=models.Session.objects.all())

    class Meta:
        model = models.Clazz
        fields = ('id', 'name', 'entrance_session', 'number', 'primary_teacher', 'grade', 'teacher_names')


class ClazzSmallSerializer(mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Clazz
        fields = ('id', 'name', 'grade', 'entrance_session', 'url')


class StudentSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    # grade = GradeSerializer()
    # clazz = ClazzSmallSerializer()

    class Meta:
        model = models.Student
        fields = ('name', 'number', 'clazz', 'grade', 'url')


class StudentBindingSerializer(serializers.Serializer):
    mobile = serializers.CharField(label="手机号", required=True)
    number = serializers.CharField(label="学号", required=True)
    name = serializers.CharField(label="姓名", required=True)
    the_id = serializers.IntegerField(label="指定ID", required=False)

    def validate(self, data):
        mobile = data['mobile']
        number = data['number']
        name = data['name']
        the_id = data.get('the_id')
        qset = models.Student.objects.filter(number=number, name=name)
        ss = []
        for s in qset:
            user = s.user
            if hasattr(user, 'as_person') and getattr(user, 'as_person').mobile == mobile:
                if not the_id or s.id == the_id:
                    ss.append(s)
        if not ss:
            raise serializers.ValidationError("相关账号不存在, 可能查询信息不正确, 或者还未录入系统")
        elif len(ss) == 1:
            user = ss[0].user
            if user.has_usable_password():
                raise serializers.ValidationError("该帐号已绑定过,不能重复绑定")
        data['students'] = ss
        return data

    def save(self, newUser):
        students = self.validated_data['students']
        if len(students) == 1:
            user = students[0].user
            from django_szuprefix.utils.modelutils import move_relation
            move_relation(user, newUser)
        return students
