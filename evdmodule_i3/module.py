from evdmodule_wm import *

from .ipc import i3ipcModule

class i3Module(wmModule):
    """
    An evd window manager module for the i3 window manager
    """
    def __init__(self, ipc = None):
        super().__init__()

        self.listen("i3ipc", "reply", "workspaces", self._workspaces)
        self.listen("i3ipc", "reply", "subscribe", self._subscribe)
        self.listen("i3ipc", "reply", "outputs", self._outputs)
        self.listen("i3ipc", "event", "workspace", self._workspace_event)
        self.listen("i3ipc", "event", "output", self._output_event)
        self.listen("i3ipc", "event", "mode", self._mode_event)
        self.listen("i3ipc", "event", "window", self._window_event)
        self.listen("i3ipc", "event", "shutdown", self._shutdown_event)

    def register_daemon(self, daemon):
        super().register_daemon(daemon)

        if "i3ipc" not in daemon.modules:
            daemon.register(i3ipcModule())

        self._ipc = daemon.modules["i3ipc"]
        self._ipc.send_cmd("outputs")
        self._ipc.send_cmd("workspaces")
        self._ipc.send_cmd("subscribe", ["workspace", "output", "mode", "window", "shutdown"])

    def unregister_daemon(self, daemon):
        super().unregister_daemon()
        daemon.unregister(self._ipc)
  
    def _construct_workspace(self, workspace):
        if workspace == None:
            return None

        w_rect = workspace['rect']
        rect = Rect(w_rect['x'], w_rect['y'], w_rect['width'], w_rect['height'])
        name = workspace['name']

        num = workspace['num']
        if num == -1:
            num = None

        ws = Workspace(rect, name, num)
        ws.focused = workspace['focused']
        ws.urgent = workspace['urgent']
        ws.visible = workspace['visible']
        return ws

    def _construct_monitor(self, output):
        if output == None:
            return None

        o_rect = output['rect']
        rect = Rect(o_rect['x'], o_rect['y'], o_rect['width'], o_rect['height'])
        name = output['name']
        monitor = Monitor(rect, name)
        monitor.active = output['active']
        monitor.primary = output['primary']
        return monitor

    def _workspaces(self, payload):
        workspaces = dict()
        for workspace in payload:
            ws = self._construct_workspace(workspace)
            workspaces[(ws.num, ws.name)] = ws

        self.state.workspaces = workspaces
        self.emit("wm", "workspaces")

    def _subscribe(self, payload):
        if "success" not in payload or not payload["success"]:
            print("[WARN][i3]", "subscribe:", "failed!")

    def _outputs(self, payload):
        monitors = dict()
        for output in payload:
            monitor = self._construct_monitor(output)
            monitors[monitor.name] = monitor

        self.state.monitors = monitors
        self.emit("wm", "monitors")

    def _workspace_event(self, payload):
        self._ipc.send_cmd("workspaces")

        if payload["change"] == "focus":
            cur = payload["current"]
            if len(cur["nodes"]) + len(cur["floating_nodes"]) == 0:
                self.state.title = ""
                self.emit("wm", "title")

    def _output_event(self, payload):
        if "change" not in payload or payload["change"] != "unspecified":
            print("[WARN][i3]", "output event:", "contains unknown change:", payload["change"])

        self._ipc.send_cmd("outputs")

    def _mode_event(self, payload):
        self.state.mode = payload["change"]
        self.emit("wm", "mode")

    def _window_event(self, payload):
        container = payload["container"]
        
        if payload["change"] == "focus" or (payload["change"] == "title" and container["focused"]):
            self.state.title = container["name"]
            self.emit("wm", "title")
    
    def _shutdown_event(self, payload):
        self.emit("wm", "shutdown")
