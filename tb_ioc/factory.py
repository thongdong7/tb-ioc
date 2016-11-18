from tb_ioc import get_class


class Factory(object):
    def __init__(self, full_class_name):
        self.class_full_name = full_class_name
        self.clazz = get_class(self.class_full_name)

    def get(self, *args, **kwargs):
        return self.clazz(*args, **kwargs)
