import re
from six import string_types


class ServiceConfig(object):
    # TODO Fix the hard-code of '$' character
    obj_property_pattern = re.compile('^\$(\w+)\.(\w+)$')

    def __init__(self, service_config, alias_func):
        self.is_method = False
        self.is_alias = False
        self.is_method_call = False
        self.is_factory_method = False
        self.is_factory_object = False
        self.is_object = False
        self.is_class = False
        self.is_delegate = False
        self.arguments = []
        self.calls = []

        # Example:
        # s3 = boto3.resource('s3')
        # s3.Bucket('mybucket')
        #
        # declare:
        # services:
        # MyBucket:
        #   factory_method: $s3.Bucket
        #   arguments: [mybucket]
        self.is_factory_object_property_method = False

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
                value = service_config['factory_method']
                m = self.obj_property_pattern.search(value)
                if m:
                    self.is_factory_object_property_method = True
                    self.service_name = m.group(1)
                    self.property_name = m.group(2)
                else:
                    self.is_factory_method = True
                    self.method_name = value
            elif 'method' in service_config:
                self.is_method_call = True
                self.full_name = service_config['method']
            elif 'factory_class' in service_config:
                # Create an factory to hide class
                self.is_object = True
                self.is_class = True
                self.full_name = 'tb_ioc.factory.Factory'
                self.arguments = [service_config['factory_class']]
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
                    factory = service_config.get('factory')

                    if isinstance(factory, string_types):
                        self.is_factory_object = True
                        self.service_name = factory
                    elif isinstance(factory, list):
                        self.is_factory = True
                        self.factory_class_name, self.method_name = factory
                    else:
                        raise Exception('Unknown factory %s' % factory)

                    if not factory:
                        # TODO Create exception for this
                        raise Exception('No class/factory for service. Provided config: %s' % (service_config,))

