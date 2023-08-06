#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet

from .execption import FlytrapException
from .response import SimpleResponse


class ViewMixin(object):
    @staticmethod
    def get_data(data=None, message=None):
        results = {
            'status': 'ok' if message is None else 'error',
            'message': message
        }
        if isinstance(data, dict) and 'results' in data:
            results.update(data)
        else:
            results.update({'results': data})
        return results

    def finalize_response(self, request, response, *args, **kwargs):
        """封装响应"""
        response = super(ViewMixin, self).finalize_response(request, response, *args, **kwargs)
        if 'status' not in response.data:
            if response.status_code <= 300:
                response.data = self.get_data(response.data)
            else:
                response.data = self.get_data(message=response.data)
        return response

    def resp(self, data, status):
        if isinstance(data, dict):
            data["status"] = status
            return SimpleResponse(data)
        if isinstance(data, str):
            return SimpleResponse({"results": data, "status": status})
        if hasattr(self, 'get_serializer'):
            return SimpleResponse(self.get_serializer(data).data)

    def resp_ok(self, data):
        return SimpleResponse(self.get_data(data))

    def resp_failed(self, data):
        return SimpleResponse(self.get_data(message=data))

    def handle_exception(self, exc):
        if isinstance(exc, FlytrapException) or (exc.args and isinstance(exc.args[0], FlytrapException)):
            return SimpleResponse(self.get_data(message=str(exc)))
        return super(ViewMixin, self).handle_exception(exc)

    def clean_data(self, data=None):
        """清洗空数据"""
        if not data:
            data = self.request.data
        index_list = []
        for key, values in data.items():
            self.clean_value(values)
            if self.is_null(values):
                index_list.append(key)
        for key in index_list[::-1]:
            del data[key]

    @classmethod
    def clean_value(cls, data):
        """递归清洗数据"""
        index_list = []
        if isinstance(data, list):
            for index, item in enumerate(data):
                if not isinstance(item, str):
                    cls.clean_value(item)
                if cls.is_null(item):
                    index_list.append(index)
        if isinstance(data, dict):
            for k, v in data.items():
                if not isinstance(v, str):
                    cls.clean_value(v)
                if cls.is_null(v):
                    index_list.append(k)
        for index in index_list[::-1]:
            del data[index]

    @staticmethod
    def is_null(value):
        """判空"""
        if value is False:
            return False
        return not bool(value)


try:
    from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet
except ImportError:
    pass
else:
    class BaseMongoViewSet(ViewMixin, MongoModelViewSet):
        pass


class BaseModeView(ViewMixin, ModelViewSet):
    pass


class BaseViewSet(ViewMixin, GenericAPIView):
    pass
