class Workspace(object):
    """
    Represents a workspace

    Attributes:
    - rect: the rectangle the workspace occupies
    - name: the name of the workspace
    - num: the number of the workspace (if numbered)
    - visible: whether this workspace can be seen
    - focused: whether this workspace is currently focused
    - urgent: whether something urgent happened on this workspace
    - monitor: the monitor this workspace is currently on or associated with
    - windows: the windows in this workspace
    """
    def __init__(self, rect, name, num):
        self.rect = rect
        self.name = name
        self.num = num
        self.visible = False
        self.focused = False
        self.urgent = False
        self.monitor = None
        self.windows = []

    def __str__(self):
        return ("<Workspace {} visible={}, focused={}, urgent={}>"
            .format(
                "'" + self.name + "'" + ((":" + str(self.num)) if self.num != None else ""),
                self.visible, self.focused, self.urgent
            )
        )
    def __repr__(self):
        return str(self)
