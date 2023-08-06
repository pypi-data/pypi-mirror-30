#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# import json
# from json import JSONEncoder
# from rest_framework.fields import empty

from rest_framework import serializers

try:
    from rest_framework_mongoengine import serializers as mongo_serializer
except ImportError:
    pass
else:
    class BaseMongoSerializer(mongo_serializer.DocumentSerializer):
        pass


class BaseSerializer(serializers.Serializer):
    pass


class BaseModelSerializer(serializers.ModelSerializer):
    pass
