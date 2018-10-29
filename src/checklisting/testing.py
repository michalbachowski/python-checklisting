class CheckType(object):

    def __init__(self, cls):
        self._cls = cls

    def __eq__(self, other):
        return isinstance(other, self._cls)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._cls.__name__})>'


class CheckGenerator(object):

    def __init__(self, expected):
        self._expected = expected

    def __eq__(self, other):
        return list(other) == self._expected

    def __repr__(self):
        return f'<generator object of: {self._expected}>'
