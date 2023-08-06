#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, help_text='id')
    name = serializers.CharField(required=False, help_text=u'姓名')

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        content_type = validated_data.get('content_type')
        if not content_type:
            content_type = ContentType.objects.filter(id=validated_data.get('content_type_id')).first()
        obj = None
        if content_type:
            obj = content_type.get_object_for_this_type(pk=validated_data.get('object_id'))
        validated_data['content_object'] = obj
        return super(CommentSerializer, self).create(validated_data)
