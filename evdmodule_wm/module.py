from evdaemon import Module

class wmModule(Module):
    """
    Represents a Window Manager and its state

    State:
    - monitors: a list of Monitor objects
    - workspaces: a list of Workspace objects
    - windows: a list of Window objects
    """
    name = "wm"
    def __init__(self):
        super().__init__()
        self.state.monitors = []
        self.state.workspaces = []
        self.state.windows = []
