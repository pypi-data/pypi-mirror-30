from unittest import TestCase

import aapippackage
import logging

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

class TestDictonary(TestCase):
    def test_dict_helper_flatten(self):
        data = [1, 2, [3, [4, 5, [6, 7]]]]
        a = aapippackage.flatten(data)
        self.assertEqual(a, [1, 2, 3, 4, 5, 6, 7])
        data = []
        a = aapippackage.flatten(data)
        self.assertEqual(a, [])

    def test_dict_helper_find_values(self):
        data = {"a":"1","b":"2"}
        res = aapippackage.find_values_json("a", data)
        self.assertEqual(res, [u'1'])
    
    def test_depth(self):
        data  = [1, [2, [3, [4]], 5]]
        a = aapippackage.depth(data)
        self.assertEqual(a,4)
        data = []
        a = aapippackage.depth(data)
        self.assertEqual(a,0)

    def test_convertlistdicttosingelist(self):
        data = [1,2,3,4,{"a":"1"}]
        a = aapippackage.convertlistdicttosingelist(data)
        self.assertEqual(a,[{'a': '1'}])

    def test_convertlistdicttoordereddict(self):
        data = [{"a":1,"b":2},{"a":3,"b":4},{"a":5,"b":6}]
        a = aapippackage.convertlistdicttoordereddict(data)
        self.assertEqual(a, OrderedDict([('a', 5), ('b', 6)]))
    
    def test_returnpythonobject(self):
        data = "{'a':1,'b':1}"
        a = aapippackage.returnpythonobject(data)
        self.assertIsInstance(a, dict)
    
    def test_capnumberofmonths(self):
        months = 5
        a = aapippackage.capnumberofmonths(months)
        self.assertEqual(a, 5)
        b = aapippackage.capnumberofmonths(17)
        self.assertEqual(b, 16)