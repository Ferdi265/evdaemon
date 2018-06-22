from evdaemon import Module

class wmModule(Module):
    """
    Represents a Window Manager and its state

    State:
    - monitors: a dict of Monitor objects
    - workspaces: a dict of Workspace objects
    """
    name = "wm"
    def __init__(self):
        super().__init__()
        self.state.mode = None
        self.state.title = None
        self.state.monitors = dict()
        self.state.workspaces = dict()
