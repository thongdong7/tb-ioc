from importlib import import_module
import logging
import os
import re
from tb_ioc.class_utils import parse_module_class
import yaml


class IOC(object):
    def __init__(self):
        self.cache_modules = dict()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.service_prefix = "$"
        self.service_config = dict()
        self.parameter_config = dict()

        self.cached_services = dict()

        self.service_prefix_pattern = re.compile('^' + re.escape(self.service_prefix) + '(.+)$')
        self.parameter_prefix = '%'
        self.parameter_suffix = '%'
        self.parameter_pattern = re.compile(
            '^' + re.escape(self.parameter_prefix) + '(.+)' + re.escape(self.parameter_suffix))
        self.import_package_pattern = re.compile("^@(\w+)(/(.*))?$")

        self.put('_Container', self)

    def load_file(self, file_path):
        if not os.path.isfile(file_path):
            raise Exception("Invalid file: %s" % file_path)

        try:
            self.logger.debug('Load file: %s' % file_path)
            with open(file_path, 'r') as f:
                config = yaml.load(f)

                file_dir = os.path.dirname(os.path.abspath(file_path))

                self.load(config, base_dir=file_dir)
        except Exception as e:
            self.logger.error('Error when parse file: %s' % file_path)
            self.logger.exception(e)
            raise e

    def load(self, config, **kwargs):
        if 'imports' in config:
            for import_config in config['imports']:
                self.load_import(import_config, **kwargs)

        self.service_config.update(config.get('services', {}))
        self.parameter_config.update(config.get('parameters', {}))

    def load_import(self, import_config, **kwargs):
        resource = import_config['resource']

        self.load_resource(resource, **kwargs)

    def load_resource(self, resource, **kwargs):
        m = self.import_package_pattern.search(resource)
        if m:
            package_name = m.group(1)
            if m.group(3):
                file_path = m.group(3)
            else:
                file_path = 'conf/services.yml'

            package_module = self.get_module(package_name)
            full_file_path = os.path.join(os.path.dirname(package_module.__file__), file_path)

            self.load_file(full_file_path)
        else:
            # Load as file
            base_dir = kwargs.get('base_dir')

            file_path = os.path.join(base_dir, resource)

            self.load_file(file_path)

    def get(self, name):
        if name in self.cached_services:
            return self.cached_services[name]

        if name not in self.service_config:
            raise KeyError("Invalid service: %s" % name)

        service = self.build_service(name)
        self.cached_services[name] = service

        return service

    def put(self, name, obj):
        self.cached_services[name] = obj

    def build_service(self, name):
        self.logger.debug('Build service: %s' % name)
        service_config = self.service_config[name]

        class_full_name = service_config.get('class')
        if class_full_name:
            module_name, class_name = parse_module_class(class_full_name)
            module = self.get_module(module_name)

            clazz = getattr(module, class_name)
            args = self.build_arguments(service_config.get('arguments', []))

            try:
                obj = clazz(*args)
            except Exception as e:
                self.logger.error(
                    'Error when create service: %s. Class: %s. Arguments: %s' % (name, class_full_name, args))
                raise e
        elif 'delegate' in service_config:
            delegate_obj_name, delegate_name = service_config.get('delegate')

            obj = self.get(delegate_obj_name)

            return getattr(obj, delegate_name)
        else:
            factory = service_config.get('factory')

            if not factory:
                raise Exception('No class/factory for service: %s. Provided config: %s' % (name, service_config))

            factory_class_name, method_name = factory
            module_name, class_name = parse_module_class(factory_class_name)

            module = self.get_module(module_name)
            clazz = getattr(module, class_name)

            method = getattr(clazz, method_name)

            args = self.build_arguments(service_config.get('arguments', []))

            obj = method(*args)

        calls = service_config.get('calls', [])
        for method_name, method_args in calls:
            method_args = self.build_arguments(method_args)
            method = getattr(obj, method_name)
            method(*method_args)

        return obj

    def get_module(self, module_name):
        if module_name in self.cache_modules:
            return self.cache_modules[module_name]

        module = import_module(module_name)
        self.cache_modules[module_name] = module

        return module

    def build_arguments(self, arguments):
        if not isinstance(arguments, list):
            raise Exception('Arguments must be a list. %s is given' % arguments)

        return self.build_argument(arguments)

    def build_argument(self, argument):
        if isinstance(argument, str):
            m = self.service_prefix_pattern.match(argument)
            if m:
                service_name = m.group(1)
                return self.get(service_name)

            m = self.parameter_pattern.match(argument)
            if m:
                parameter_name = m.group(1)
                if parameter_name not in self.parameter_config:
                    raise KeyError('Parameter "%s" is not declared' % parameter_name)

                return self.parameter_config[parameter_name]

            return argument
        elif isinstance(argument, list):
            tmp = []
            for item in argument:
                tmp.append(self.build_argument(item))

            return tmp
        else:
            return argument

    def put_parameter(self, param_name, value):
        self.parameter_config[param_name] = value

    def get_parameter(self, param_name):
        return self.parameter_config[param_name]
