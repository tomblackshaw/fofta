# -*- coding: utf-8 -*-
"""test_get_disk_record test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.utils
    $ python3 -m unittest test.utils.Test

"""
import os
import sys
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']

    sys.path.append(os.getcwd())
    unittest.main()
