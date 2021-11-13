# -*- coding: utf-8 -*-
"""test_get_disk_record test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_get_disk_record
    $ python3 -m unittest test.test_disktools.test_get_disk_record.TestGetDiskRecord_TestFSTypeGetterAndSetter

"""
import os.path
import sys
from test import MY_TESTDISK_PATH
from my.globals import _DOS, _GPT
import unittest

from my.disktools.disks import is_this_a_disk, disk_namedtuple
from my.disktools.partitions import delete_all_partitions
from test.test_disktools import SAMPLE_LIST_OF_BOGUS_PARAMS


class TestGetDiskRecord_ZERO(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        for node in SAMPLE_LIST_OF_BOGUS_PARAMS:
            with self.assertRaises(ValueError, msg="%s" % node):
                _ = disk_namedtuple(node)


class TestGetDiskRecord_ONE(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        _ = disk_namedtuple(MY_TESTDISK_PATH)


class TestGetDiskRecord_TWO(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):
        r = disk_namedtuple(MY_TESTDISK_PATH)
        if r.partitiontable.myid not in (None, ""):
            self.assertTrue(is_this_a_disk(r.partitiontable.myid))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.myid)))
            self.assertEqual(
                os.path.realpath(r.partitiontable.myid),
                os.path.realpath(MY_TESTDISK_PATH),
            )
        if r.partitiontable.node not in (None, ""):
            self.assertTrue(is_this_a_disk(r.partitiontable.node))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.node)))
            self.assertEqual(
                os.path.realpath(r.partitiontable.node),
                os.path.realpath(MY_TESTDISK_PATH),
            )
        if r.partitiontable.device not in (None, ""):
            self.assertTrue(is_this_a_disk(r.partitiontable.device))
            self.assertTrue(is_this_a_disk(os.path.realpath(r.partitiontable.device)))
            self.assertEqual(
                os.path.realpath(r.partitiontable.device),
                os.path.realpath(MY_TESTDISK_PATH),
            )
        self.assertEqual(r.partitiontable.unit, "sectors")
        self.assertEqual(r.partitiontable.disklabel_type, "dos")
        self.assertEqual(
            0,
            os.system(
                """fdisk -l {fname} | grep "{serno}" >/dev/null""".format(
                    fname=MY_TESTDISK_PATH, serno=r.partitiontable.serno
                )
            ),
        )
        self.assertEqual(512, r.partitiontable.sector_size)
        self.assertTrue(
            r.partitiontable.size_in_sectors
            > 1024 * 1024 * 1024 // r.partitiontable.sector_size
        )
        self.assertEqual([], r.partitiontable.partitions)


class TestGetDiskRecord_TestFSTypeGetterAndSetter(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testGetter(self):
        from my.disktools.disks import Disk
        from my.disktools.partitions import get_partition_fstype

        d = Disk(MY_TESTDISK_PATH, _DOS)
        for fstype in ("83", "81", "83", "82", "80", "82", "83"):
            d.add_partition(partno=1, start=5555, end=9999, fstype=fstype)
            self.assertEqual(
                get_partition_fstype(d.node, d.partitions[0].partno), fstype
            )
            self.assertEqual(d.partitions[0].fstype, fstype)
            d.delete_partition(partno=1)

    def testSetter(self):
        from my.disktools.disks import Disk
        from my.disktools.partitions import get_partition_fstype, set_partition_fstype

        d = Disk(MY_TESTDISK_PATH, _DOS)
        for old_fstype in ("83", "5", "83", "82", "5", "82", "83"):
            for new_fstype in ("83", "5", "83", "82", "5", "82", "83"):
                d.add_partition(partno=1, start=5555, end=9999, fstype=old_fstype)
                self.assertEqual(
                    get_partition_fstype(d.node, d.partitions[0].partno), old_fstype
                )
                set_partition_fstype(d.node, d.partitions[0].partno, new_fstype)
                self.assertEqual(
                    get_partition_fstype(d.node, d.partitions[0].partno), new_fstype
                )
                if old_fstype != new_fstype:
                    self.assertEqual(d.partitions[0].fstype, old_fstype)
                d.partitions[0].update()
                self.assertEqual(d.partitions[0].fstype, new_fstype)
                d.delete_partition(partno=1)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
