"""
Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_gpt_parts.TestPartitionCreation.testMakeAndDeleteRandomly

"""
import os
import random
import sys
from test import MY_TESTDISK_PATH
import unittest
from my.disktools.partitions import (
    partition_exists,
    add_partition,
    delete_all_partitions,
    delete_partition,
    overlapping,
    add_partition
)
from my.exceptions import PartitionWasNotCreatedError
from my.globals import call_binary, _GPT, _DOS
from my.disktools.disks import Disk


class TestSimpleMakeAndWipe(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBatchDel(self):
        delete_all_partitions(MY_TESTDISK_PATH)

    def testMakeAndBatchDel(self):
        for _ in range(0,2): 
            d = Disk(MY_TESTDISK_PATH, _GPT)
            add_partition(d.node, partno=1, start=8192)
            delete_partition(d.node, partno=1)
            d = Disk(MY_TESTDISK_PATH, _DOS)
            add_partition(d.node, partno=1, start=8192)
            delete_partition(d.node, partno=1)
            self.assertEqual(d.partitiontable_type, _DOS) 
        d = Disk(MY_TESTDISK_PATH, _GPT)
        add_partition(d.node, partno=1, start=8192)
        delete_partition(d.node, partno=1)
        d = Disk(MY_TESTDISK_PATH)
        add_partition(d.node, partno=1, start=8192)
        self.assertEqual(d.partitiontable_type, _GPT) 
    
    def testSimpleParttableWipe(self):
        d = Disk(MY_TESTDISK_PATH, _GPT)
        d.add_partition(partno=1, start=8192)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(d.partitions[0].partno, 1)
        d.delete_partition(partno=1)
        self.assertEqual(len(d.partitions), 0)
        self.assertEqual(d.partitions, [])
        self.assertEqual(d.partitiontable_type, _GPT)

    def testUnnecessaryWipes(self):
        d = Disk(MY_TESTDISK_PATH, _GPT)
        d.delete_all_partitions()
        for i in range(0,9):
            d.delete_partition(i) #, update=False)
        for i in range(0,9):
            d.delete_partition(i, update=False)


class TestPartitionCreation(unittest.TestCase):
    def setUp(self):
        self.disk = Disk(MY_TESTDISK_PATH, _GPT)
        d = self.disk
        d.add_partition(size_in_MiB=200)
        d.add_partition(size_in_MiB=200)
        d.add_partition(size_in_MiB=200)
        self.assertFalse(partition_exists(d.node, 0))
        self.assertEqual(d.partitions[0].partno, 1)
        self.assertEqual(d.partitions[1].partno, 2)
        self.assertEqual(d.partitions[2].partno, 3)
        self.assertFalse(partition_exists(d.node, 4))

    def tearDown(self):
        d = self.disk
        d.delete_all_partitions()
        for i in range(0,20):
            self.assertFalse(partition_exists(d.node, i))

    def testMakeFourPhysicalPartitions(self):
        d = self.disk
        d.add_partition(partno=4)
        self.assertEqual(d.partitions[3].partno, 4)
        self.assertGreater(d.partitions[1].start, d.partitions[0].end)
        self.assertGreater(d.partitions[2].start, d.partitions[1].end)
        self.assertGreater(d.partitions[3].start, d.partitions[2].end)
        self.assertGreater(d.partitions[3].end, d.partitions[2].end)
        self.assertFalse(partition_exists(d.node, 0))
        self.assertTrue(partition_exists(d.node, 1))
        self.assertTrue(partition_exists(d.node, 2))
        self.assertTrue(partition_exists(d.node, 3))
        self.assertTrue(partition_exists(d.node, 4))
        self.assertFalse(partition_exists(d.node, 5))
        
    def testMake737(self):
        d = self.disk
        d.add_partition(partno=7, size_in_MiB=50)
        d.add_partition(partno=37, size_in_MiB=75)
        self.assertEqual(len(d.partitions), 5)
        self.assertEqual(d.partitions[0].partno, 1)
        self.assertEqual(d.partitions[1].partno, 2)
        self.assertEqual(d.partitions[2].partno, 3)
        self.assertEqual(d.partitions[3].partno, 7)
        self.assertEqual(d.partitions[4].partno, 37)
        self.assertFalse(4 in [p.partno for p in d.partitions])
        self.assertFalse(6 in [p.partno for p in d.partitions])
        self.assertFalse(36 in [p.partno for p in d.partitions])
        self.assertFalse(38 in [p.partno for p in d.partitions])

    def testMakeAndDeleteRandomly(self):
        d = self.disk
        newpartno = None
        start_base = d.partitions[-1].end + 1
        for _ in range(0,10):
            oldpartno = newpartno
            newpartno = random.randint(5,10)
            if oldpartno is not None:
                d.delete_partition(oldpartno)
            d.add_partition(partno=newpartno, start=start_base + 200*newpartno, end=start_base + 200*(newpartno+1))


'''
from my.globals import call_binary, _GPT, _DOS
from my.disktools.disks import Disk, get_serno, set_serno
from test import MY_TESTDISK_PATH
import random
d = Disk(MY_TESTDISK_PATH, _GPT)
d.add_partition(size_in_MiB=200)
d.add_partition(size_in_MiB=200)
d.add_partition(size_in_MiB=200)
newpartno = None
oldpartno = newpartno
newpartno = random.randint(5,10)
if oldpartno is not None:
    d.delete_partition(oldpartno)

start_base = d.partitions[-1].end + 1
d.add_partition(partno=newpartno, start=start_base + 200*newpartno, end=start_base + 200*(newpartno+1))


'''

        
class TestSerialNumberThing(unittest.TestCase):
    def setUp(self):
        self.disk = Disk(MY_TESTDISK_PATH, _GPT)
    
    def tearDown(self):
        pass

    def testCheckDiskSerno(self):
        from my.disktools.disks import get_serno
        d = self.disk
        shouldbe_serno = get_serno(d.node)
        actuallyis_serno = d.serno
        self.assertEqual(shouldbe_serno, actuallyis_serno)
        xxx  = d.serno.replace('9','0').replace('4','7').replace('8','3')
        d.serno = xxx
        new_one = get_serno(d.node)
        self.assertEqual(new_one, d.serno)




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
