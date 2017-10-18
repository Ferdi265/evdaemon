from functools import reduce
from select import select
from time import perf_counter

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

    def emit(self, *path):
        path = list(path)
        for module in self._modules.values():
            module.emit_local(*path)

    def timeout(self, secs, fn):
        self._timeouts.append((perf_counter() + secs, fn))

    def run(self):
        if len(self._modules) == 0:
            raise ValueError("no modules registered")
        while True:
            print("--- iter")
            if self._has_files() or self._has_timeouts() == 0:
                print("  ! break")
                break
            timeout = self._calculate_timeout()
            print("  . select", timeout)
            ready, _, _ = select(self._files(), [], [], timeout)
            print("  . ready")
            self._dispatch_timeouts()
            for file in ready:
                print("  > file")
                self._trigger_file(file)

    # private API

    def _has_timeouts(self):
        for module in self._modules.values():
            if len(module.timeouts()) != 0:
                return True
        return False

    def _calculate_timeout(self):
        now = perf_counter()
        first_tos = sorted(
            module.timeouts()[0]
                for module in self._modules.values()
                if len(module.timeouts()) != 0
        )
        if len(first_tos) == 0:
            return None
        elif first_tos[0] - now <= 0:
            return 0
        else:
            return first_tos[0] - now

    def _dispatch_timeouts(self):
        now = perf_counter()
        for module in self._modules.values():
            tos = module.timeouts()
            while len(tos) != 0:
                ready_time, fn = tos[0]
                if now > ready_time:
                    print("  > timeout", ready_time - now)
                    fn(ready_time - now)
                    tos.pop()
                else:
                    break

    def _has_files(self):
        for module in self._modules.values():
            if len(module.files()) != 0:
                return True
        return False

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
