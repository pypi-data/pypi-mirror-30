# -*- coding: utf-8 -*-
from functools import wraps


def field_cache(method):
    @wraps(method)
    def _manage_cache(self, instance, *args, **kwargs):
        value = getattr(instance, f'_{self._name}', 'N/A')
        if value != 'N/A':
            return value
        return method(self, instance, *args, **kwargs)
    return _manage_cache

