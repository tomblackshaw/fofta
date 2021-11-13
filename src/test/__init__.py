# -*- coding: utf-8 -*-
"""test_get_disk_record test module

Created on Oct 19, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test
    $ python3 -m unittest test.SomethingOrOther

"""
import os.path
import unittest
import random

MY_TESTDISK_PATH = "/dev/sda"  # disk/by-id/usb-Mass_Storage_Device_121220160204-0:0'
MY_PARTTABLETYPE = 'dos' # ('gpt','dos')[random.randint(0,1)]

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    if not os.path.exists(MY_TESTDISK_PATH):
        raise SystemError(
            "Test disk {d} is missing! Please insert a micro-SD card and try again.".format(
                d=MY_TESTDISK_PATH
            )
        )
    unittest.main()
