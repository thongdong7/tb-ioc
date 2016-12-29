class InitObjectFromClassError(Exception):
    def __str__(self):
        name, class_full_name, args, message = self.args
        return 'Init service "{0}" failed: {1}. Class: {2}. Arguments: {3}'.format(name, message, class_full_name, args)


class InitServiceError(Exception):
    def __init__(self, name, error):
        self.name = name
        self.error = error

    def __str__(self):
        return 'Could not init service `{0}`: {1}'.format(self.name, self.error)
