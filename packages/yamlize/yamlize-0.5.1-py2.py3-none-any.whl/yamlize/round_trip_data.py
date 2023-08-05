from .pickle_helper import pickle_slotted


class _AnchorNode(object):
    # TODO: replace with ruamel.yaml.comments.Anchor

    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value


@pickle_slotted
class RoundTripData(object):

    __slots__ = ('_rtd', '_kids_rtd', '_name_order')  # can't use private variables with six

    def __init__(self, node):
        self._rtd = {}
        self._kids_rtd = {}
        self._name_order = []

        if node is not None:
            for key in ('comment', 'tag', 'anchor'):
                attr = getattr(node, key)
                self._rtd[key] = attr

            flow_style = getattr(node, 'flow_style', None)

            if flow_style is not None:
                self._rtd['flow_style'] = flow_style

    def __bool__(self):
        return len(self._rtd) > 0

    __nonzero__ = __bool__

    def apply(self, node):
        for key, val in self._rtd.items():
            if key == 'anchor':
                val = _AnchorNode(val)
            setattr(node, key, val)

    def __get_key(self, key):
        try:
            return hash(key)
        except TypeError:
            return type(key), id(key)

    def __setitem__(self, key, rtd):
        # don't bother storing if there wasn't any data
        if rtd:
            self._kids_rtd[self.__get_key(key)] = rtd

    def __getitem__(self, key):
        return self._kids_rtd.get(self.__get_key(key), RoundTripData(None))

