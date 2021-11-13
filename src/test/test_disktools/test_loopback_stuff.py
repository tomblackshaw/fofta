"""
Created on Nov 9, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_loopback_stuff
    $ python3 -m unittest test.test_disktools.test_loopback_stuff.TestDiskImageLoopdev.testNewPartitionTableGoofy

"""
import os
import random
import sys
from test import MY_TESTDISK_PATH
import unittest
# from my.disktools.partitions import (
#     partition_exists,
#     add_partition,
#     delete_all_partitions,
#     delete_partition,
#     overlapping,
# )
from my.exceptions import PartitionTableCannotReadError,\
    MissingPriorPartitionError, PartitionDeletionError
from my.globals import call_binary
from my.disktools.disks import Disk, is_this_a_disk
from my.disktools.partitions import delete_all_partitions, _FS_EXTENDED,\
    partition_exists


class TestSample(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        delete_all_partitions(MY_TESTDISK_PATH)


MY_DISK_IMGSIZE_IN_MB = 500
MY_DISK_LOOPDEV  = '/dev/loop5'
MY_DISK_IMGFILE = '/tmp/.fofta.temp.image.file'

'''
MY_DISK_IMGSIZE_IN_MB = 500
MY_DISK_LOOPDEV  = '/dev/loop5'
MY_DISK_IMGFILE = '/tmp/.fofta.temp.image.file'
from my.disktools.disks import *
from my.disktools.partitions import *
from my.globals import *
if int(call_binary(['df','-m','/tmp'])[1].split('\n')[1].split('tmpfs')[1].strip(' ').split(' ')[0]) < MY_DISK_IMGSIZE_IN_MB:
    MY_DISK_IMGFILE = MY_DISK_IMGFILE.replace('/tmp/','/root/')

retcode, stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                               'count=%d'%MY_DISK_IMGSIZE_IN_MB])
retcode, stdout_txt, stderr_txt = call_binary(['losetup', '-d', MY_DISK_LOOPDEV])
retcode, stdout_txt, stderr_txt = call_binary(['losetup', MY_DISK_LOOPDEV, MY_DISK_IMGFILE])
os.system("partprobe %s" % MY_DISK_LOOPDEV)
d = Disk(MY_DISK_LOOPDEV, new_partition_table='dos')
d.add_partition()
adp = all_disk_paths()
nt = partition_namedtuple(d.node)
p = DiskPartition(d.node, 1)





MY_DISK_IMGSIZE_IN_MB = 500
MY_DISK_LOOPDEV  = '/dev/loop5'
MY_DISK_IMGFILE = '/tmp/.fofta.temp.image.file'
from my.disktools.disks import *
from my.disktools.partitions import *
from my.globals import *
if int(call_binary(['df','-m','/tmp'])[1].split('\n')[1].split('tmpfs')[1].strip(' ').split(' ')[0]) < MY_DISK_IMGSIZE_IN_MB:
    MY_DISK_IMGFILE = MY_DISK_IMGFILE.replace('/tmp/','/root/')

retcode, stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                               'count=%d'%MY_DISK_IMGSIZE_IN_MB])

d = Disk(MY_DISK_IMGFILE, new_partition_table='dos')
d.add_partition()
d.delete_partition(partno=1)

adp = all_disk_paths()
nt = partition_namedtuple(d.node)
devdiskbyxxxx_path
node = '/tmp/.fofta.temp.image.file1'


'''


class TestDiskImageLoopdev(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     os.environ['PATH'] = os.environ['PATH']+':'+os.getenv('PATH')
    #     import pydevd; pydevd.settrace("192.168.0.139", port=5678, stdoutToServer=True, stderrToServer=True)
        
    def setUp(self):
        retcode, _stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                                       'count=%d'%MY_DISK_IMGSIZE_IN_MB])
        self.assertEqual(retcode,0, "Failed to create sample loopdev disk image\n"+stderr_txt)
        retcode, _stdout_txt, _stderr_txt = call_binary(['losetup', '-d', MY_DISK_LOOPDEV])
        retcode, _stdout_txt, stderr_txt = call_binary(['losetup', MY_DISK_LOOPDEV, MY_DISK_IMGFILE])
        self.assertEqual(retcode,0, "Failed to losetup the disk image\n"+stderr_txt)
        os.system("sync;sync;sync;partprobe;sync;sync;sync")
        with self.assertRaises(PartitionTableCannotReadError):
            _d = Disk(MY_DISK_IMGFILE)

    def tearDown(self):
        call_binary(['umount', MY_DISK_LOOPDEV])
        call_binary(['losetup', '-d', MY_DISK_LOOPDEV])
        call_binary(['rm', '-f', MY_DISK_IMGFILE])
        
    def testIsADisk(self):
        _d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='dos')
        self.assertTrue(is_this_a_disk(MY_DISK_LOOPDEV))
        call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                                       'count=4'])
        self.assertFalse(is_this_a_disk(MY_DISK_LOOPDEV))
        call_binary(['umount', MY_DISK_LOOPDEV])
        call_binary(['losetup', '-d', MY_DISK_LOOPDEV])
        self.assertFalse(is_this_a_disk(MY_DISK_LOOPDEV))
            
    def testNewPartitionTableGoofy(self):
        with self.assertRaises(ValueError):
            _d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='flurble')
        with self.assertRaises(ValueError):
            _d = Disk(node=MY_DISK_LOOPDEV, new_partition_table=1234)
        with self.assertRaises(ValueError):
            _d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='blah')
        with self.assertRaises(ValueError):
            _d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='')

    def testShouldNotCreateDiskInstanceWithoutPartitionTable(self):
        with self.assertRaises(PartitionTableCannotReadError):
            _d = Disk(node=MY_DISK_LOOPDEV)

    def testNewPartitionTableSensibleGPT(self):
        d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='gpt')
        self.assertEqual(d.disklabel_type, 'gpt')

    def testNewPartitionTableSensibleDOS(self):
        d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='dos')
        self.assertEqual(d.disklabel_type, 'dos')

    def testCreateSimpleDiskPartitionTableRandoms(self):
        for _ in range(0,16):
            dltype = ('gpt','dos')[random.randint(0,1)]
            d = Disk(node=MY_DISK_LOOPDEV, new_partition_table=dltype)
            self.assertEqual(d.disklabel_type, dltype)

    def testAddPartitionAndRemoveItAgain(self):
        d = Disk(node=MY_DISK_LOOPDEV, new_partition_table='dos')
        d.add_partition()
        d.delete_partition(1)
        

class TestDiskActualImage(unittest.TestCase):
    def setUp(self):
        retcode, _stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                                       'count=%d'%MY_DISK_IMGSIZE_IN_MB])
        self.assertEqual(retcode,0, "Failed to create sample loopdev disk image\n"+stderr_txt)
        os.system("sync;sync;sync;partprobe;sync;sync;sync")

    def tearDown(self):
        call_binary(['rm', '-f', MY_DISK_IMGFILE])

    def testIsADIsk(self):
        self.assertFalse(is_this_a_disk(MY_DISK_IMGFILE))
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        self.assertTrue(is_this_a_disk(MY_DISK_IMGFILE))
        self.assertEqual(d.partitions, [])
        call_binary(['rm', '-f', MY_DISK_IMGFILE])
        with self.assertRaises(ValueError):
            _ = is_this_a_disk(MY_DISK_IMGFILE)


    def testNewPartyGoof(self):
        for goofy_table_type in ('blah', 'flibble', 1234, ''):
            with self.assertRaises(PartitionTableCannotReadError):
                _d = Disk(node=MY_DISK_IMGFILE)
            with self.assertRaises(ValueError):
                _d = Disk(node=MY_DISK_IMGFILE, new_partition_table=goofy_table_type)
    
    def testCreateSimpleDiskPartitionTableRandoms(self):
        for _ in range(0,16):
            dltype = ('gpt','dos')[random.randint(0,1)]
            d = Disk(node=MY_DISK_IMGFILE, new_partition_table=dltype)
            self.assertEqual(d.disklabel_type, dltype)
                
    def testCreateAndDeleteImage(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition()
        d.delete_partition(partno=1)

    def testCnD_Two(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition()
        d.delete_partition(partno=1)

    def testMakeWibble(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.delete_all_partitions()

    def testMakeSquibble(self):
        '''
MY_DISK_IMGSIZE_IN_MB = 160
MY_DISK_LOOPDEV  = '/dev/loop5'
MY_DISK_IMGFILE = '/tmp/.fofta.temp.image.file'
from my.disktools.disks import *
from my.disktools.partitions import *
from my.globals import *
if int(call_binary(['df','-m','/tmp'])[1].split('\n')[1].split('tmpfs')[1].strip(' ').split(' ')[0]) < MY_DISK_IMGSIZE_IN_MB:
    MY_DISK_IMGFILE = MY_DISK_IMGFILE.replace('/tmp/','/root/')

retcode, stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                               'count=%d'%MY_DISK_IMGSIZE_IN_MB])
        
d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(size_in_MiB=1024)
d.add_partition(fstype=_FS_EXTENDED)
d.delete_all_partitions()
        '''
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        d.delete_all_partitions()

    def testMakeGerbil(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)

    def testMakeFive(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        d.add_partition(partno=5)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))

    def testMake5And6(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        d.add_partition(partno=5, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        d.add_partition(partno=6, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        d.delete_partition(partno=6)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        d.delete_partition(partno=5)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))

    def testMake5And7(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(partno=5, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        with self.assertRaises(MissingPriorPartitionError):
            d.add_partition(partno=7, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(partno=6, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(partno=7, size_in_MiB=32)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        self.assertTrue(partition_exists(disk_path=d.node, partno=7))

    def testMake56765(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(5, size_in_MiB=50)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(6, size_in_MiB=30)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(7, size_in_MiB=40)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        self.assertTrue(partition_exists(disk_path=d.node, partno=7))
        d.delete_partition(7)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.delete_partition(6)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.delete_partition(5)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))


    def testMake567AndTinkerWith2(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        self.assertFalse(partition_exists(disk_path=d.node, partno=5))
        self.assertFalse(partition_exists(disk_path=d.node, partno=6))
        self.assertFalse(partition_exists(disk_path=d.node, partno=7))
        d.add_partition(5, size_in_MiB=50)
        self.assertTrue(partition_exists(disk_path=d.node, partno=5))
        d.add_partition(6, size_in_MiB=40)
        self.assertTrue(partition_exists(disk_path=d.node, partno=6))
        d.add_partition(7, size_in_MiB=30)
        self.assertTrue(partition_exists(disk_path=d.node, partno=7))
        p2_partno = d.partitions[1].partno
        p2_start = d.partitions[1].start
        p2_end = d.partitions[1].end
        self.assertEqual(p2_partno, 2)
        self.assertTrue(partition_exists(disk_path=d.node, partno=2))
        d.delete_partition(2)
        self.assertFalse(partition_exists(disk_path=d.node, partno=2))
        d.add_partition(2)
        self.assertTrue(partition_exists(disk_path=d.node, partno=2))
        self.assertEqual(d.partitions[1].partno, 2)
        self.assertEqual(d.partitions[1].start, p2_start)
        self.assertEqual(d.partitions[1].end, p2_end)
        d.delete_partition(2)
        self.assertFalse(partition_exists(disk_path=d.node, partno=2))

    def testDeleteHighestLogical(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        d.add_partition(5, size_in_MiB=32)
        d.add_partition(6, size_in_MiB=32)
        with self.assertRaises(PartitionDeletionError):
            d.delete_partition(5)
        self.assertTrue(partition_exists(d.node, 5))
        self.assertTrue(partition_exists(d.node, 6))

    def testDeleteNonhighestLogical(self):
        d = Disk(node=MY_DISK_IMGFILE, new_partition_table='dos')
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(size_in_MiB=32)
        d.add_partition(fstype=_FS_EXTENDED)
        d.add_partition(5, size_in_MiB=32)
        d.add_partition(6, size_in_MiB=32)
        d.delete_partition(6)
        self.assertTrue(partition_exists(d.node, 5))
        self.assertFalse(partition_exists(d.node, 6))

'''DOES ADDING P(n+1) DELETE ANYTHING FROM P(n)'S FILESYSTEM??'''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
