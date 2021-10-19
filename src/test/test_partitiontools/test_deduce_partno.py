'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import os
import sys
import unittest
from my.partitiontools import is_this_a_disk, deduce_partno
from test.test_partitiontools import SAMPLE_LIST_OF_BOGUS_PARAMS, \
    SAMPLE_LIST_OF_DRIVES_STUBS, SAMPLE_LIST_OF_DODGY_STUBS


class TestDeducePartno(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAbilityToRejectBadParams(self):
        for i in SAMPLE_LIST_OF_BOGUS_PARAMS:
            with self.assertRaises(ValueError, msg='%s' % i):
                _ = deduce_partno(i)

    def testAbilityToReturnTrueCorrectly(self):
        for stub in SAMPLE_LIST_OF_DRIVES_STUBS:
            node = '/dev/%s' % (stub)
            self.assertTrue(is_this_a_disk(node, insist_on_this_existence_state=True), "%s *is* a disk, actually" % node)

    def testAbilityToReturnFalseCorrectly(self):
        for stub in SAMPLE_LIST_OF_DRIVES_STUBS:
            if 'mmc' in stub:
                stub += 'p'
            for i in range(1, 105):
                node = '/dev/%s%d' % (stub, i)
            with self.assertRaises(ValueError):
                _ = is_this_a_disk(node, insist_on_this_existence_state=False)

    def testAbilityToFail(self):
        for stub in SAMPLE_LIST_OF_DODGY_STUBS:
            node = '/dev/%s' % (stub)
            with self.assertRaises(ValueError):
                _ = is_this_a_disk(node)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
