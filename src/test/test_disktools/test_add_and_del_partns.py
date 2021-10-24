'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import os
import sys
from test import MY_TESTDISK_NODE
import unittest

from my.disktools.partitions import delete_partition, delete_all_partitions, add_partition, was_this_partition_created


class TestSimpleDeleteAll(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        delete_all_partitions(MY_TESTDISK_NODE)


class TestSimpleAddAndAllDel(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        add_partition(node=MY_TESTDISK_NODE, partno=1,
                      start=2048, end=999999, fstype='83')  # , debug, size_in_MiB)
        realnode = os.path.realpath(MY_TESTDISK_NODE)
        self.assertTrue(was_this_partition_created(realnode, 1))
        delete_all_partitions(MY_TESTDISK_NODE)


class TestSimpleAddAndIndividualDel(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testName(self):
        realnode = os.path.realpath(MY_TESTDISK_NODE)
        for i in range(3):
            self.assertFalse(was_this_partition_created(realnode, 1))
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, 1))
            add_partition(node=MY_TESTDISK_NODE, partno=1, start=2048, end=999999, fstype='83')  # , debug, size_in_MiB)
            self.assertTrue(was_this_partition_created(realnode, 1))
            self.assertTrue(was_this_partition_created(MY_TESTDISK_NODE, 1))
            delete_partition(MY_TESTDISK_NODE, 1)
            self.assertFalse(was_this_partition_created(realnode, 1))
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, 1))


class TestAnMBAddAndIndividualDel(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testName(self):
        realnode = os.path.realpath(MY_TESTDISK_NODE)
        for i in range(3):
            self.assertFalse(was_this_partition_created(realnode, 1))
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, 1))
            add_partition(node=MY_TESTDISK_NODE, partno=1, start=2048, size_in_MiB=1000, fstype='83')
            self.assertTrue(was_this_partition_created(realnode, 1))
            self.assertTrue(was_this_partition_created(MY_TESTDISK_NODE, 1))
            delete_partition(MY_TESTDISK_NODE, 1)
            self.assertFalse(was_this_partition_created(realnode, 1))
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, 1))


class TestCreateAndDeleteFourPartitions(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testPartprobeNecessity(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            wozzit_A = was_this_partition_created(MY_TESTDISK_NODE, partno)
            os.system('sync;sync;sync; partprobe; sync;sync;sync')
            wozzit_B = was_this_partition_created(MY_TESTDISK_NODE, partno)
            self.assertTrue(wozzit_B)
            self.assertTrue(wozzit_A)
            self.assertEqual(res, 0)

    def testMakeAndDelWithXtraProbe(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            os.system('sync;sync;sync; partprobe; sync;sync;sync')
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithProbeButNoSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, was_this_partition_created(MY_TESTDISK_NODE, partno))
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            os.system('partprobe')
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithPartialProbeAndNoSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, was_this_partition_created(MY_TESTDISK_NODE, partno))
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            os.system('partprobe {node}'.format(node=MY_TESTDISK_NODE))
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithSyncButNoProbe(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, was_this_partition_created(MY_TESTDISK_NODE, partno))
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            os.system('sync;sync;sync')
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithoutProbeOrSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)


class TestCreate123Delete2Remake2(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testName(self):
        size_in_sectors = 1000000
        starts = {}
        for partno in range(1, 3):
            self.assertFalse(was_this_partition_created(MY_TESTDISK_NODE, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(node=MY_TESTDISK_NODE, partno=partno, start=start, end=end, fstype='83')  # , debug, size_in_MiB)
            self.assertEqual(True, was_this_partition_created(MY_TESTDISK_NODE, partno))
            self.assertEqual(res, 0)
            starts[str(partno)] = start
        delete_partition(MY_TESTDISK_NODE, 2)
        add_partition(MY_TESTDISK_NODE, 2, start=starts['2'])


class TestCreateAndDeleteFivePartitions(unittest.TestCase):

    def setUp(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_NODE)

    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
