from six import string_types


class ServiceConfig(object):
    def __init__(self, service_config):
        self.is_method = False
        self.is_method_call = False
        self.is_factory_method = False
        self.is_object = False
        self.is_class = False
        self.is_delegate = False
        self.arguments = []
        self.calls = []

        if isinstance(service_config, string_types):
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

            # calls = service_config.get('calls', [])
            # for call in calls:
            #     assert isinstance(call, list)
            #     assert len(call) == 1 or len(call) == 2
            #
            #     if len(call) == 2:
            #         method_name, method_args = call
            #     elif len(call) == 1:
            #         method_name, = call
            #         method_args = []
            #     else:
            #         raise Exception(
            #             'Service {0}.calls error: Expect a list of 1 or 2 items. Got: {1}'.format(name, call))
            #
            #     method_args = self.build_arguments(method_args)
            #     method = getattr(obj, method_name)
            #     method(*method_args)
