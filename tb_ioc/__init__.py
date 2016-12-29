import logging
import os
import re

import yaml
from six import string_types
from tb_ioc.class_utils import parse_module_class, get_module, get_method_from_full_name, get_class, GetClassError
from tb_ioc.exception import InitObjectFromClassError
from tb_ioc.model import ServiceConfig


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
            with open(file_path, 'rb') as f:
                config = yaml.load(f)

                file_dir = os.path.dirname(os.path.abspath(file_path))

                self.load(config, base_dir=file_dir)
        except Exception as e:
            self.logger.error('Error when parse file: %s' % file_path)
            self.logger.exception(e)
            raise

    def load(self, config, **kwargs):
        if not config:
            # Empty config file
            return

        if not isinstance(config, dict):
            if isinstance(config, string_types):
                raise AssertionError('Must use load_resource()/load_file() to load %s' % config)

            raise AssertionError("load(config) expect config is dict, provided '%s'" % config.__class__)

        if 'imports' in config:
            for import_config in config['imports']:
                self.load_import(import_config, **kwargs)

        self.service_config.update(config.get('services', {}))
        self.parameter_config.update(config.get('parameters', {}))

    def load_import(self, import_config, **kwargs):
        resource = import_config['resource']

        self.load_resource(resource, **kwargs)

    def load_resource(self, resource, **kwargs):
        self.logger.debug('Load resource: %s' % resource)
        m = self.import_package_pattern.search(resource)
        if m:
            package_name = m.group(1)
            if m.group(2):
                file_path = m.group(3)
            else:
                file_path = 'conf/services.yml'

            package_module = get_module(package_name)
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

    def _build_args_execute_method(self, service_config, method):
        args = self.build_arguments(service_config.arguments)
        kwargs = self._build_kwargs(service_config.kwargs)

        return method(*args, **kwargs)

    def build_service(self, name):
        self.logger.debug('Build service: %s' % name)
        service_config = ServiceConfig(self.service_config[name], alias_func=self._get_service_alias)

        if service_config.is_alias:
            return self.get(service_config.alias_name)

        if service_config.is_method:
            return get_method_from_full_name(service_config.full_name)

        if service_config.is_factory_object_property_method:
            parent_service = self.get(service_config.service_name)
            method = getattr(parent_service, service_config.property_name)

            obj = self._build_args_execute_method(service_config, method)
        elif service_config.is_factory_method:
            method = self.get(service_config.method_name)

            obj = self._build_args_execute_method(service_config, method)
        elif service_config.is_method_call:
            method = get_method_from_full_name(service_config.full_name)

            obj = self._build_args_execute_method(service_config, method)
        elif service_config.is_object:
            if service_config.is_class:
                try:
                    clazz = get_class(service_config.full_name)
                except GetClassError as e:
                    raise Exception("Init service %s error: %s" % (name, str(e)))

                args = self.build_arguments(service_config.arguments)
                kwargs = self._build_kwargs(service_config.kwargs)

                try:
                    obj = clazz(*args, **kwargs)
                except Exception as e:
                    logging.exception(e)
                    raise InitObjectFromClassError(name, service_config.full_name, args, str(e))

            elif service_config.is_delegate:
                obj = self.get(service_config.delegate_obj_name)

                return getattr(obj, service_config.delegate_name)
            elif service_config.is_factory_object:
                factory_service_name = service_config.service_name
                factory_obj = self.get(factory_service_name)
                method = getattr(factory_obj, 'get')
                args = self.build_arguments(service_config.arguments)
                obj = method(*args)
            else:
                module_name, class_name = parse_module_class(service_config.factory_class_name)

                module = get_module(module_name)
                clazz = getattr(module, class_name)

                method = getattr(clazz, service_config.method_name)

                args = self.build_arguments(service_config.arguments)

                obj = method(*args)
        else:
            raise Exception('Config for service {0} must be string or dict. Got {1}'.format(name, service_config))

        calls = service_config.calls
        for call in calls:
            assert isinstance(call, list)
            assert len(call) == 1 or len(call) == 2

            if len(call) == 2:
                method_name, method_args = call
            elif len(call) == 1:
                method_name, = call
                method_args = []
            else:
                raise Exception(
                    'Service {0}.calls error: Expect a list of 1 or 2 items. Got: {1}'.format(name, call))

            method_args = self.build_arguments(method_args)
            method = getattr(obj, method_name)
            method(*method_args)

        return obj

    def build_arguments(self, arguments):
        if not isinstance(arguments, list):
            raise Exception('Arguments must be a list. %s is given' % arguments)

        return self.build_argument(arguments)

    def _build_kwargs(self, arguments):
        if not isinstance(arguments, dict):
            raise Exception('Arguments must be a dict. %s is given' % arguments)

        return self.build_argument(arguments)

    def _get_service_alias(self, text):
        """
        Get service_name from alias string like `$<service_name>`

        :param text:
        :return:
        """
        m = self.service_prefix_pattern.match(text)
        if m:
            return m.group(1)

    def build_argument(self, argument):
        if isinstance(argument, string_types):
            service_name = self._get_service_alias(argument)
            if service_name:
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
        elif isinstance(argument, dict):
            tmp = {}
            for k in argument:
                tmp[k] = self.build_argument(argument[k])

            return tmp
        else:
            return argument

    def put_parameter(self, param_name, value):
        self.parameter_config[param_name] = value

    def get_parameter(self, param_name, default_value=None):
        return self.parameter_config.get(param_name, default_value)
