import re

__author__ = 'thongdong7'


parse_module_pattern = re.compile('^([\.\w]+)\.([^\.]+)$')


def parse_module_class(class_full_name):
    m = parse_module_pattern.match(class_full_name)
    if not m:
        raise Exception('Could not find module for class: %s' % class_full_name)

    return m.group(1), m.group(2)
