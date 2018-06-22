from time import perf_counter

from .hooks import Hooks
from .state import State

class Module(object):
    """
    A module for the evd

    Attributes:
    - name: the name of the module (must be set)
    - state: this module's state
    - global_state: the state of the evd

    Event facilites:
    - emit/listen/remove(): emits to or listens on the global daemon or removes such a listener
    - emit_local(): emits an event only to the local module, listen and remove as above
    - emit_private/listen_private/remove_private(): emits or listens on a private event only to the local module
    """
    name = None

    def __init__(self):
        if self.name == None:
            raise ValueError("class-attribute 'name' has to be set to a module name")
        
        self.global_state = None
        self.global_modules = None
        self.state = State()

        self._daemon = None
        self._hooks = Hooks()
        self._hooks_private = Hooks()
        self._files = {}
        self._timeouts = []
   
    # public API

    def register_daemon(self, daemon):
        """
        Called by the daemon when registering
        """
        self.global_state = daemon.state
        self.global_modules = daemon.modules
        self._daemon = daemon

    def unregister_daemon(self, daemon):
        """
        Called by the daemon when unregistering
        """
        self.global_state = None
        self.global_modules = None
        self._daemon = None
    
    def register_file(self, file, *path):
        """
        Register a file to emit an event when it can be read
        """
        path = list(path)
        if file not in self._files:
            self._files[file] = path
        else:
            raise ValueError("file already registered")

    def unregister_file(self, file):
        """
        Unregister a file from emitting events
        """
        if file in self._files:
            del self._files[file]
        else:
            raise ValueError("file not registered")

    def files(self):
        """
        Returns all registered files
        """
        return self._files.keys()

    def trigger_file(self, file):
        """
        Manually trigger a file event
        """
        if file in self._files:
            self.emit_private(*self._files[file])
        else:
            raise ValueError("file not registered")

    def timeouts(self):
        """
        Return all timeouts on this module
        """
        return self._timeouts

    def timeout(self, secs, fn):
        """
        Run a function after some timeout
        """
        to = (perf_counter() + secs, fn)
        self._timeouts.append(to)
        self._timeouts.sort(key = lambda to: to[0])

    def listen(self, *path):
        """
        Listen on events of a specific type
        """
        return self._listen_imp(self._hooks, path)

    def listen_once(self, *path):
        """
        Listen on an event of a specific type
        Removes the listener after one trigger
        """
        path = list(path)
        fn = path.pop()
        def listener_once(*args):
            self.remove(*path, listener_once)
            fn(*args)
        return self.listen(*path, listener_once)

    def remove(self, *path):
        """
        Remove a listener on a specific path
        """
        self._remove_imp(self._hooks, path)

    def emit(self, *path):
        """
        Emit an event to the global daemon
        """
        if self._daemon != None:
            self._daemon.emit(*path)
        else:
            raise ValueError("module not yet registered to an event daemon")

    def emit_local(self, *path):
        """
        Emit an event only to this module
        """
        self._hooks.emit(list(path))
    
    def listen_private(self, *path):
        """
        Listen on an event of a specific type,
        but trigger on events emitted privately by this module
        """
        return self._listen_imp(self._hooks_private, path)

    def listen_once_private(self, *path):
        """
        Listen on an event of a specific type,
        but trigger on events emitted privately by this module
        Removes the listener after one trigger
        """
        path = list(path)
        fn = path.pop()
        def listener_once(*args):
            self.remove_private(*path, listener_once)
            fn(*args)
        return self.listen_private(*path, listener_once)

    def remove_private(self, *path):
        """
        Remove a private listener on a specific path
        """
        self._remove_imp(self._hooks_private, path)

    def emit_private(self, *path):
        """
        Emit a private event only to this module
        """
        self._hooks_private.emit(list(path))

    # private API

    def _listen_imp(self, hooks, path):
        path = list(path)
        if len(path) == 0:
            raise TypeError("listen() missing 1 required positional argument: 'listener'")
        listener = path.pop()
        hooks.listen(path, listener)
        return listener

    def _remove_imp(self, hooks, path):
        path = list(path)
        if len(path) == 0:
            raise TypeError("remove() missing 1 required positional argument: 'listener'")
        listener = path.pop()
        hooks.remove(path, listener)
