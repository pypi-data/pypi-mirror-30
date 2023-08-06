#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django_filters import FilterSet
from .models import Comment


class CommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = {
            'author_id': ['in'],
            'is_valid': ['exact'],
            'email': ['exact'],
            'content_type': ['exact'],
            'object_id': ['in'],
            'public': ['exact']
        }
