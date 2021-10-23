'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import os.path
from test import MY_TESTDISK_NODE
import unittest

from my.disktools.disks import is_this_a_disk, get_disk_record
from my.disktools.partitions import     delete_all_partitions
import sys.path
from test.test_partitiontools import SAMPLE_LIST_OF_BOGUS_PARAMS


class TestGetDiskRecord_ZERO(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        for node in SAMPLE_LIST_OF_BOGUS_PARAMS:
            with self.assertRaises(ValueError, msg='%s' % node):
                _ = get_disk_record(node)


class TestGetDiskRecord_ONE(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        _ = get_disk_record(MY_TESTDISK_NODE)


class TestGetDiskRecord_TWO(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testName(self):
        r = get_disk_record(MY_TESTDISK_NODE)
        if r.partitiontable.id not in (None, ''):
            self.assertTrue(is_this_a_disk(r.partitiontable.id))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.id)))
            self.assertEqual(os.path.realpath(r.partitiontable.id), os.path.realpath(MY_TESTDISK_NODE))
        if r.partitiontable.node not in (None, ''):
            self.assertTrue(is_this_a_disk(r.partitiontable.node))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.node)))
            self.assertEqual(os.path.realpath(r.partitiontable.node), os.path.realpath(MY_TESTDISK_NODE))
        if r.partitiontable.device not in (None, ''):
            self.assertTrue(is_this_a_disk(r.partitiontable.device))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.device)))
            self.assertEqual(os.path.realpath(r.partitiontable.device), os.path.realpath(MY_TESTDISK_NODE))
        self.assertEqual(r.partitiontable.unit, 'sectors')
        self.assertEqual(r.partitiontable.disk_label, 'dos')
        self.assertEqual(0, os.system('''fdisk -l {fname} | grep "{hexid}" >/dev/null'''.format(fname=MY_TESTDISK_NODE, hexid=r.partitiontable.disk_id)))
        self.assertEqual(512, r.partitiontable.sector_size)
        self.assertTrue(r.partitiontable.size_in_sectors > 1024 * 1024 * 1024 // r.partitiontable.sector_size)
        self.assertEqual([], r.partitiontable.partitions)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
