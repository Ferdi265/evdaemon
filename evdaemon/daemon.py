from functools import reduce
from select import select

from .state import State

class Daemon(object):
    def __init__(self):
        self._modules = {}
        self.state = State()
    
    # public API

    def register(self, module):
        if module.name in self._modules.keys():
            raise ValueError("module of that name already registered")
        else:
            module.register_daemon(self)
            setattr(self.state, module.name, module.state)
            self._modules[module.name] = module

    def unregister(self, module):
        if module in self._modules.values():
            module.unregister_daemon(self)
            delattr(self.state, module.name)
            del self._modules[module.name]
        else:
            raise ValueError("this module is not registered")

    def emit(self, path):
        path = list(path)
        for module in self._modules:
            module.hooks.emit(path)

    def run(self):
        if len(self._modules) == 0:
            raise ValueError("no modules registered")
        while True:
            ready, _, _ = select(self._files(), [], [])
            for file in ready:
                self._trigger_file(file)

    # private API

    def _files(self):
        return list(reduce(
            lambda acc, module: acc + list(module.files()),
            list(self._modules.values()),
            []
        ))

    def _trigger_file(self, file):
        for module in self._modules.values():
            if file in module.files():
                module.trigger_file(file)
                return
        raise ValueError("file not registered to any module")
