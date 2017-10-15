class Workspace(object):
    def __init__(self, rect, name, num):
        self.rect = rect
        self.name = name
        self.num = num
        self.visible = False
        self.focused = False
        self.urgent = False
        self.monitor = None
        self.windows = []
