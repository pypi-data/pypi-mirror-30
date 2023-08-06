# -*- coding: utf-8 -*-

import functools
import six


def view_http_method(names=None):
    """
    给view添加http method 约束，默认在不为get.
    """
    names = names or ['get']

    if isinstance(names, six.string_types):
        names = [names]

    names = [m.lower() for m in names]

    def _api_view(fn):
        @functools.wraps(fn)
        def __api_view(*args, **kwargs):
            return fn(*args, **kwargs)

        setattr(__api_view, 'http_method_names', names)
        return __api_view

    return _api_view
