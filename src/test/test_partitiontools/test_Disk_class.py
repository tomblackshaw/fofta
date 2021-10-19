'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import os
import sys
from test import MY_TESTDISK_NODE
import unittest
import unittest

from my.partitiontools import Disk, is_this_a_disk, deduce_partno, \
    get_disk_record, delete_all_partitions, was_this_partition_created, \
    FS_EXTENDED, delete_partition
from test.test_partitiontools import SAMPLE_LIST_OF_BOGUS_PARAMS, \
    SAMPLE_LIST_OF_DRIVES_STUBS, SAMPLE_LIST_OF_DODGY_STUBS


class TestAAADiskClassCreation(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        disk = Disk(MY_TESTDISK_NODE)
        for _ in range(3):
            disk.delete_all_partitions()


class TestDeleteAllPartitions(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition()


class TestCreate12123(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1, size_in_MiB=100)
        self.disk.add_partition(partno=2, size_in_MiB=100)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=1, size_in_MiB=100)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=2, size_in_MiB=100)
        self.disk.add_partition(partno=3, size_in_MiB=100)


class TestCreateFullThenAddOne(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=2, size_in_MiB=100)


class TestCreateDeliberatelyOverlappingPartitions(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1, start=50000, end=99999)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=2,
                                    start=0,
                                    end=self.disk.partitions[-1].start)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=2,
                                    start=self.disk.partitions[-1].start,
                                    end=self.disk.partitions[-1].end)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=2,
                                    start=self.disk.partitions[-1].end,
                                    end=self.disk.partitions[-1].end + 99999)
        self.disk.add_partition(partno=2,
                                    start=self.disk.partitions[-1].end + 1,
                                    end=self.disk.partitions[-1].end + 99999)
        was_this_partition_created(self.disk.node, 2)


class TestMakeFourAndFiddleWithP2(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition()
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(len(self.disk.partitions), 1)
        self.disk.delete_partition(1)
        self.disk.add_partition(start=100000, end=199999)
        self.disk.add_partition(start=200000, end=299999)
        self.disk.add_partition(start=300000, end=399999)
        self.disk.add_partition(start=400000, end=499999)
        self.disk.delete_partition(2)
        self.assertEqual(self.disk.partitions[2].partno, 4)
        self.assertEqual(len(self.disk.partitions), 3)
        with self.assertRaises(AttributeError):
            self.disk.add_partition()
        self.disk.add_partition(2)
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(self.disk.partitions[1].partno, 2)
        self.assertEqual(self.disk.partitions[2].partno, 3)
        self.assertEqual(self.disk.partitions[3].partno, 4)
        self.disk.delete_partition(2)
        self.disk.add_partition(2, fstype=FS_EXTENDED)
        self.disk.delete_partition(2)
        self.disk.add_partition(2, fstype=FS_EXTENDED, size_in_MiB=128)
        self.disk.delete_partition(2)
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(self.disk.partitions[1].partno, 3)
        self.assertEqual(self.disk.partitions[2].partno, 4)
        with self.assertRaises(AttributeError):
            self.disk.add_partition(2, fstype=FS_EXTENDED, end=299999, size_in_MiB=256)


class TestLogicalPartitions_ONE(unittest.TestCase):

    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk = Disk(MY_TESTDISK_NODE)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        with self.assertRaises(AttributeError):
            self.disk.add_partition()
        self.disk.delete_partition(4)
        self.disk.add_partition(fstype=FS_EXTENDED)
        self.disk.add_partition(5, size_in_MiB=256)
        self.assertTrue(was_this_partition_created(self.disk.node, 5))
        self.disk.delete_partition(5)
        self.assertFalse(was_this_partition_created(self.disk.node, 5))
        self.disk.add_partition(5, size_in_MiB=256)
        self.assertTrue(was_this_partition_created(self.disk.node, 5))
        self.assertTrue(self.disk.partitions[2].partno == 3)
        old_p3_start = self.disk.partitions[2].start
        self.disk.delete_partition(3)
        self.assertFalse(was_this_partition_created(self.disk.node, 3))
        self.assertTrue(was_this_partition_created(self.disk.node, 5))
        self.disk.add_partition(3, old_p3_start)
        self.assertTrue(self.disk.partitions[2].partno == 3)
        self.disk.delete_partition(3)
        self.assertFalse(was_this_partition_created(self.disk.node, 3))
        self.disk.add_partition(3)
        self.assertTrue(self.disk.partitions[2].partno == 3)
        self.assertEqual(self.disk.partitions[2].start, old_p3_start)

'''
from my.partitiontools import *
d = Disk('/dev/sda')
d.delete_all_partitions()
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(fstype=FS_EXTENDED)
d.add_partition(partno=5, size_in_MiB=100)
d.add_partition(partno=6, size_in_MiB=100)
d.delete_partition(5)
was_this_partition_created(d.node, 5)
was_this_partition_created(d.node, 6)


'''


class TestLogicalPartitions_TWO(unittest.TestCase):

    def setUp(self):
        self.disk = Disk(MY_TESTDISK_NODE)
        self.assertTrue(is_this_a_disk(MY_TESTDISK_NODE))
        self.disk.delete_all_partitions()
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(fstype=FS_EXTENDED)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testMakeFive(self):
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.disk.add_partition(partno=5)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))

    def testMake5And6(self):
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.disk.add_partition(partno=5, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.disk.add_partition(partno=6, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=6))
        self.disk.delete_partition(partno=6)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.disk.delete_partition(partno=5)
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))

    def testMake5And7(self):
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=7))
        self.disk.add_partition(partno=5, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=7))
        with self.assertRaises(AttributeError):
            self.disk.add_partition(partno=7, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=6))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=7))
        self.disk.add_partition(partno=6, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=6))
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=7))
        self.disk.add_partition(partno=7, size_in_MiB=100)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=5))
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=6))
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=7))

    def testMake567AndTinkerWith2(self):
        for i in range(5, 7):
            self.assertFalse(was_this_partition_created(node=self.disk.node, partno=i))
            self.disk.add_partition(i, size_in_MiB=i * 10)
            self.assertTrue(was_this_partition_created(node=self.disk.node, partno=i))
        p2_partno = self.disk.partitions[1].partno
        p2_start = self.disk.partitions[1].start
        p2_end = self.disk.partitions[1].end
        self.assertEqual(p2_partno, 2)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=2))
        self.disk.delete_partition(2)
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=2))
        self.disk.add_partition(2)
        self.assertTrue(was_this_partition_created(node=self.disk.node, partno=2))
        self.assertEqual(self.disk.partitions[1].partno, 2)
        self.assertEqual(self.disk.partitions[1].start, p2_start)
        self.assertEqual(self.disk.partitions[1].end, p2_end)
        self.disk.delete_partition(2)
        self.assertFalse(was_this_partition_created(node=self.disk.node, partno=2))

    def testDeleteHighestLogical(self):
        self.disk.add_partition(5, size_in_MiB=100)
        self.disk.add_partition(6, size_in_MiB=100)
        with self.assertRaises(AttributeError):
            self.disk.delete_partition(5)
        self.assertTrue(was_this_partition_created(self.disk.node, 5))
        self.assertTrue(was_this_partition_created(self.disk.node, 6))

    def testDeleteNonhiestLogical(self):
        self.disk.add_partition(5, size_in_MiB=100)
        self.disk.add_partition(6, size_in_MiB=100)
        self.disk.delete_partition(6)
        self.assertTrue(was_this_partition_created(self.disk.node, 5))
        self.assertFalse(was_this_partition_created(self.disk.node, 6))

'''
self.disk.delete_partition(1)
assert(was_this_partition_created(self.disk.node, 1) == False)
self.disk.add_partition(1)
assert(was_this_partition_created(self.disk.node, 1) == True)
old_size_of_p12 = self.disk.partitions[12].size
self.disk.delete_partition(13)
new_size_of_p12 = self.disk.partitions[12].size

with open('/proc/partitions', 'r') as f:
    txt = f.read()



'''

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
