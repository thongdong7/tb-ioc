import re
from importlib import import_module

__author__ = 'thongdong7'

parse_module_pattern = re.compile('^([\.\w]+)\.([^\.]+)$')


def parse_module_class(class_full_name):
    m = parse_module_pattern.match(class_full_name)
    if not m:
        raise Exception('Could not find module for class: %s' % class_full_name)

    return m.group(1), m.group(2)


_cache_modules = {}


def get_module(module_name):
    if module_name in _cache_modules:
        return _cache_modules[module_name]

    module = import_module(module_name)
    _cache_modules[module_name] = module

    return module


def get_method_from_full_name(method_full_name):
    module_name, method_name = parse_module_class(method_full_name)

    module = get_module(module_name)

    return getattr(module, method_name)
