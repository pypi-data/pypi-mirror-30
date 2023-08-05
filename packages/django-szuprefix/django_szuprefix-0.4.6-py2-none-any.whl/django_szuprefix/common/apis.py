# -*- coding:utf-8 -*-
from ..api.mixins import UserApiMixin
from . import serializers, models
from rest_framework import viewsets, decorators, response, status
from ..api import register

__author__ = 'denishuang'




class TempFileViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.TempFileSerializer
    queryset = models.TempFile.objects.all()
    user_field_name = 'owner'


register(__package__, 'tempfile', TempFileViewSet)