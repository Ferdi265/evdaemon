class Monitor(object):
    """
    Represents a monitor

    Attributes:
    - rect: the screen rectangle the monitor occupies
    - name: the monitors name or id
    - active: whether this is the currently focused or active monitor
    - primary: whether this is the primary monitor
    - workspaces: a list of workspaces associated with this monitor
    """
    def __init__(self, rect, name):
        self.rect = rect
        self.name = name
        self.active = False
        self.primary = False
        self.workspaces = []
