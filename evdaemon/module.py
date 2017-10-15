from .hooks import Hooks
from .state import State

class Module(object):
    name = None

    def __init__(self):
        if self.name == None:
            raise ValueError("class-attribute 'name' has to be set to a module name")
        
        self.global_state = None
        self.state = State()

        self._daemon = None
        self._hooks = Hooks()
        self._hooks_private = Hooks()
        self._files = {}
   
    # public API

    def register_daemon(self, daemon):
        self.global_state = daemon.state
        self._daemon = daemon

    def unregister_daemon(self, daemon):
        self.global_state = None
        self._daemon = None
    
    def register_file(self, file, *path):
        path = list(path)
        if file not in self._files:
            self._files[file] = path
        else:
            raise ValueError("file already registered")

    def unregister_file(self, file):
        if file in self._files:
            del self._files[file]
        else:
            raise ValueError("file not registered")

    def files(self):
        return self._files.keys()

    def trigger_file(self, file):
        if file in self._files:
            self.emit_private(*self._files[file])
        else:
            raise ValueError("file not registered")

    def emit_global(self, *path):
        if self._daemon != None:
            self._daemon.emit(path)
        else:
            raise ValueError("module not yet registered to an event daemon")

    def listen(self, *path):
        self._listen_imp(self._hooks, path)
    def remove(self, *path):
        self._remove_imp(self._hooks, path)
    def emit(self, *path):
        self._daemon.emit(list(path))
    
    def listen_private(self, *path):
        self._listen_imp(self._hooks_private, path)
    def remove_private(self, *path):
        self._remove_imp(self._hooks_private, path)
    def emit_private(self, *path):
        self._hooks_private.emit(list(path))

    # private API

    def _listen_imp(self, hooks, path):
        path = list(path)
        if len(path) == 0:
            raise TypeError("listen() missing 1 required positional argument: 'listener'")
        listener = path.pop()
        hooks.listen(path, listener)

    def _remove_imp(self, hooks, path):
        path = list(path)
        if len(path) == 0:
            raise TypeError("remove() missing 1 required positional argument: 'listener'")
        listener = path.pop()
        hooks.remove(path, listener)
