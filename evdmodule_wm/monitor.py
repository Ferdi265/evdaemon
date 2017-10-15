class Monitor(object):
    def __init__(self, rect, name):
        self.rect = rect
        self.name = name
        self.active = False
        self.primary = False
        self.workspaces = []
