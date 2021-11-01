# -*- coding: utf-8 -*-
"""test_Disk_class test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_Disk_class
    $ python3 -m unittest test.test_disktools.test_Disk_class.TestLogicalPartitions_TWO.testMake567AndTinkerWith2

"""
import os
import sys
from test import MY_TESTDISK_PATH
import unittest

from my.disktools.disks import Disk, is_this_a_disk, set_disk_id
from my.disktools.partitions import partition_exists, _FS_EXTENDED
from my.exceptions import (
    StartEndAssBackwardsError,
    MissingPriorPartitionError,
    PartitionWasNotCreatedError,
    DiskIDSettingFailureError,
    PartitionDeletionError,
    PartitionsOverlapError,
    WeNeedAnExtendedPartitionError,
)
from my.globals import call_binary


class TestAAADiskClassCreation(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        disk = Disk(MY_TESTDISK_PATH)
        for _ in range(3):
            disk.delete_all_partitions()


class TestDeleteAllPartitions(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition()


class TestCreate12123(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1, size_in_MiB=100)
        self.disk.add_partition(partno=2, size_in_MiB=100)
        with self.assertRaises(ValueError):
            self.disk.add_partition(partno=1, size_in_MiB=100)
        with self.assertRaises(ValueError):
            self.disk.add_partition(partno=2, size_in_MiB=100)
        self.disk.add_partition(partno=3, size_in_MiB=100)


class TestCreateFullThenAddOne(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1)
        with self.assertRaises(PartitionWasNotCreatedError):
            self.disk.add_partition(partno=2, size_in_MiB=100)


class TestCreateDeliberatelyOverlappingPartitions(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(partno=1, start=50000, end=99999)
        self.assertEqual(len(self.disk.partitions), 1)
        with self.assertRaises(StartEndAssBackwardsError):
            self.disk.add_partition(
                partno=2, start=None, end=self.disk.partitions[-1].start
            )
        self.assertEqual(len(self.disk.partitions), 1)
        with self.assertRaises(PartitionsOverlapError):
            self.disk.add_partition(
                partno=2,
                start=self.disk.partitions[-1].start,
                end=self.disk.partitions[-1].end,
            )
        self.assertEqual(len(self.disk.partitions), 1)
        with self.assertRaises(PartitionsOverlapError):
            self.disk.add_partition(
                partno=2,
                start=self.disk.partitions[-1].end,
                end=self.disk.partitions[-1].end + 99999,
            )
        self.assertEqual(len(self.disk.partitions), 1)
        self.disk.add_partition(
            partno=2,
            start=self.disk.partitions[-1].end + 1,
            end=self.disk.partitions[-1].end + 99999,
        )
        partition_exists(self.disk.node, 2)
        self.assertEqual(len(self.disk.partitions), 2)


class TestMakeFourAndFiddleWithP2(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition()
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(len(self.disk.partitions), 1)
        self.disk.delete_partition(1)
        with self.assertRaises(StartEndAssBackwardsError):
            self.disk.add_partition(start=199999, end=100000)
        self.disk.add_partition(start=100000, end=199999)
        self.disk.add_partition(start=200000, end=299999)
        self.disk.add_partition(start=300000, end=399999)
        self.disk.add_partition(start=400000, end=499999)
        self.disk.delete_partition(2)
        self.assertEqual(self.disk.partitions[2].partno, 4)
        self.assertEqual(len(self.disk.partitions), 3)
        with self.assertRaises(WeNeedAnExtendedPartitionError):
            self.disk.add_partition()
        self.disk.add_partition(2)
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(self.disk.partitions[1].partno, 2)
        self.assertEqual(self.disk.partitions[2].partno, 3)
        self.assertEqual(self.disk.partitions[3].partno, 4)
        self.disk.delete_partition(2)
        self.disk.add_partition(2, fstype=_FS_EXTENDED)
        self.disk.delete_partition(2)
        self.disk.add_partition(2, fstype=_FS_EXTENDED, size_in_MiB=128)
        self.disk.delete_partition(2)
        self.assertEqual(self.disk.partitions[0].partno, 1)
        self.assertEqual(self.disk.partitions[1].partno, 3)
        self.assertEqual(self.disk.partitions[2].partno, 4)
        with self.assertRaises(ValueError):
            self.disk.add_partition(2, fstype=_FS_EXTENDED, end=299999, size_in_MiB=256)


class TestLogicalPartitions_ONE(unittest.TestCase):
    def setUp(self):
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk = Disk(MY_TESTDISK_PATH)
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        with self.assertRaises(WeNeedAnExtendedPartitionError):
            self.disk.add_partition()
        self.disk.delete_partition(4)
        self.disk.add_partition(fstype=_FS_EXTENDED)
        self.disk.add_partition(5, size_in_MiB=256)
        self.assertTrue(partition_exists(self.disk.node, 5))
        self.disk.delete_partition(5)
        self.assertFalse(partition_exists(self.disk.node, 5))
        self.disk.add_partition(5, size_in_MiB=256)
        self.assertTrue(partition_exists(self.disk.node, 5))
        self.assertTrue(self.disk.partitions[2].partno == 3)
        old_p3_start = self.disk.partitions[2].start
        self.disk.delete_partition(3)
        self.assertFalse(partition_exists(self.disk.node, 3))
        self.assertTrue(partition_exists(self.disk.node, 5))
        self.disk.add_partition(3, old_p3_start)
        self.assertTrue(self.disk.partitions[2].partno == 3)
        self.disk.delete_partition(3)
        self.assertFalse(partition_exists(self.disk.node, 3))
        self.disk.add_partition(3)
        self.assertTrue(self.disk.partitions[2].partno == 3)
        self.assertEqual(self.disk.partitions[2].start, old_p3_start)


class TestSettingDiskID(unittest.TestCase):
    def setUp(self):
        self.disk = Disk(MY_TESTDISK_PATH)
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk.delete_all_partitions()

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        for _ in range(5):
            retcode, stdout_txt, stderr_txt = call_binary(
                ["bash"],
                """printf "%08x" 0x$(dd if=/dev/urandom bs=1 count=200 2>/dev/null | tr -dc 'a-f0-9' | cut -c-8)""",
            )
            new_diskid = "0x{stdout_txt}".format(stdout_txt=stdout_txt)
            set_disk_id(self.disk.node, new_diskid)
            self.assertNotEqual(self.disk.disk_id, new_diskid)
            self.disk.update()
            self.assertEqual(self.disk.disk_id, new_diskid)
        del retcode, stdout_txt, stderr_txt
        for new_id in (
            None,
            "",
            "0x123456789",
            "0x",
            "0x1234567",
            "1234567890",
            "",
            "ABCDEFGHIJ",
            "0xABCDEFGH",
            "0xabdefgh",
            0x1234ABCD,
        ):
            with self.assertRaises(DiskIDSettingFailureError):
                set_disk_id(self.disk.node, new_id)


class TestLogicalPartitions_TWO(unittest.TestCase):
    def setUp(self):
        self.disk = Disk(MY_TESTDISK_PATH)
        self.assertTrue(is_this_a_disk(MY_TESTDISK_PATH))
        self.disk.delete_all_partitions()
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(size_in_MiB=1024)
        self.disk.add_partition(fstype=_FS_EXTENDED)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testMakeFive(self):
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.add_partition(partno=5)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))

    def testMake5And6(self):
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.add_partition(partno=5, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.add_partition(partno=6, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.delete_partition(partno=6)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.delete_partition(partno=5)
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))

    def testMake5And7(self):
        """
        from my.disktools.disks import *
        from my.disktools.partitions import partition_exists, _FS_EXTENDED
        d = Disk('/dev/sda')
        d.delete_all_partitions()
        d.add_partition(size_in_MiB=1024)
        d.add_partition(size_in_MiB=1024)
        d.add_partition(size_in_MiB=1024)
        d.add_partition(fstype=_FS_EXTENDED)
        assert(False is partition_exists(disk_path=d.node, partno=5))
        assert(False is partition_exists(disk_path=d.node, partno=6))
        assert(False is partition_exists(disk_path=d.node, partno=7))
        d.add_partition(partno=5, size_in_MiB=100)
        assert(True is partition_exists(disk_path=d.node, partno=5))
        assert(False is partition_exists(disk_path=d.node, partno=6))
        assert(False is partition_exists(disk_path=d.node, partno=7))
        d.add_partition(partno=7, size_in_MiB=100)
        """
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=7))
        self.disk.add_partition(partno=5, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=7))
        with self.assertRaises(MissingPriorPartitionError):
            self.disk.add_partition(partno=7, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=7))
        self.disk.add_partition(partno=6, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=7))
        self.disk.add_partition(partno=7, size_in_MiB=100)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=7))

    def testMake567AndTinkerWith2(self):
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=5))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=6))
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=7))
        self.disk.add_partition(5, size_in_MiB=500)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=5))
        self.disk.add_partition(6, size_in_MiB=600)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=6))
        self.disk.add_partition(7, size_in_MiB=700)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=7))
        p2_partno = self.disk.partitions[1].partno
        p2_start = self.disk.partitions[1].start
        p2_end = self.disk.partitions[1].end
        self.assertEqual(p2_partno, 2)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=2))
        self.disk.delete_partition(2)
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=2))
        self.disk.add_partition(2)
        self.assertTrue(partition_exists(disk_path=self.disk.node, partno=2))
        self.assertEqual(self.disk.partitions[1].partno, 2)
        self.assertEqual(self.disk.partitions[1].start, p2_start)
        self.assertEqual(self.disk.partitions[1].end, p2_end)
        self.disk.delete_partition(2)
        self.assertFalse(partition_exists(disk_path=self.disk.node, partno=2))

    def testDeleteHighestLogical(self):
        self.disk.add_partition(5, size_in_MiB=100)
        self.disk.add_partition(6, size_in_MiB=100)
        with self.assertRaises(PartitionDeletionError):
            self.disk.delete_partition(5)
        self.assertTrue(partition_exists(self.disk.node, 5))
        self.assertTrue(partition_exists(self.disk.node, 6))

    def testDeleteNonhiestLogical(self):
        self.disk.add_partition(5, size_in_MiB=100)
        self.disk.add_partition(6, size_in_MiB=100)
        self.disk.delete_partition(6)
        self.assertTrue(partition_exists(self.disk.node, 5))
        self.assertFalse(partition_exists(self.disk.node, 6))

    # def testSomeOtherBS(self):
    #     '''
    #     self.disk.delete_partition(1)
    #     assert(partition_exists(self.disk.node, 1) == False)
    #     self.disk.add_partition(1)
    #     assert(partition_exists(self.i, 1) == True)
    #     old_size_of_p12 = self.disk.partitions[12].size
    #     self.disk.delete_partition(13)
    #     new_size_of_p12 = self.disk.partitions[12].size
    #
    #     with open('/proc/partitions', 'r') as f:
    #         txt = f.read()
    #     '''
    #     pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
