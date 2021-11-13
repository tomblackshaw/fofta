"""
Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_disktools.test_gpt_parts

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
            self.assertEqual(d.disklabel_type, _DOS) 
        d = Disk(MY_TESTDISK_PATH, _GPT)
        add_partition(d.node, partno=1, start=8192)
        delete_partition(d.node, partno=1)
        d = Disk(MY_TESTDISK_PATH)
        add_partition(d.node, partno=1, start=8192)
        self.assertEqual(d.disklabel_type, _GPT) 
    
    def testSimpleParttableWipe(self):
        d = Disk(MY_TESTDISK_PATH, _GPT)
        d.add_partition(partno=1, start=8192)
        self.assertEqual(len(d.partitions), 1)
        self.assertEqual(d.partitions[0].partno, 1)
        d.delete_partition(partno=1)
        self.assertEqual(len(d.partitions), 0)
        self.assertEqual(d.partitions, [])
        self.assertEqual(d.disklabel_type, _GPT)

    def testUnnecessaryWipes(self):
        d = Disk(MY_TESTDISK_PATH, _GPT)
        d.delete_all_partitions()
        for i in range(0,9):
            d.delete_partition(i) #, update=False)
        for i in range(0,9):
            d.delete_partition(i, update=False)
        


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
