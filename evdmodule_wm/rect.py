class Rect(object):
    """
    Represents a rectangle on the screen

    Attributes:
    - x: x-position
    - y: y-position
    - width: rectangle extent in x direction, rightwards from position
    - height: rectangle extent in y direction, downwards from position
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def __str__(self):
        return ("{}x{}+{}+{}"
            .format(self.width, self.height, self.x, self.y)
        )
    def __repr__(self):
        return "<Rect {}>".format(self)
