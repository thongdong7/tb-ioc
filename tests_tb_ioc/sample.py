def hello(name):
    return 'Hello ' + name


class HelloService(object):
    def __init__(self, name):
        self.name = name

    def set_name(self, name):
        self.name = name


class HelloFactory(object):
    @staticmethod
    def get():
        return HelloService('Peter')


def create_hello_service(name):
    return HelloService(name)
