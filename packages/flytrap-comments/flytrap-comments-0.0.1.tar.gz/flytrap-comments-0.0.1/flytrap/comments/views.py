#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.permissions import AllowAny
from flytrap.base.view import BaseModeView
from .serializers import CommentSerializer
from .filter import CommentFilter
from .models import Comment


class CommentViewSet(BaseModeView):
    permission_classes = (AllowAny,)
    serializer_class = CommentSerializer
    filter_class = CommentFilter
    queryset = Comment.objects.filter(is_valid=True)

    def list(self, request, *args, **kwargs):
        """query"""
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.clean_data()
        request.data['author'] = request.user.id
        return super(CommentViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.clean_data()
        request.data['author'] = request.user.id
        return super(CommentViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(CommentViewSet, self).destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete_obj()
