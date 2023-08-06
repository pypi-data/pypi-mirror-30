#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib import admin
from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'is_valid', 'name', 'email', 'public']
    search_fields = ['author', 'name', 'email', 'object_id']
    list_filter = ['is_valid', 'public']
    raw_id_fields = ['reply', 'author']


admin.site.register(Comment, CommentAdmin)
