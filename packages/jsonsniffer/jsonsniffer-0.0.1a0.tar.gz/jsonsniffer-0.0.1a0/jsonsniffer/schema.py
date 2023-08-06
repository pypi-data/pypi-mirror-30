# -*- coding: utf-8 -*-
from jsonsniffer.base import FieldABC, SchemaABC


class SchemaMeta(type):
    def __new__(mcs, cls_name, cls, attrs):
        for field_name, field_instance in attrs.items():
            if isinstance(field_instance, FieldABC):
                setattr(field_instance, '_name', field_name)
        return super().__new__(mcs, cls_name, cls, attrs)


class Schema(SchemaABC, metaclass=SchemaMeta):
    def load(self, data):
        self.data = data
        return self
