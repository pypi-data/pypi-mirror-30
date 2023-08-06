from collections import defaultdict


class func_cache(object):
    '''
        A decorator to cache the function or method result.
    '''
    def __init__(self, function):
        self._function = function
        self._function_self = None
        self.__doc__ = function.__doc__
        self.__name__ = function.__name__
        self._cache = defaultdict(dict)

    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in self._cache:
            if self._function_self:
                obj_key = id(self._function_self)
                self._cache[obj_key][key] = self._function(self._function_self, *args, **kwargs)
            else:
                obj_key = 'None'
                self._cache[obj_key][key] = self._function(*args, **kwargs)
        return self._cache[obj_key][key]

    def __get__(self, instance, owner):
        self._function_self = instance
        return self
