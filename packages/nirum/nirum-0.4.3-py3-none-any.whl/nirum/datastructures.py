""":mod:`nirum.datastructures` --- Immutable data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.4.0

"""
import collections

__all__ = 'List', 'Map', 'list_type', 'map_type'


class Map(collections.Mapping):
    """As Python standard library doesn't provide immutable :class:`dict`,
    Nirum runtime itself need to define one.

    """

    __slots__ = 'value',

    def __init__(self, *args, **kwargs):
        # TODO: type check on elements
        self.value = dict(*args, **kwargs)

    def __eq__(self, other):
        if not (isinstance(other, collections.Mapping) and
                len(self.value) == len(other)):
            return False
        for k, v in self.items():
            if k in other and other[k] == v:
                continue
            return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, key):
        return self.value[key]

    def __contains__(self, key):
        return key in self.value

    def __reduce__(self):
        return type(self), (self.value,)

    def __bool__(self):
        return bool(self.value)

    __nonzero__ = __bool__

    def __hash__(self):
        return hash(tuple(self.items()))

    def __repr__(self):
        if self:
            items = sorted(self.value.items())
            format_item = '{0!r}: {1!r}'.format
            args = '{' + ', '.join(format_item(*item) for item in items) + '}'
        else:
            args = ''
        return '{0.__module__}.{0.__name__}({1})'.format(type(self), args)


class List(collections.Sequence):

    def __init__(self, l):
        self.l = l  # noqa: E741

    def __eq__(self, other):
        if not (isinstance(other, collections.Sequence) and
                len(self) == len(other)):
            return False
        for a, b in zip(self, other):
            if a == b:
                continue
            return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __getitem__(self, index):
        return self.l[index]

    def __len__(self):
        return len(self.l)

    def __contains__(self, item):
        return item in self.l

    def __iter__(self):
        return iter(self.l)

    def __hash__(self):
        return hash(tuple(self))

    def index(self, item):
        return self.l.index(item)

    def count(self, item):
        return self.l.count(item)


map_type = Map
list_type = List
