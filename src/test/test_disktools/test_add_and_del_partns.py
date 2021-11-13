"""
Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_add_and_del_partns
    $ python3 -m unittest test.test_disktools.test_add_and_del_partns.TestOverlappingSubroutine.testName

"""
import os
import random
import sys
from test import MY_TESTDISK_PATH
from my.globals import _DOS, _GPT
import unittest
from my.disktools.partitions import (
    partition_exists,
    add_partition,
    delete_all_partitions,
    delete_partition,
    overlapping,
)
from my.exceptions import PartitionWasNotCreatedError
from my.globals import call_binary


class TestSoloDeleteAll(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        delete_all_partitions(MY_TESTDISK_PATH)


class TestSimpleAddAndAllDel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        add_partition(
            disk_path=MY_TESTDISK_PATH, partno=1, start=2048, end=999999, fstype="83"
        )  # , debug, size_in_MiB)
        realnode = os.path.realpath(MY_TESTDISK_PATH)
        self.assertTrue(partition_exists(realnode, 1))
        delete_all_partitions(MY_TESTDISK_PATH)


class TestSimpleAddAndIndividualDel(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):
        realnode = os.path.realpath(MY_TESTDISK_PATH)
        for _ in range(3):
            self.assertFalse(partition_exists(realnode, 1))
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, 1))
            add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=1,
                start=2048,
                end=999999,
                fstype="83",
            )  # , debug, size_in_MiB)
            self.assertTrue(partition_exists(realnode, 1))
            self.assertTrue(partition_exists(MY_TESTDISK_PATH, 1))
            delete_partition(MY_TESTDISK_PATH, 1)
            self.assertFalse(partition_exists(realnode, 1))
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, 1))


class TestAnMBAddAndIndividualDel(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):
        realnode = os.path.realpath(MY_TESTDISK_PATH)
        for _ in range(3):
            self.assertFalse(partition_exists(realnode, 1))
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, 1))
            add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=1,
                start=2048,
                size_in_MiB=1000,
                fstype="83",
            )
            self.assertTrue(partition_exists(realnode, 1))
            self.assertTrue(partition_exists(MY_TESTDISK_PATH, 1))
            delete_partition(MY_TESTDISK_PATH, 1)
            self.assertFalse(partition_exists(realnode, 1))
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, 1))


class TestOverlappingSubroutine(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)
        from my.disktools.disks import Disk
        self.disk = Disk(MY_TESTDISK_PATH, _DOS)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testRidiculouslySmallPartition(self):
        with self.assertRaises(PartitionWasNotCreatedError):
            # too small (>=2048 needed)
            self.disk.add_partition(partno=1, start=500, end=999)

    def testName(self):
        """
        from my.disktools.disks import Disk
        from my.disktools.partitions import add_partition, add_partition_SUB, overlapping
        d = Disk('/dev/sda', _DOS)
        d.delete_all_partitions()
        d.add_partition(partno=1, start=5000, end=9990)
        d.add_partition(partno=2, start=10000, end=14990)
        overlapping(d.node, [1, 5000, 9990, '83'])
        """
        self.disk.add_partition(partno=1, start=5000, end=9990)
        self.disk.add_partition(partno=2, start=10000, end=14990)
        self.assertFalse(overlapping(self.disk.node))
        self.assertTrue(overlapping(self.disk.node, [1, 5000, 9990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [2, 10000, 14990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [2, 5000, 9990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [1, 10000, 14990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [1, 5000, 9990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [2, 10000, 14990, "83"]))

        self.assertFalse(overlapping(self.disk.node, [3, 15000, 15990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [3, 4900, 5000, "83"]))
        self.assertFalse(overlapping(self.disk.node, [3, 4900, 4990, "83"]))
        self.assertFalse(overlapping(self.disk.node, [3, None, 4990, "83"]))
        self.assertTrue(overlapping(self.disk.node, [3, 14990, 20000, "83"]))
        self.assertFalse(overlapping(self.disk.node, [3, 15000, 20000, "83"]))
        self.assertFalse(overlapping(self.disk.node, [3, None, None, "83"]))
        self.assertFalse(overlapping(self.disk.node, [3, 15000, None, "83"]))


class TestCreateAndDeleteFourPartitions(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testPartprobeNecessity(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            wozzit_A = partition_exists(MY_TESTDISK_PATH, partno)
            call_binary(['partprobe']); call_binary(['sync'])
            wozzit_B = partition_exists(MY_TESTDISK_PATH, partno)
            self.assertTrue(wozzit_B)
            self.assertTrue(wozzit_A)
            self.assertEqual(res, 0)

    def testMakeAndDelWithXtraProbe(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            os.system("sync;sync;sync; partprobe; sync;sync;sync")
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithProbeButNoSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, partition_exists(MY_TESTDISK_PATH, partno))
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            os.system("partprobe")
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithPartialProbeAndNoSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, partition_exists(MY_TESTDISK_PATH, partno))
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            os.system("partprobe {node}".format(node=MY_TESTDISK_PATH))
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithSyncButNoProbe(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            self.assertEqual(False, partition_exists(MY_TESTDISK_PATH, partno))
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            os.system("sync;sync;sync")
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)

    def testMakeAndDelWithoutProbeOrSync(self):
        size_in_sectors = 1000000
        for partno in range(1, 5):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)


class TestCreate123Delete2Remake2(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):
        size_in_sectors = 1000000
        starts = {}
        for partno in range(1, 3):
            self.assertFalse(partition_exists(MY_TESTDISK_PATH, partno))
            start = 2048 if partno == 1 else size_in_sectors * (partno - 1)
            end = size_in_sectors * partno - 1
            res = add_partition(
                disk_path=MY_TESTDISK_PATH,
                partno=partno,
                start=start,
                end=end,
                fstype="83",
            )  # , debug, size_in_MiB)
            self.assertEqual(True, partition_exists(MY_TESTDISK_PATH, partno))
            self.assertEqual(res, 0)
            starts[str(partno)] = start
        delete_partition(MY_TESTDISK_PATH, 2)
        add_partition(MY_TESTDISK_PATH, 2, start=starts["2"])


def compare_devdiskbyxxxx_path_what_should_be_with_what_is(partition):
    from my.disktools.both import devdiskbyxxxx_path

    mismatches = 0
    for searchby in ("myid", "uuid", "partuuid", "label", "path"):
        should_be = devdiskbyxxxx_path(partition.node, searchby.replace('my',''))
        but_is = getattr(partition, searchby)
        if should_be != but_is:
            print(
                "{node}.{searchby} should read {should_be} but actually is {but_is}".format(
                    node=partition.node,
                    searchby=searchby,
                    should_be=should_be,
                    but_is=but_is,
                )
            )
            mismatches += 1
    return mismatches


class TestCreateAndDeleteFivePartitions(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testName(self):
        pass # TODO: WRITE THIS!


class TestLabelAndIDThing(unittest.TestCase):
    def setUp(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def tearDown(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testDevdiskbyxxxx_path_ONE(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "(yes y 2> /dev/null)| mkfs.ext4 -L {label} {node} > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )

    def testDevdiskbyxxxx_path_TWO(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "(yes y 2> /dev/null) | mkfs.ext4 -L {label} {node} > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )

    def testNameExt4_halfassed_update(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "(yes y 2> /dev/null)| mkfs.ext4 -L {label} {node}  > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        # ...because we have to update all of d()
        self.assertEqual(d.partitions[-1].label, "/dev/disk/by-label/%s" % my_label)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )  # ...because we have to update all of d()

    def testNameExt4_full_update(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "(yes y 2> /dev/null)| mkfs.ext4 -L {label} {node}  > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        self.assertEqual(d.partitions[-1].label, "/dev/disk/by-label/%s" % my_label)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )

    def testNameBtrfs(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "mkfs.btrfs -L {label} -f {node} > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        self.assertEqual(d.partitions[-1].label, "/dev/disk/by-label/%s" % my_label)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )

    def testNameBtrfsFLAWEDwithoutpartprobe(self):
        from my.disktools.disks import Disk

        d = Disk(MY_TESTDISK_PATH, _DOS)
        d.add_partition(fstype="83", size_in_MiB=300)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )
        my_label = "MY_LAB%d" % random.randint(0, 100)
        os.system(
            "mkfs.btrfs -L {label} -f {node} > /dev/null 2> /dev/null".format(
                label=my_label, node=d.partitions[-1].node
            )
        )
        d.update()
        # That's why this is NotEqual!
        self.assertEqual(d.partitions[-1].label, "/dev/disk/by-label/%s" % my_label)
        self.assertEqual(
            0, compare_devdiskbyxxxx_path_what_should_be_with_what_is(d.partitions[0])
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
