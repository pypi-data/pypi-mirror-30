# -*- coding:utf-8 -*-
from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import RelatedField

__author__ = 'denishuang'


class RelatedChoicesMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(RelatedChoicesMetadata, self).get_field_info(field)

        if (not field_info.get('read_only') and
                isinstance(field, RelatedField) and
                hasattr(field, 'queryset')):
            if field.queryset.count() < 1000:
                # print field
                field_info['choices'] = [
                    {
                        'value': r.pk,
                        'display_name': unicode(r)
                    }
                    for r in field.queryset.all()
                    ]

        return field_info
