"""
Created on Oct 19, 2021

@author: Tom Blackshaw
"""
import os
import sys
import unittest

SAMPLE_LIST_OF_DRIVES_STUBS = ("sda", "sdb", "sdp", "mmcblk0", "mmcblk1", "mmcblk10")
SAMPLE_LIST_OF_DODGY_STUBS = ("b0rk", "sj5a", "hx", "tty100", "vcsu999")
SAMPLE_LIST_OF_BOGUS_PARAMS = (None, "", "/dec/blah", "dev/xyz", "1234", "/dev", "/")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()



