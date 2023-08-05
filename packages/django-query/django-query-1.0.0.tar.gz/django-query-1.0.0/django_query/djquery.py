# -*- coding: utf-8 -*-


def get_query_value(request, key, default=None, val_cast_func=None):
    """ Get Query by POST/GET """
    value = request.POST.get(key) or request.GET.get(key) or default
    return val_cast_func(value) if val_cast_func else value
