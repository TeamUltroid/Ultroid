from .. import udB

class KeyManager():

    def __init__(self, key, cast=None) -> None:
        self._key = key
        if callable(cast):
            self.cast = cast()
        else:
            self.cast = cast
    
    def get(self):
        return udB.get_key(self._key) or self.cast
    
    def get_child(self, key):
        return self.get()[key]

    def count(self):
        return len(self.get())

    def add(self, item):
        content = self.get()
        if isinstance(item, dict):
            content.update(item)
        elif isinstance(item, list):
            content.append(item)
        else:
            return
        udB.set_key(self._key, content)
    
    def remove(self, item):
        content = self.get()
        if isinstance(content, list):
            content.pop(content)
        else:
            del content[item]
        udB.set_key(self._key, item)

    def contains(self, item):
        return item in self.get()

