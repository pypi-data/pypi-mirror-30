# -*- coding: utf-8 -*-
from jmespath import search

from jsonsniffer.base import FieldABC
from jsonsniffer.decorators import field_cache
from jsonsniffer.exceptions import JSONDataNotLoadedError


class Field(FieldABC):
    def __init__(self, jmespath):
        self._name = None
        self._jmespath = jmespath

    @field_cache
    def __get__(self, instance, cls):
        options = getattr(cls, '_jmesfunctions', None)
        json_data = self._json_data(instance)
        value = search(self._jmespath, json_data, options=options)
        return value

    def _json_data(self, instance):
        json_data = getattr(instance, 'data', None)
        if json_data is None:
            raise JSONDataNotLoadedError(
                'Load json data beforehand to the main Schema instance'
            )
        return json_data


class FlattenNestedField(Field):
    def __init__(self, jmespath=None, recursive_path=None, component=None):
        super().__init__(jmespath)
        missing = []
        for kw in (('recursive_path', recursive_path), ('componet', component)):
            if kw[1] is None:
                missing.append(kw[0])
        if missing:
            raise TypeError(
                f"{self._name}() missing {len(missing)} required keyword"
                f" argument{len(missing) and 's' or ''}:"
                f" {' and '.join(missing)}"
            )
        self._recursive_path = recursive_path
        self._component = component

    @field_cache
    def __get__(self, instance, cls):
        options = getattr(cls, '_jmesfunctions', None)
        json_data = self._json_data(instance)
        if self._jmespath:
            json_data = search(self._jmespath, json_data, options=options)

        result = []
        while json_data:
            if isinstance(json_data, list):
                json_data = search(
                    '[*].' + self._recursive_path + ' | []',
                    json_data, options=options
                )
            else:
                json_data = search(
                    self._recursive_path, json_data, options=options
                )
            result.extend(self._load_fields(json_data))
        return result

    def _load_fields(self, fields_data):
        print(fields_data)
        if fields_data is None:
            return []
        elif isinstance(fields_data, list):
            return [self._component().load(fdata) for fdata in fields_data]
        else:
            return [self._component().load(fields_data)]


class RelationalNestedField(Field):
    pass
