'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import os
import sys
from test import MY_TESTDISK_NODE
import unittest

from my.partitiontools import *
from my.partitiontools import is_this_a_disk, deduce_partno, \
    delete_all_partitions, add_partition, was_this_partition_created, \
    delete_partition


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

    def testMakeAndDelWithoutExtraProbe(self):
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

'''
from my.partitiontools import *
from test import MY_TESTDISK_NODE

d.add_partition(partno=1, start=50000, end=99999)
try:
    d.add_partition(start=0, end=d.partitions[-1].start)
    raise SystemError("That should have failed.")
except AttributeError:
    pass

d.delete_all_partitions()
d.add_partition()
assert(d.partitions[0].partno == 1)
d.delete_partition(1)
d.add_partition(start=100000, end=199999)
d.add_partition(start=200000, end=299999)
d.add_partition(start=300000, end=399999)
d.add_partition(start=400000, end=499999)
d.delete_partition(2)
try:
    d.add_partition()  # #5
    raise SystemError("That should have failed.")
except AttributeError:
    pass
d.add_partition(2)
d.delete_partition(2)
d.add_partition(2, fstype=FS_EXTENDED)
d.delete_partition(2)
d.add_partition(2, fstype=FS_EXTENDED, size_in_MiB=16)
d.delete_partition(2)
try:
    d.add_partition(2, fstype=FS_EXTENDED, end=299999, size_in_MiB=16)
    raise SystemError("That should have failed.")
except AttributeError:
    pass

d.add_partition(2, fstype=FS_EXTENDED)
d.delete_all_partitions()

d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.delete_partition(2)
d.add_partition(2, fstype=FS_EXTENDED)
d.delete_partition(3)
d.delete_partition(4)
d.delete_partition(2)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(fstype=FS_EXTENDED)
d.add_partition(5, size_in_MiB=100)

d = Disk('/dev/disk/by-id/usb-Mass_Storage_Device_121220160204-0:0')  # d = Disk('/dev/sda')
d.delete_all_partitions()
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(fstype=FS_EXTENDED)
for i in range(5, 15):
    print("%d..." % i)
    d.add_partition(i, size_in_MiB=i * 10)

d.delete_partition(1)
assert(was_this_partition_created(d.node, 1) == False)
d.add_partition(1)
assert(was_this_partition_created(d.node, 1) == True)
old_size_of_p12 = d.partitions[12].size
d.delete_partition(13)
new_size_of_p12 = d.partitions[12].size

with open('/proc/partitions', 'r') as f:
    txt = f.read()

'''

# class TestImportOnly(unittest.TestCase):
#
#     def setUp(self):
#         from my.partitiontools import Disk, DiskPartition
#         pass
#
#     def tearDown(self):
#         pass
#
#     def testName(self):
#         pass
#
#
# class TestDeleteCrashability(unittest.TestCase):
#
#     def setUp(self):
#         from my.partitiontools import Disk, DiskPartition
#         d = Disk()
#
#     def tearDown(self):
#         pass
#
#     def testName(self):
#         pass
#
#
# class TestIsThisADisk(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#     def testAbilityToRejectBadParams(self):
#
#         with self.assertRaises(FileNotFoundError):
#             _ = is_this_a_disk('/blah/blah')
#         with self.assertRaises(FileNotFoundError):
#             _ = is_this_a_disk('/dev/foobar1234321')
#         with self.assertRaises(FileNotFoundError):
#             _ = is_this_a_disk('/')
#         with self.assertRaises(FileNotFoundError):
#             _ = is_this_a_disk('')
#         with self.assertRaises(FileNotFoundError):
#             _ = is_this_a_disk(None)
#
#     def testAbilityToNoticeDisks(self):
#         for stub in ('sda', 'sdb', 'sdp', 'mmcblk0', 'mmcblk1', 'mmcblk10'):
#             node = '/dev/%s' % (stub)
#             self.assertTrue(is_this_a_disk(node), "%s *is* a disk, actually" % node)
#
#     def testAbilityToNoticeNotdisks(self):
#         for stub in ('sda', 'sdb', 'sdp', 'mmcblk0p', 'mmcblk1p', 'mmcblk10p'):
#             for i in range(1, 101):
#                 node = '/dev/%s%d' % (stub, i)
#             self.assertFalse(is_this_a_disk(node), "%s *isn't* a disk, actually" % node)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
