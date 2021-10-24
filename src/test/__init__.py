'''
Created on Oct 19, 2021

@author: Tom Blackshaw

# cd ~/src
# python3 -m unittest discover
'''
import os.path
import unittest

MY_TESTDISK_NODE = '/dev/disk/by-id/usb-Mass_Storage_Device_121220160204-0:0'

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    if not os.path.exists(MY_TESTDISK_NODE):
        raise SystemError("Test disk {d} is missing! Please insert a micro-SD card and try again.".format(d=MY_TESTDISK_NODE))
    unittest.main()

