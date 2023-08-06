import abc


class Method():
    def __init__(self, name, callback=None):
        self.name = name
        self.callback = callback
        self.req_info = {}


class NumberField():
    def __init__(self):
        self.number = None


class TextField():
    def __init__(self):
        self.text = None


class PassField():
    def __init__(self):
        self.passwd = None


class UrlField():
    def __init__(self):
        self.url = None


# client apps intending to use the callback interface must implement the getters they intend on using
class Callback(metaclass=abc.ABCMeta):
    def cb(self, info):
        return_info = {}
        for name, val_type in info.items():
            if type(val_type) == NumberField:
                return_info[name] = self.get_number()
            elif type(val_type) == TextField:
                return_info[name] = self.get_text()
            elif type(val_type) == PassField:
                return_info[name] = self.get_pass()
            elif type(val_type) == UrlField:
                return_info[name] = self.get_url()
        return return_info

    @abc.abstractmethod
    def get_number(self):
        print('get_number')

    @abc.abstractmethod
    def get_text(self):
        print('get_text')

    @abc.abstractmethod
    def get_pass(self):
        print('get_pass')

    @abc.abstractmethod
    def get_url(self):
        print('get_url')


# run list of mesa methods against casa obj and supply any callbacks and required info as necessary
def run_mesa_methods(obj, mesa_methods, cb):
    results = []
    for step in mesa_methods:
        if step.callback:
            method_result = getattr(obj, step.name)(cb, step.req_info)
        else:
            method_result = getattr(obj, step.name)()
        results.append(method_result)
    return results
