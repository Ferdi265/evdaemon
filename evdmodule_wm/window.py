class Window(object):
    """
    Represents a window

    Attributes:
    - wid: the Xorg window id
    """
    def __init__(self, wid):
        self.wid = wid

    def __str__(self):
        return "<Window 0x{:08x}>".format(self.wid)
    def __repr__(self):
        return str(self)
