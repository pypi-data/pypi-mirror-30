class func_cache(object):
    '''
        A decorator to cache the function or method result.
    '''
    def __init__(self, function):
        self._function = function
        self._function_self = None
        self.__doc__ = function.__doc__
        self.__name__ = function.__name__
        self._cache = {}

    def __call__(self, *args, **kwargs):
        obj_key = id(self._function_self)
        param_key = str(args) + str(kwargs)
        key = str(obj_key) + '-' + param_key
        if key not in self._cache:
            if self._function_self:
                self._cache[key] = self._function(
                    self._function_self, *args, **kwargs)
            else:
                self._cache[key] = self._function(*args, **kwargs)
        return self._cache[key]

    def __get__(self, instance, owner):
        self._function_self = instance
        return self
