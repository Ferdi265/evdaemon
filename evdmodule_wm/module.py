from evdaemon import Module

class wmModule(Module):
    name = "wm"
    def __init__(self):
        super().__init__()
        self.state.monitors = []
        self.state.workspaces = []
        self.state.windows = []
