'''
Created on Oct 19, 2021

@author: Tom Blackshaw
'''
import unittest
import sys.path


class Test(unittest.TestCase):

    def setUp(self):
        from my.partitiontools import Disk, DiskPartition
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']

    sys.path.append(os.getcwd())
    unittest.main()
