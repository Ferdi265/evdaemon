from functools import reduce
from select import select
from time import perf_counter

from .state import State

class Daemon(object):
    """
    An event loop daemon (evd)

    Daemon modules can be registered and they are woken up when opened files
    can be read or events fire

    Attributes:
    - state: contains the state object of all loaded modules
    """
    def __init__(self):
        self.modules = {}
        self.state = State()
    
    # public API

    def register(self, module):
        """
        Register a module to the daemon

        Adds the module state to the daemon state
        """
        if module.name in self.modules.keys():
            raise ValueError("module of that name already registered")
        else:
            module.register_daemon(self)
            setattr(self.state, module.name, module.state)
            self.modules[module.name] = module

    def unregister(self, module):
        """
        Unregister a module from the daemon

        Removes the module state from the daemon state
        """
        if module in self.modules.values():
            module.unregister_daemon(self)
            delattr(self.state, module.name)
            del self.modules[module.name]
        else:
            raise ValueError("this module is not registered")

    def emit(self, *path):
        """
        Emit an event to all listening modules
        """
        path = list(path)
        for module in self.modules.values():
            module.emit_local(*path)

    def run(self):
        """
        Run the event loop
        """
        if len(self.modules) == 0:
            raise ValueError("no modules registered")
        while True:
            if not self._has_files() and not self._has_timeouts():
                break
            timeout = self._calculate_timeout()
            ready, _, _ = select(self._files(), [], [], timeout)
            self._dispatch_timeouts()
            for file in ready:
                self._trigger_file(file)

    # private API

    def _has_timeouts(self):
        for module in self.modules.values():
            if len(module.timeouts()) != 0:
                return True
        return False

    def _calculate_timeout(self):
        now = perf_counter()
        first_tos = sorted(
            module.timeouts()[0]
                for module in self.modules.values()
                if len(module.timeouts()) != 0
        )
        if len(first_tos) == 0:
            return None
        elif first_tos[0][0] - now <= 0:
            return 0
        else:
            return first_tos[0][0] - now

    def _dispatch_timeouts(self):
        now = perf_counter()
        for module in self.modules.values():
            tos = module.timeouts()
            while len(tos) != 0:
                ready_time, fn = tos[0]
                if now > ready_time:
                    fn(ready_time - now)
                    tos.pop(0)
                else:
                    break

    def _has_files(self):
        for module in self.modules.values():
            if len(module.files()) != 0:
                return True
        return False

    def _files(self):
        return list(reduce(
            lambda acc, module: acc + list(module.files()),
            list(self.modules.values()),
            []
        ))

    def _trigger_file(self, file):
        for module in self.modules.values():
            if file in module.files():
                module.trigger_file(file)
                return
        raise ValueError("file not registered to any module: {}".format(file))
