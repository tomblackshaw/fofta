# -*- coding: utf-8 -*-
"""my.disktools.disks

Globally appealing functions.

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains subroutines for viewing and modifying disks (but
not partitions themselves). In particular, it contains the Disk class,
which is used to control individual disks. The device's path is sent
as a parameter (e.g. /dev/sda) to the class instance creator.

Usage:-
    $ python3 -m unittest test.test_disktools.test_globals
    $ python3 -m unittest test.test_disktools.test_globals.TestCallBinary.testDaftParameters

Todo:
    * Add more TODOs

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import os
import random
import sys
from test import MY_TESTDISK_PATH
import unittest
from my.globals import call_binary, generate_random_string, pause_until_true


class TestCallBinary(unittest.TestCase):
    def setUp(self):
        from my.disktools.disks import Disk

        self.disk = Disk(MY_TESTDISK_PATH)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testDaftParameters(self):
        _ = call_binary(["ls"])
        (retcode, stdin_str, stdout_str) = call_binary(["ls"])  # @UnusedVariable
        with self.assertRaises(ValueError):
            # @UnusedVariable  #pylint: disable=unbalanced-tuple-unpacking
            _, __ = call_binary(["ls"])
        with self.assertRaises(FileNotFoundError):
            _ = call_binary(["lsd123"])
        _ = call_binary(["ls"], None)
        _ = call_binary(["ls"], "")

    def testKnownNonzeroResults(self):
        assert not os.path.exists("/this/folder/really/shouldnt/exist")
        retcode, stdout_txt, stderr_txt = call_binary(
            ["ls", "/this/folder/really/shouldnt/exist"]
        )
        self.assertNotEqual(retcode, 0)
        self.assertNotEqual(stderr_txt, "")
        self.assertNotEqual(stderr_txt, None)
        del retcode, stdout_txt, stderr_txt

    def testKnownZeroResults(self):
        self.assertEqual(call_binary(["ls"])[0], 0)
        self.assertEqual(call_binary(["ls", "/"])[0], 0)
        retcode, stdout_txt, stderr_txt = call_binary(["ls", self.disk.node])
        del stdout_txt, stderr_txt
        self.assertEqual(retcode, 0)
        self.disk.add_partition(partno=1, start=5555, end=9999, fstype="83")
        self.assertEqual(call_binary(["ls", self.disk.node])[0], 0)
        self.assertEqual(call_binary(["ls", self.disk.partitions[0].node])[0], 0)
        retcode, stdout_txt, stderr_txt = call_binary(["fdisk", "-l", self.disk.node])
        self.assertEqual(retcode, 0)
        self.assertTrue(
            stdout_txt.find(str(self.disk.partitions[0].start)) >= 0
            and stdout_txt.find(str(self.disk.partitions[0].end)) >= 0
            and stdout_txt.find(str(self.disk.partitions[0].node)) >= 0
        )
        self.assertEqual(stderr_txt, "")

    def testEcho(self):
        for i in range(10):
            hexstr = generate_random_string(random.randint(10, 40))
            retcode, stdout_txt, stderr_txt = call_binary(
                ["bash"], '''echo -en "{hexstr}"'''.format(hexstr=hexstr)
            )
            self.assertEqual(retcode, 0)
            self.assertEqual(hexstr, stdout_txt)
        del i, retcode, stdout_txt, stderr_txt



class TestPauseUntilTrue(unittest.TestCase):
    def setUp(self):
        from my.disktools.disks import Disk

        self.disk = Disk(MY_TESTDISK_PATH)

    def tearDown(self):
        self.disk.delete_all_partitions()

    def testName(self):
        random_fname = '/tmp/%s' % generate_random_string(32)
        os.system("sleep 3; touch %s" % random_fname)
        pause_until_true(timeout=5, test_func=(lambda x=random_fname: os.path.exists(x)))
        os.system("(sleep 5; rm -f %s) &" % random_fname)
        with self.assertRaises(TimeoutError):
            pause_until_true(timeout=2, test_func=(lambda x=random_fname: not os.path.exists(x)))
        pause_until_true(timeout=6, test_func=(lambda x=random_fname: not os.path.exists(x)),
                         nudge_func = lambda: os.system('sync'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    sys.path.append(os.getcwd())
    unittest.main()
