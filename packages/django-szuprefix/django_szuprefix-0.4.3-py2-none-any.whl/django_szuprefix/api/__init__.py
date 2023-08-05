# -*- coding:utf-8 -*-
from django.conf.urls import url
from django.utils.module_loading import autodiscover_modules

from django_szuprefix.utils import modelutils
from django_szuprefix.utils.views import csrf_token

__author__ = 'denishuang'
from rest_framework import serializers, routers


class newRouter(routers.DefaultRouter):
    def get_urls(self):
        urls = super(newRouter, self).get_urls()
        from ..auth.urls import urlpatterns
        urls += urlpatterns
        return urls

router = newRouter()


def autodiscover():
    # print "autodiscover"
    autodiscover_modules('apis')


def register(package, resource, viewset, base_name=None):
    p = "%s/%s" % (package.split(".")[-1], resource)
    router.register(p, viewset, base_name=base_name)


serializers.ModelSerializer.serializer_field_mapping.update({modelutils.JSONField: serializers.JSONField})
autodiscover()
