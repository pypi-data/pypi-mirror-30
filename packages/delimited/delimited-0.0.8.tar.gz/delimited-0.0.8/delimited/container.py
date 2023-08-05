"""
delimited.container
~~~~~~~~~~~~~~~~~
"""

import copy

from delimited.sequence import SequenceIndex
from delimited.sequence import SequenceValue


class NestedContainer(object):
    container = None
    path = None
    sequence = None
    mapping = None
    
    def __init__(self, data=None):
        self(data)
        
    def __call__(self, data=None):
        if data is None:
            self.data = self.container()
        elif isinstance(data, self.container):
            self.data = self._wrap(data)
        else:
            raise TypeError(f"data is not of type {self.container}")
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.data == other.data
        return self.data == other
        
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.data)
        
    def __repr__(self):
        return f"{self.__class__.__name__}({self.data})"
    
    def __hash__(self):
        return hash(str(self.data))

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(len(self.data))
    
    def __contains__(self, value):
        return value in self.data
    
    def __getitem__(self, path):
        return self.ref(path)

    def __setitem__(self, path, value):
        self.set(path, value)

    def __delitem__(self, path):
        self.unset(path)

    def __copy__(self):
        new = self.__class__()
        new.data = copy.copy(self.data)
        return new

    def __deepcopy__(self, *args):
        new = self.__class__()
        new.data = copy.deepcopy(self.data)
        return new

    def _wrap(self, data):
        i = data.items() if isinstance(data, dict) else enumerate(data)
        for key, value in i:    
            if isinstance(value, dict):
                data[key] = self.mapping(data[key])
            elif isinstance(value, list):
                data[key] = self.sequence(data[key])
                
        return data
        
    def _unwrap(self, data):
        i = data.items() if isinstance(data, dict) else enumerate(data)
        for key, value in i:
            if isinstance(value, (self.mapping, self.sequence)):
                data[key] = value.get()
    
        return data
        
    def unwrap(self):
        return self._unwrap(self.data)

    def ref(self, path=None, create=False):
        if path is None:
            return self.data

        haystack = self.data

        if not isinstance(path, self.path):
            path = self.path(path)

        for i, segment in enumerate(path):
            
            s = segment.index if isinstance(segment, SequenceIndex) else segment
            
            try:
                haystack = haystack[s]

            except KeyError as e:
                if create:
                    haystack[s] = self.container()
                    haystack = haystack[s]

                else:
                    e.args = (f"{s} in {path}",) + e.args[1:]
                    raise
            
            except IndexError as e:
                if create:
                    haystack.append(self.container())
                    haystack = haystack[s]

                else:
                    e.args = (f"{s} in {path}",) + e.args[1:]
                    raise

            except TypeError as e:
                e.args = (f"{s} in {path}",) + e.args[1:]
                raise

        return haystack

    def get(self, path=None, *args):
        try:
            return copy.deepcopy(self._unwrap(self.ref(path)))
        except (KeyError, IndexError):
            if args:
                return args[0]
            raise

    def has(self, path=None):
        try:
            return bool(self.ref(path))
        except (KeyError, IndexError):
            return False

    def copy(self, path=None):
        return copy.copy(self)

    def clone(self, path=None):
        clone = self.__class__()
        clone.data = self.ref(path)
        return clone
    
    @classmethod
    def _merge(cls, a, b):
        if not isinstance(a, b.__class__):
            return copy.copy(a)
        
        b = copy.copy(b)
        iterable = a.keys() if isinstance(a, dict) else range(len(a))
        
        for k in iterable:
            
            # sequences
            if all(isinstance(v, list) for v in [a, b]):
                
                # unequal lengths
                if k > (len(b) - 1):
                    b.append(a[k])
                
                # recursive merge
                else:
                    b[k] = cls._merge(a[k], b[k])
                    
            # mappings
            elif all(isinstance(v, dict) for v in [a, b]):
                
                # key not set
                if k not in b:
                    b[k] = a[k]
                
                # recursive merge
                else:
                    b[k] = cls._merge(a[k], b[k])
        
        return b
    
    def merge(self, data, path=None):
        if isinstance(data, self.__class__):
            data = data.unwrap()
        
        return self._merge(self.get(path), data)
    
    # NOTE: expects a dict
    # def _expand(self, data):
    # 
    #     # determine type for expanded data
    #     expanded = self.container()
    # 
    #     for path, value in data.items():
    #         if not isinstance(path, self.path):
    #             path = self.path(path)
    # 
    #         for i, segment in enumerate(reversed(path)):
    # 
    #             if isinstance(segment, SequenceIndex):
    #                 index = segment.index
    #                 new_segment = [[SequenceValue()] * (index + 1)]
    # 
    #             else:
    #                 index = segment
    #                 new_segment = dict()
    # 
    #             # first segment
    #             if i == 0:
    #                 new_segment[index] = value
    #                 expanded_segment = new_segment
    # 
    #             # > first segment
    #             elif i > 0:
    #                 new_segment[index] = expanded_segment
    #                 expanded_segment = new_segment
    # 
    #             # last segment
    #             if i == (len(path) - 1):
    #                 expanded = self._merge(expanded_segment, expanded)
    # 
    #     return expanded

    def collapse(self, path=None, func=None):
        data = self if path is None else self.get(path)
        return self._collapse(data, func=func)
    
    @classmethod
    def _collapse(cls, data, func=None, _parent_path=None):

        collapsed = {}
        path = cls.path() if _parent_path is None else _parent_path

        # sequence
        if isinstance(data, cls.sequence):
            i, index = enumerate(data), cls.sequence.sequenceindex

        # mapping
        elif isinstance(data, cls.mapping):
            i, index = data.items(), None

        # all others
        else:
            return data

        for key, value in i:
            
            # NOTE: use of `func` results in current level not being collapsed
            if callable(func) and func(key, value, data.__class__):

                if isinstance(data, cls.sequence):
                    
                    # if func returns True and current level is sequence
                    # change collapsed to correct container type for merge
                    if isinstance(collapsed, dict):
                        collapsed = []
                    
                    uncollapsed = list([SequenceValue()] * (key + 1))
                    
                elif isinstance(data, cls.mapping):
                    uncollapsed = dict()

                # assign collapsed value to container
                # NOTE: by omitting `_parent_path` in collapse call below and 
                # assiging directly to container, all paths of collapsed
                # children will not include current level path
                uncollapsed[key] = cls._collapse(value, func=func)
                
                if isinstance(data, cls.sequence):
                    value = uncollapsed
                    
                elif isinstance(data, cls.mapping):
                    value = {path.encode(): uncollapsed}

            else:

                # wrap key in sequence index class if necessary
                if index is not None:
                    key = index(key)

                # NOTE: create copy of path so further extend calls do not
                # mutate current level path
                path_copy = path.copy()
                path_copy.append(key)

                # continue to collapse nested values
                value = cls._collapse(value, func=func, _parent_path=path_copy)

                # if value is not collapsable, tree has been traversed for branch
                # and value of `encoded path: value` should be returned
                if not isinstance(value, (list, dict)):
                    value = {path_copy.encode(): value}

            # update root with branch
            collapsed = cls._merge(collapsed, value)


        return collapsed
    
    def set(self, path, value, create=True):
        if not isinstance(path, self.path):
            path = self.path(path)
            
        tail = path.tail
        if path.head is None and isinstance(path.tail, SequenceIndex):
            tail = path.tail.index
            
        haystack = self.ref(path.head, create=create)
        haystack[tail] = value

    def unset(self, path, cleanup=False):
        if not isinstance(path, self.path):
            path = self.path(path)
        
        haystack = self.ref(path.head)
        
        tail = path.tail
        if path.head is None and isinstance(path.tail, SequenceIndex):
            tail = path.tail.index
        
        del haystack[tail]

        if cleanup and path.head is not None:
            if not len(haystack):
                self.unset(path.head)

        return True

    def push(self, path, value, create=True):
        if not isinstance(path, self.path):
            path = self.path(path)

        haystack = self.ref(path.head, create=create)
        
        tail = path.tail
        if path.head is None and isinstance(path.tail, SequenceIndex):
            tail = path.tail.index

        try:
            haystack[tail].append(value)

        except KeyError as e:
            if create:
                haystack[tail] = self.sequence()
                haystack[tail].append(value)
            else:
                e.args = (f"{tail} in {path}",) + e.args[1:]
                raise

        except AttributeError as e:
            if create:
                haystack[tail] = self.sequence([haystack[tail]])
                haystack[tail].append(value)
            else:
                e.args = (f"{tail} in {path}",) + e.args[1:]
                raise

        return True

    def pull(self, path, value, cleanup=False):
        if not isinstance(path, self.path):
            path = self.path(path)

        haystack = self.ref(path.head)

        tail = path.tail
        if path.head is None and isinstance(path.tail, SequenceIndex):
            tail = path.tail.index

        haystack[tail].remove(value)

        if cleanup:
            if not len(haystack[tail]):
                del haystack[tail]

        return True

