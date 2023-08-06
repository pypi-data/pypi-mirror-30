# -*- coding: utf-8 -*-

import six

from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response as RestResponse


class Response(object):
    def __new__(cls, data=None, status=None,
                template_name=None, headers=None,
                exception=False, content_type=None):

        return RestResponse(data, status, template_name, headers, exception, content_type)


class ErrorResponse(object):
    """
    向客户端输出错误提示的Response, error可以是字符串 or 列表 or 元组 or serializer or 字典。
    """

    def __new__(cls, error):
        if isinstance(error,  six.string_types):
            error = {'error': error}
        elif isinstance(error, (list, tuple)):
            error = {'error': u','.join(error)}
        elif isinstance(error, serializers.Serializer):
            serializer = error
            errors = []
            for (k, v) in serializer.errors.items():
                field = serializer.fields.get(k, None)
                if field is not None:
                    errors.append(u'%s%s' % (field.label, u''.join(v)))
                else:
                    errors.append(u''.join(v))
            error = {'error': u''.join(errors)}

        return RestResponse(error, status=status.HTTP_400_BAD_REQUEST)
