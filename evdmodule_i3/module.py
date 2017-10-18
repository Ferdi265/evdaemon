from evdmodule_wm import *

from .ipc import i3ipcModule

class i3Module(wmModule):
    def __init__(self, ipc = None):
        super().__init__()
        self._ipc = ipc or i3ipcModule()
       
        self.listen("i3ipc", "reply", "tree", self._tree)

    def register_daemon(self, daemon):
        super().register_daemon(daemon)
        daemon.register(self._ipc)

    def unregister_daemon(self, daemon):
        super().unregister_daemon()
        daemon.unregister(self._ipc)
    
    def _tree(self, payload):
        print(payload)
