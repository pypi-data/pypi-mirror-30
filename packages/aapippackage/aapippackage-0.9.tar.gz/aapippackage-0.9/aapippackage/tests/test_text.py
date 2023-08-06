from unittest import TestCase

import aapippackage

class TestText(TestCase):
    def test_helloworld(self):
        s = aapippackage.helloworld()
        self.assertTrue(isinstance(s, basestring))