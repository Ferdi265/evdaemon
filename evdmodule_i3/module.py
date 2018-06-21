from evdmodule_wm import *

from .ipc import i3ipcModule

class i3Module(wmModule):
    """
    An evd window manager module for the i3 window manager
    """
    def __init__(self, ipc = None):
        super().__init__()
        self._ipc = ipc or i3ipcModule()

        self.listen_once("i3ipc", "reply", "outputs", self._outputs)
        self._ipc.send_cmd("outputs")

    def register_daemon(self, daemon):
        super().register_daemon(daemon)
        daemon.register(self._ipc)

    def unregister_daemon(self, daemon):
        super().unregister_daemon()
        daemon.unregister(self._ipc)
    
    def _outputs(self, payload):
        monitors = []
        for output in outputs:
            o_rect = output['rect']
            rect = Rect(o_rect['x'], o_rect['y'], o_rect['width'], o_rect['height'])
            name = output['name']
            monitor = Monitor(rect, name)
            monitor.active = output['active']
            monitor.primary = output['primary']

    def _tree(self, payload):
        print(payload)
        print(payload.keys())
