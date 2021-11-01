# -*- coding: utf-8 -*-
"""test_get_disk_record test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_subroutines
    $ python3 -m unittest test.test_disktools.test_subroutines.TestPartitionNamedtupleFunction.testPNode

"""
import os
import sys
import unittest
from my.disktools.disks import is_this_a_disk, Disk
from test.test_disktools import SAMPLE_LIST_OF_BOGUS_PARAMS, \
    SAMPLE_LIST_OF_DRIVES_STUBS, SAMPLE_LIST_OF_DODGY_STUBS
from test import MY_TESTDISK_PATH
from my.disktools.partitions import delete_all_partitions, add_partition, partition_namedtuple
import random


def make_disk_have_one_randomizerd_partitionom_partition(disk_path, partno):
    delete_all_partitions(MY_TESTDISK_PATH)
    start = random.randint(5555,9999)
    end = start + random.randint(1000,99999)
    fstype = str(random.randint(70,83))
    add_partition(disk_path=disk_path, partno=partno, start=start, end=end, fstype=fstype)
    from my.disktools.disks import Disk
    partition = Disk(disk_path).partitions[0]
    assert(partition.partno == partno)
    return (disk_path, start, end, fstype, partno, partition)

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


class TestPartitionNamedtupleFunction(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

#     def testStr(self):
#         (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
#         should_be_str = """"X(node={node}, start={start}, size={size}, type={fstype}, id={id}, \
# label={label}, partuuid={partuuid}, path={path}, uuid={uuid})""".format(node=disk_path, 
#                                                                         start=start,
#                                                                         size=end-start,
#                                                                         fstype=fstype,
#                                                                         id=partition.id,
#                                                                         label=partition.label,
#                                                                         partuuid=partition.uuid,
#                                                                         path=partition.path,
#                                                                         uuid=partition.uuid
#                                                                         )
#         but_is_str = str(partition_namedtuple(partition.node))
#         print("Should be", should_be_str)
#         print("...but is", but_is_str)
#         self.assertEqual(should_be_str, but_is_str)

    def testPNode(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertTrue(partition.node.startswith(MY_TESTDISK_PATH))
        self.assertTrue(partition.node.endswith(str(pno)))
        self.assertEqual(partition_namedtuple(partition.node).node, partition.node)

    def testPEnd(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(end, start + partition_namedtuple(partition.node).size - 1)
    
    def testPStart(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(start, partition_namedtuple(partition.node).start)

    def testPId(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.id, partition_namedtuple(partition.node).id)

    def testPUUID(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.uuid, partition_namedtuple(partition.node).uuid)

    def testPPartUUID(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.partuuid, partition_namedtuple(partition.node).partuuid)
        
    def testPLabel(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.label, partition_namedtuple(partition.node).label)

    def testPPath(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.path, partition_namedtuple(partition.node).path)

    def testPType(self):
        (disk_path, start, end, fstype, pno, partition) = make_disk_have_one_randomizerd_partitionom_partition(MY_TESTDISK_PATH, 1)
        self.assertEqual(partition.fstype, partition_namedtuple(partition.node).type)




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
