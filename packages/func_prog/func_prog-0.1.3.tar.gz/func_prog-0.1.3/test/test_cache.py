import unittest
from func_prog.cache import func_cache


@func_cache
def func(a_tuple, a_dict):
    print('computing for func')
    return a_tuple[0] + a_dict['x']


class ExampleClass(object):
    @func_cache
    def method(self, a_tuple, a_dict):
        print('computing for method')
        return a_tuple[0] + a_dict['x']


class TestCache(unittest.TestCase):
    def test_func_cache(self):
        self.assertEqual(func._cache, {})
        for _ in range(3):
            result = func((1, 2), a_dict={'x': 2})
            self.assertEqual(result, 3)
            self.assertEqual(
                tuple(func._cache.values())[0],
                3)

    def test_method_cache(self):
        obj = ExampleClass()
        self.assertEqual(obj.method._cache, {})
        for _ in range(3):
            result = obj.method((1, 2), a_dict={'x': 2})
            self.assertEqual(result, 3)
            self.assertEqual(
                tuple(obj.method._cache.values())[0],
                3)
