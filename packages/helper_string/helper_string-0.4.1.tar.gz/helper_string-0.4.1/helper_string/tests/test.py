#coding:utf8
import unittest

import helper_string

class TestStringMethods(unittest.TestCase):

    def test_to_str(self):
        self.assertEqual("中文", helper_string.HelperString.to_str(u"中文"))

        expected = {"k1": "中文", "k2": {"k": "中文"}}
        got = helper_string.HelperString.to_str({"k1": u"中文", u"k2": {"k": u"中文"}})
        self.assertDictEqual(expected, got)

    def test_to_uni(self):
        self.assertEqual(u"中文", helper_string.HelperString.to_uni("中文"))