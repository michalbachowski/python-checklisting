class CheckType(object):

    def __init__(self, cls):
        self._cls = cls

    def __eq__(self, other):
        return isinstance(other, self._cls)


class CheckGenerator(object):

    def __init__(self, expected):
        self._expected = expected

    def __eq__(self, other):
        return list(other) == self._expected
