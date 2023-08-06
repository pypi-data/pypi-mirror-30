# -*- coding: utf-8 -*-

import time
import unittest

from classutils import class_cache_result, clear_class_cached_results


class CachedProperties(object):

    def __init__(self):
        self.reset()

    @property
    @class_cache_result
    def property_1(self):
        self.count += 1
        return self.count

    @property
    @class_cache_result
    def property_2(self):
        self.count += 1
        return self.count

    @property
    @class_cache_result(timeout=3)
    def property_3(self):
        self.count += 1
        return self.count

    @clear_class_cached_results
    def reset(self):
        self.count = 0


class TestResettableCachedProperties(unittest.TestCase):

    def setUp(self):
        self.result_cacher = CachedProperties()

    def test_cached(self):
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)

        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)

    def test_cached_timeout(self):
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)

        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)

        time.sleep(1)

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)

        time.sleep(2)

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(4, self.result_cacher.property_3)
        self.assertEqual(4, self.result_cacher.property_3)

    def test_resetable(self):

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)

        self.result_cacher.reset()

        self.assertEqual(1, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_1)


if __name__ == u'__main__':
    unittest.main()
