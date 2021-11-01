# -*- coding: utf-8 -*-
"""test_singletons test module

Created on Oct 30, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_singletons
    $ python3 -m unittest test.test_disktools.test_singletons.TestZero

"""
from test import MY_TESTDISK_PATH
import unittest

from my.disktools.partitions import add_partition, delete_partition, delete_all_partitions


class TestZero(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):

        from my.disktools.disks import threadsafeDisk
        a = threadsafeDisk(MY_TESTDISK_PATH)
        b = threadsafeDisk(MY_TESTDISK_PATH)
        self.assertEqual(a.node, b.node)
        self.assertEqual(0, len(a.partitions))
        self.assertEqual(len(a.partitions), len(b.partitions))
        self.assertEqual(a, b)
        a.add_partition(partno=1, start=5000, end=9999, fstype='83')
        self.assertEqual(a.partitions[0].node, b.partitions[0].node)
        pdev = a.partitions[0].node
        # This does not update a.partitions or b.partitions
        delete_all_partitions(MY_TESTDISK_PATH)
        self.assertEqual(b.partitions[0].node, pdev)
        self.assertEqual(a.partitions[0].node, pdev)
        self.assertEqual(len(a.partitions), len(b.partitions))
        self.assertEqual(a.partitions[0].end, 9999)
        with self.assertRaises(ValueError):
            a.add_partition(partno=1, start=5000, end=9998, fstype='83')
        a.update()
        self.assertEqual(b.partitions, [])
        self.assertEqual(a.partitions, [])
        a.add_partition(partno=1, start=5000, end=9997, fstype='83')
        self.assertEqual(b.partitions[0].end, 9997)
        self.assertEqual(a.partitions[0].end, 9997)
        delete_partition(a.node, 1)
        add_partition(disk_path=a.node, partno=1,
                      start=5000, end=7777, fstype='83')
        self.assertEqual(b.partitions[0].end, 9997)
        self.assertEqual(a.partitions[0].end, 9997)
        a.partitions[-1].update()
        self.assertEqual(b.partitions[0].end, 7777)
        self.assertEqual(a.partitions[0].end, 7777)
        a.delete_partition(1)
        self.assertEqual(b.partitions, [])
        self.assertEqual(a.partitions, [])


class TestOne(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testSimpleSingleThread(self):
        from my.disktools.disks import threadsafeDisk
        d = threadsafeDisk(MY_TESTDISK_PATH)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
