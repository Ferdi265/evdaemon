class Hooks(object):
    subhook_types = [int, str]

    def __init__(self):
        self.listeners = []
        self.subhooks = {}

    def listen(self, path, listener):
        if len(path) == 0:
            if listener not in self.listeners:
                self.listeners.append(listener)
            else:
                raise ValueError("listener already registered for this event")
        else:
            name = path.pop(0)
            if name not in self.subhooks:
                self.subhooks[name] = Hooks()
            self.subhooks[name].listen(path, listener)

    def remove(self, path, listener):
        if len(path) == 0:
            if listener in self.listeners:
                self.listeners.remove(listener)
            else:
                raise ValueError("cannot remove nonexisting listener")
        else:
            name = path.pop(0)
            if name in self.subhooks:
                subhook = self.subhooks[name]
                subhook.remove(path, listener)
                if len(subhook.listeners) + len(subhook.subhooks) == 0:
                    del self.subhooks[name]
            else:
                raise ValueError("cannot remove nonexisting listener")

    def emit(self, path):
        for listener in self.listeners:
            listener(*path)
        if len(path) > 0:
            name = path.pop(0)
            if type(name) in self.subhook_types and name in self.subhooks:
                print("yes")
                self.subhooks[name].emit(path)
