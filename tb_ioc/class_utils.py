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


class GetClassError(Exception):
    def __init__(self, class_full_name, detail, *args, **kwargs):
        super(GetClassError, self).__init__(*args, **kwargs)
        self.class_full_name = class_full_name
        self.detail = detail

    def __str__(self):
        return "Could not get class from {self.class_full_name}: {self.detail}".format(**locals())


def get_class(class_full_name):
    try:
        module_name, class_name = parse_module_class(class_full_name)
        module = get_module(module_name)
        return getattr(module, class_name)
    except ImportError as e:
        raise GetClassError(class_full_name, detail=str(e))



def get_method_from_full_name(method_full_name):
    module_name, method_name = parse_module_class(method_full_name)

    module = get_module(module_name)

    return getattr(module, method_name)
