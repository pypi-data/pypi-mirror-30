"""
delimited.mapping
~~~~~~~~~~~~~~~~~
"""


class NestedMapping(object):

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value

    def items(self):
        for key, value in self.data.items():
            yield (key, value)

    def keys(self):
        for key in self.data.keys():
            yield key

    def values(self):
        for value in self.data.values():
            yield value

    def update(self, data, path=None):
        if isinstance(data, self.__class__):
            data = data.unwrap()

        self.ref(path).update(data)
