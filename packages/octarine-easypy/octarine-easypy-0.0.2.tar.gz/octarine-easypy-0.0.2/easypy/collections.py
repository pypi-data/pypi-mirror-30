from __future__ import absolute_import
import collections
from numbers import Integral
from itertools import chain, islice
from functools import partial
import random
from .predicates import make_predicate
from .tokens import UNIQUE

import sys
if sys.version_info[:2] >= (3, 5):
    # In order to support 'get_prev' and 'get_next', we need access to OrderedDict's internal .__map,
    # which we don't have in the C-implementation of the class in Python3.5
    # This hack allows us to get to the pythonic implemenation of OrderedDict
    from test.support import import_fresh_module
    PythonOrderedDict = import_fresh_module('collections', blocked=['_collections']).OrderedDict
else:
    from collections import OrderedDict as PythonOrderedDict


class ObjectNotFound(LookupError):
    pass


class defaultlist(list):

    def __init__(self, fx):
        self._fx = fx
        super().__init__()

    def _fill(self, index):
        while len(self) <= index or (len(self) == 0 and index == -1):
            self.append(self._fx())

    def __setitem__(self, index, value):
        self._fill(index)
        list.__setitem__(self, index, value)

    def __getitem__(self, index):
        self._fill(index)
        return list.__getitem__(self, index)


def _get_value(obj, attr):
    value = getattr(obj, attr)
    if callable(value):
        value = value()
    return value


def _validate(obj, key, value):
    assert value is not UNIQUE, "Can't specify %s except with '.sample()'" % UNIQUE
    actual = _get_value(obj, key)
    return actual == value


def filters_to_predicates(filters):
    return [make_predicate(partial(_validate, key=key, value=value))
            for key, value in filters.items()]


def filtered(objects, preds, filters):
    preds = [make_predicate(p) for p in preds]
    preds += filters_to_predicates(filters)

    # don't collapse into one line so easier to debug
    for obj in objects:
        for pred in preds:
            if not pred(obj):
                break
        else:
            yield obj


def uniquify(items, num, attrs):
    item_map = {}
    partitions = collections.defaultdict(lambda: collections.defaultdict(set))

    for item in items:
        k = id(item)
        item_map[k] = item
        for attr in attrs:
            value = _get_value(item, attr)
            partitions[attr][value].add(k)

    if not all(len(group.values()) >= num for group in partitions.values()):
        return []

    def gen(available, collected=[]):
        if len(collected) == num:
            yield [item_map[k] for k in collected]
            return

        for k in shuffled(available):
            excluded = {i for attr in attrs for i in partitions[attr][_get_value(item_map[k], attr)]}
            remain = available - {k} - excluded
            yield from gen(remain, collected=collected + [k])

    try:
        return next(gen(set(item_map.keys())))
    except StopIteration:
        return []


# Inspired by code written by Rotem Yaari

class ObjectCollection(object):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        returned = 0
        for _ in self:
            returned += 1
        return returned

    def __nonzero__(self):
        for _ in self:
            return True
        return False

    def _new(self, items):
        return self.__class__(items)

    def _getitem(self, index):
        if isinstance(index, Integral):
            if index < 0:
                return list(self)[index]
            try:
                return next(islice(self, index, index+1))
            except StopIteration:
                raise LookupError(index)
        elif isinstance(index, slice):
            try:
                return self._new(islice(self, index.start, index.stop, index.step))
            except StopIteration:
                raise LookupError(index)
        else:
            return self.get(index)

    def __getitem__(self, index):
        return self._getitem(index)

    def __repr__(self):
        return repr(list(self))

    def __str__(self):
        return str(list(self))

    def get_by_key(self, key):
        return self.get(key=key)

    def get_by_uid(self, uid):
        return self.get_by_key(uid)

    def safe_get_by_key(self, key):
        try:
            return self.get_by_key(key)
        except ObjectNotFound:
            return None

    def safe_get_by_uid(self, uid):
        return self.safe_get_by_key(uid)

    def get_by_keys(self, keys):
        gen = map(self.get_by_key, keys)
        try:
            return type(keys)(gen)  # return something of the same type as keys
        except TypeError:  # keys is generator type - return a generator
            return gen

    def iter_filtered(self, *preds, **filters):
        _shuffle = filters.pop("_shuffle", False)
        if _shuffle:
            objects = list(self)
            random.shuffle(objects)
        else:
            objects = self
        return filtered(objects, preds, filters)

    def select(self, *preds, **filters):
        return ListCollection(self.iter_filtered(*preds, **filters))

    def safe_get(self, *preds, **filters):
        # this python fu avoids filtering the entire list, while still checking for one item
        matching = [obj for obj, _ in zip(self.iter_filtered(*preds, **filters), range(2))]
        if len(matching) > 1:
            raise ObjectNotFound("More than one object found")
        return matching[0] if matching else None

    def _format_filter_string(self, preds, filters):
        returned = ""
        if preds:
            returned += " predicates=[%s]" % ", ".join(map(str, preds))
        if filters:
            returned += " filters=[%s]" % ", ".join("%s=%r" % item for item in filters.items())
        return returned

    def get(self, *preds, **filters):
        # this python fu avoids filtering the entire list, while still checking for one item
        matching = [obj for obj, _ in zip(self.iter_filtered(*preds, **filters), range(2))]
        if len(matching) == 0:
            raise ObjectNotFound("No objects found (%s)" % self._format_filter_string(preds, filters))
        if len(matching) != 1:
            raise ObjectNotFound("Found more than a single object (%s, %s)" % (len(matching), self._format_filter_string(preds, filters)))
        return matching[0]

    def choose(self, *preds, **filters):
        for obj in self.iter_filtered(_shuffle=True, *preds, **filters):
            return obj
        raise ObjectNotFound("No objects found (%s)" % self._format_filter_string(preds, filters))

    def safe_choose(self, *preds, **filters):
        try:
            return self.choose(*preds, **filters)
        except ObjectNotFound:
            return None

    def filtered(self, *preds, **filters):
        return FilterCollection(self, preds, filters)

    def shuffled(self):
        return self.sample(len(self))

    def sorted(self, key=None):
        return self._new(sorted(self, key=key))

    def sample(self, num, *preds, **filters):
        """
        If 'num' is negative, leaves 'num' out of the sample:

            >>> ListCollection([1, 2, 3]).sample(-1)
            [1, 3]
        """
        if num < 0:
            num += len(self)

        if isinstance(num, float):
            num, d = divmod(num, 1)
            assert d == 0, "Can't sample a non-integer number of items"
            num = int(num)

        if not num:
            return self._new([])

        uniquifiers = []
        for k, v in list(filters.items()):
            if v is UNIQUE:
                filters.pop(k)
                uniquifiers.append(k)

        if uniquifiers:
            if (preds or filters):
                matching = self.iter_filtered(_shuffle=True, *preds, **filters)
            else:
                matching = self

            matching = uniquify(matching, num, uniquifiers)

        else:
            # use 'zip' as a limiter
            matching = [obj for _, obj in zip(range(num), self.iter_filtered(_shuffle=True, *preds, **filters))]

        if len(matching) < num:
            raise ObjectNotFound("Not enough objects for sampling (need at least %s)" % num)

        return self._new(matching)

    def _choose_sampling_size(self, minimum=0, maximum=None):
        if minimum < 0:
            minimum += len(self)
        if maximum is None:
            maximum = len(self)
        elif maximum < 0:
            maximum += len(self)
        maximum = min(maximum, len(self))
        return random.randint(minimum, maximum)

    def sample_some(self, minimum=0, maximum=None):
        sample_size = self._choose_sampling_size(minimum, maximum)
        return self.sample(sample_size)

    def without(self, *items_to_exclude):
        def filter(item):
            return item not in items_to_exclude
        return self.filtered(filter)

    @property
    def M(self):
        from .concurrency import MultiObject
        return MultiObject(self)

    def __add__(self, collection):
        return AggregateCollection([self, collection])


class AggregateCollection(ObjectCollection):
    def __init__(self, collections):
        super().__init__()
        self._collections = collections

    def __iter__(self):
        return chain(*self._collections)

    def __add__(self, collection):
        return AggregateCollection(self._collections + [collection])

    def _new(self, items):
        return ListCollection(items)


class ListCollection(list, ObjectCollection):

    def pop_some(self, minimum=0, maximum=None):
        sample_size = self._choose_sampling_size(minimum, maximum)
        return self._new([self.pop() for i in range(sample_size)])


class SimpleObjectCollection(ObjectCollection):
    ID_ATTRIBUTE = 'uid'

    class Collectable():
        """
        objects get assigned with a backpointer to the collection they were put in, via .collection
        """
        collection = None

    def __init__(self, objs=(), ID_ATTRIBUTE=None, backref=False):
        super().__init__()
        if ID_ATTRIBUTE:
            self.ID_ATTRIBUTE = ID_ATTRIBUTE
        self._objects = PythonOrderedDict()
        for obj in objs:
            self.add(obj, backref=backref)

    def _new(self, items):
        return self.__class__(items, self.ID_ATTRIBUTE)

    def _get_object_uid(self, obj):
        return getattr(obj, self.ID_ATTRIBUTE)

    def _add_and_get_uid(self, obj):
        uid = self._get_object_uid(obj)
        self._objects[uid] = obj
        return uid, obj

    def add(self, obj, backref=False):
        if backref:
            assert isinstance(obj, self.Collectable), "Can add backref only to Collectable classes"
            assert obj.collection is None or obj.collection is self, \
                "Collectable object not allowed to be added to multiple collections"
            obj.collection = self
        return self._add_and_get_uid(obj)[1]

    def _remove_and_get_uid(self, obj):
        uid = self._get_object_uid(obj)
        return uid, self._objects.pop(uid)

    def remove(self, obj):
        return self._remove_and_get_uid(obj)[1]

    def clear(self):
        self._objects.clear()

    def remove_by_uid(self, uid):
        obj = self._objects.pop(uid)
        return obj

    def get(self, *preds, **filters):
        if len(preds) == 1 and not filters and not callable(preds[0]):
            key, = preds
            return self.get_by_key(key)
        return super().get(*preds, **filters)

    def get_by_key(self, key):
        if key not in self._objects:
            raise ObjectNotFound(key)
        return self._objects[key]

    def index(self, obj):
        lookup_uid = self._get_object_uid(obj)
        if lookup_uid not in self._objects:
            raise ValueError("%s not in collection", obj)
        for i, uid in enumerate(self._objects.keys()):
            if lookup_uid == uid:
                return i

    def get_next(self, obj):
        uid = self._get_object_uid(obj)
        if uid not in self._objects:
            raise ObjectNotFound(uid)
        next_uid = self._objects._OrderedDict__map[uid].next
        try:
            key = next_uid.key
        except AttributeError:
            key = next_uid.next.key
        return self._objects[key]

    def get_prev(self, obj):
        uid = self._get_object_uid(obj)
        if uid not in self._objects:
            raise ObjectNotFound(uid)
        prev_uid = self._objects._OrderedDict__map[uid].prev
        try:
            key = prev_uid.key
        except AttributeError:
            key = prev_uid.prev.key
        return self._objects[key]

    def keys(self):
        return self._objects.keys()

    def __iter__(self):
        return iter(self._objects.values())

    def __len__(self):
        return len(self._objects)

    @property
    def M(self):
        from .concurrency import MultiObject
        return MultiObject(self, list(self._objects.keys()))


class FilterCollection(ObjectCollection):
    def __init__(self, base, preds, filters, parent=None):
        super().__init__()
        self.base = base
        self.parent = parent if parent is not None else base
        self.preds = preds
        self.filters = filters

    def _new(self, items):
        if hasattr(self.base, 'ID_ATTRIBUTE'):
            return self.base.__class__(items, ID_ATTRIBUTE=self.base.ID_ATTRIBUTE)
        return self.base.__class__(items)

    def __iter__(self):
        return self.iter_filtered()

    def iter_filtered(self, *preds, **filters):
        _shuffle = filters.pop("_shuffle", False)
        combined_preds = list(self.preds)
        combined_preds += preds
        for k, v in self.filters.items():
            if k in filters:
                assert v == filters[k], "Two different values provided for the same filter key!"
        filters.update(self.filters)
        return self.parent.iter_filtered(_shuffle=_shuffle, *combined_preds, **filters)

    def filtered(self, *preds, **filters):
        return FilterCollection(self.base, preds, filters, parent=self)

    def get(self, *preds, **filters):
        if len(preds) == 1 and not filters and not callable(preds[0]):
            key, = preds
            return self.get_by_key(key)
        else:
            return super().get(*preds, **filters)

    def get_by_key(self, key):
        for obj in filtered([self.base.get_by_key(key)], self.preds, self.filters):
            return obj
        raise ObjectNotFound(key)

    def get_next(self, obj):
        while True:
            next_obj = self.base.get_next(obj)
            if any(filtered([next_obj], self.preds, self.filters)):
                return next_obj
            obj = next_obj

    def __getitem__(self, uid):
        if not isinstance(uid, str):
            return super().__getitem__(uid)
        objs = filtered([self.base[uid]], self.preds, self.filters)
        if not objs:
            raise ObjectNotFound(uid)
        for obj in objs:
            return obj
        raise ObjectNotFound(uid)


def TypeFilterCollection(base, type):
    return base.filtered(lambda obj: isinstance(obj, type))


class IteratorBasedCollection(ObjectCollection):

    def __init__(self, iterator_func):
        super().__init__()
        self._iterator_func = iterator_func

    def __iter__(self):
        return self._iterator_func()


class IndexedObjectCollection(SimpleObjectCollection):

    def __init__(self, objs=(), keys=(), **kwargs):
        self._indices = {key: collections.defaultdict(set) for key in keys}
        super().__init__(objs, **kwargs)

    def _new(self, items):
        return self.__class__(items, keys=self._indices.keys(), ID_ATTRIBUTE=self.ID_ATTRIBUTE)

    def add(self, obj):
        uid, obj = self._add_and_get_uid(obj)
        for key, uid_map in self._indices.items():
            value = getattr(obj, key)
            uid_map[value].add(uid)

    def remove(self, obj):
        uid, obj = self._remove_and_get_uid(obj)
        for uid_map in self._indices.values():
            for uids in uid_map.values():
                uids.discard(uid)
        return obj

    def clear(self):
        self._objects.clear()
        for idx in self._indices.values():
            idx.clear()

    def remove_by_uid(self, uid):
        return self.remove(self._objects[uid])

    def get(self, *preds, **filters):
        if len(preds) == 1 and not filters and not callable(preds[0]):
            key, = preds
            return self.get_by_key(key)
        return super().get(*preds, **filters)

    def iter_filtered(self, *preds, **filters):
        _shuffle = filters.pop("_shuffle", False)
        indexed = set(filters) & set(self._indices)
        unindexed = set(filters) - indexed
        if indexed:
            filtered_keys = set.intersection(*(self._indices.get(key, {}).get(filters[key], set()) for key in indexed))
            objects = (self.get_by_key(key) for key in filtered_keys)
        else:
            objects = self
        if _shuffle:
            objects = list(objects)
            random.shuffle(objects)
        if not (preds or unindexed):
            return objects
        filters = {k: filters[k] for k in unindexed}
        return filtered(objects, preds, filters)


def grouped(sequence, key=None, transform=None):
    """
    Parse the sequence into groups, according to key:

        >>> grouped(range(10), lambda n: n % 3 == 0)
        {False: [1, 2, 4, 5, 7, 8], True: [0, 3, 6, 9]}
    """
    groups = {}
    if not key:
        key = lambda x: x
    if not transform:
        transform = lambda x: x
    for item in sequence:
        groups.setdefault(key(item), []).append(transform(item))
    return groups


def separate(sequence, key=None):
    """
    Partition the sequence into items that don't match (nonzero) and those do:

        >>> above_three, three_or_less = separate(range(10), lambda n: n > 3)

        >>> print(three_or_less)
            [0, 1, 2, 3]

        >>> print(above_three)
            [4, 5, 6, 7, 8, 9]
    """
    if not key:
        key = lambda x: x
    groups = grouped(sequence, key=lambda e: bool(key(e)))
    return groups.get(True, []), groups.get(False, [])


def iterable(obj):
    return isinstance(obj, collections.Iterable) and not isinstance(obj, (str, bytes, dict))


def ilistify(obj):
    """
    Conform input into an iterable:

        >>> list(ilistify(1))
        [1]
        list(ilistify([1, 2, 3]))
        [1, 2, 3]
    """
    if not iterable(obj):
        yield obj
    else:
        yield from obj


listify = lambda obj: list(ilistify(obj))


def chunkify(sequence, size):
    """
    Chunk a sequence into equal-size chunks:

        >>> ["".join(p) for p in chunkify('abcdefghijklmnopqrstuvwxyz', 7)]
        ['abcdefg', 'hijklmn', 'opqrstu', 'vwxyz']
    """
    sequence = iter(sequence)
    while True:
        chunk = [e for _, e in zip(range(size), sequence)]
        if not chunk:
            return
        yield chunk


def partial_dict(d, keys):
    """
    Returns a new dict with a subset of the original items

    >>> partial_dict({'a': 1, 'b': 2, 'c': 3}, ['a', 'b'])
    {'a': 1, 'b': 2}
    """
    return {k: d[k] for k in keys}


def intersected_dict(d, keys):
    """
    Returns a new dict with a subset of the original items.
    Items that are specified in keys but not in the original dict are discarded

    >>> intersected_dict({'a': 1, 'b': 2, 'c': 3}, ['a', 'b', 'z'])
    {'a': 1, 'b': 2}
    """
    return {k: d[k] for k in keys if k in d}


def dicts_to_table(dicts, index_header="idx"):
    if isinstance(dicts, dict):
        _, sample_row = next(iter(dicts.items()))
        rows = ((key, dicts[key]) for key in sorted(dicts))
    else:
        sample_row = dicts[0]
        rows = enumerate(dicts)
    headers = sorted(sample_row.keys())
    table = [[index_header] + headers]
    for key, row in rows:
        table.append([key] + [row[header] for header in headers])
    return table


def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l


class SlidingWindow(list):
    """
    A list that maintains a constant size, popping old items as new items are appended (FIFO)
    """
    def __init__(self, *args, size):
        self.size = size
        super().__init__(*args)

    def append(self, item):
        super().append(item)
        if len(self) > self.size:
            self.pop(0)
