# -*- coding: utf-8 -*-
"""test_get_disk_record test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_is_this_a_disk
    $ python3 -m unittest test.test_disktools.test_is_this_a_disk.TestIsThiSADisk_One

"""
import os
import sys
import unittest
from my.disktools.disks import is_this_a_disk
from test.test_disktools import SAMPLE_LIST_OF_BOGUS_PARAMS, \
    SAMPLE_LIST_OF_DRIVES_STUBS, SAMPLE_LIST_OF_DODGY_STUBS


class TestIsThisADisk_ONE(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAbilityToNoticeDisks(self):
        for stub in SAMPLE_LIST_OF_DRIVES_STUBS:
            node = '/dev/%s' % (stub)
            self.assertTrue(is_this_a_disk(node, insist_on_this_existence_state=True), "%s *is* a disk, actually" % node)

    def testAbilityToNoticeNotdisks(self):
        for stub in SAMPLE_LIST_OF_DRIVES_STUBS:
            if 'mmc' in stub:
                stub += 'p'
            for i in range(1, 105):
                node = '/dev/%s%d' % (stub, i)
            self.assertFalse(is_this_a_disk(node, insist_on_this_existence_state=True), "%s *isn't* a disk, actually" % node)

    def testAbilityToFail(self):
        for stub in SAMPLE_LIST_OF_DODGY_STUBS:
            node = '/dev/%s' % (stub)
            with self.assertRaises(ValueError):
                _ = is_this_a_disk(node, insist_on_this_existence_state=True)


class TestIsThisADisk_TWO(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIfExistenceMakesADifference(self):
        for i in ('/dev/mmcblk0', '/dev/mmcblk1', '/dev/sda', '/dev/sdb', '/dev/sdp'):
            self.assertTrue(is_this_a_disk(device_path=i, insist_on_this_existence_state=True))
            self.assertTrue(is_this_a_disk(device_path=i, insist_on_this_existence_state=True))
        for i in ('/dev/mmcblk0p1', '/dev/mmcblk9p5', '/dev/mmcblk69p44', '/dev/sda1', '/dev/sdb8', '/dev/sdc99', '/dev/sdp5'):
            self.assertFalse(is_this_a_disk(device_path=i, insist_on_this_existence_state=True))
            self.assertFalse(is_this_a_disk(device_path=i, insist_on_this_existence_state=True))


class TestIsThisADisk_THREE(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAbilityToRejectBadParams(self):
        for i in SAMPLE_LIST_OF_BOGUS_PARAMS:
            with self.assertRaises(ValueError):
                _ = is_this_a_disk(i, insist_on_this_existence_state=True)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()