#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url('^$', csrf_exempt(views.CommentViewSet.as_view({'get': 'list', 'post': 'create'})), name='comments'),
    url('^(?P<pk>\d+)$', csrf_exempt(views.CommentViewSet.as_view({'put': 'update', 'delete': 'destroy'})), name='comment'),
]
