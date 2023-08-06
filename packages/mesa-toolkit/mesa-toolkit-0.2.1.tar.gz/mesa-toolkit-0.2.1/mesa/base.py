import inspect, sys, pkgutil, importlib, types

import abc


class Casa():
    def __init__(self, pkg, hideExceptions=False, interface=None):
        if pkg is None:
            raise Exception
        self.pkg = pkg
        __import__(self.pkg)
        self.package = sys.modules[pkg]
        self.prefix = pkg + '.'
        self._fill_casa()
        self.interface = interface

    def _fill_casa(self):
        self.casa = {}
        for importer, modname, ispkg in pkgutil.iter_modules(self.package.__path__, self.prefix):
            module = __import__(modname, locals(), [], -1)
            for name, cls in inspect.getmembers(module):
                if inspect.isclass(cls):  # and of type interface
                    self.casa[cls.__name__] = cls()

    def get_members(self):
        if self.casa:
            return self.casa.keys()

    def rebuild(self):
        for importer, modname, ispkg in pkgutil.iter_modules(self.package.__path__, self.prefix):
            if modname in sys.modules:
                module = sys.modules[modname]
            else:
                module = __import__(modname, locals(), [], -1)
            importlib.reload(module)
        self._fill_casa()

    # safe rebuild. rollback to previous if newly loaded module fails. file io.
    def update(self):
        pass

    def _exec(self, name, cls, member, *args):
        if type(getattr(cls, member)) == types.FunctionType:
            return getattr(cls, member)()
        else:
            return getattr(cls, member)(*args)

    # run method in each casa member
    def run(self, method):
        for name, cls in self.casa.items():
            self._exec(name, cls, method)

    # yield result of function in each casa member; (name, return value) tuple.
    def generate(self, function, *args):
        ret = {}
        n = self.next(function, *args)
        while (True):
            try:
                (name, result) = next(n)
                ret[name] = result
            except:
                return ret

    def next(self, function, *args):
        for name, cls in self.casa.items():
            yield (name, self._exec(name, cls, function, *args))

    def __len__(self):
        return len(self.casa)


'''
Like a Casa only taller!

A Casa subclass that implements the group of objects as a list and not a dict.
Explicit ordering optional. Useful for the pipeline datastructure.
'''


class Torre(Casa):
    def _fill_casa(self):
        self.casa = []
        for importer, modname, ispkg in pkgutil.iter_modules(self.package.__path__, self.prefix):
            module = __import__(modname, locals(), [], -1)
            for name, cls in inspect.getmembers(module):
                if inspect.isclass(cls):  # and of type interface
                    self.casa.append(cls())
            if issubclass(cls, OrderMixin):
                self.casa = sorted(self.casa, key=lambda z: z.get_priority())

    def run(self, method):
        for cls in self.casa:
            self._exec(cls, method)


class OrderMixin():
    @abc.abstractmethod
    def get_priority(self):
        raise NotImplementedError('get_priority must be implemented by classes inheriting the OrderMixin')
