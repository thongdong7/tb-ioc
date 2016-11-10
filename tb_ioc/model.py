from six import string_types


class ServiceConfig(object):
    def __init__(self, service_config, alias_func):
        self.is_method = False
        self.is_alias = False
        self.is_method_call = False
        self.is_factory_method = False
        self.is_object = False
        self.is_class = False
        self.is_delegate = False
        self.arguments = []
        self.calls = []

        if isinstance(service_config, string_types):
            service_name = alias_func(service_config)
            if service_name:
                self.is_alias = True
                self.alias_name = service_name
            else:
                self.is_method = True
                self.full_name = service_config
        elif isinstance(service_config, dict):
            self.arguments = service_config.get('arguments', [])
            self.kwargs = service_config.get('kwargs', {})
            self.calls = service_config.get('calls', [])
            if 'factory_method' in service_config:
                self.is_factory_method = True
                self.method_name = service_config['factory_method']
            elif 'method' in service_config:
                self.is_method_call = True
                self.full_name = service_config['method']
            else:
                self.is_object = True

                class_full_name = service_config.get('class')
                if class_full_name:
                    self.is_class = True
                    self.full_name = class_full_name
                elif 'delegate' in service_config:
                    self.delegate_obj_name, self.delegate_name = service_config.get('delegate')
                    self.is_delegate = True
                else:
                    self.is_factory = True
                    factory = service_config.get('factory')

                    if not factory:
                        # TODO Create exception for this
                        raise Exception('No class/factory for service. Provided config: %s' % (service_config,))

                    self.factory_class_name, self.method_name = factory
