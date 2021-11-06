# -*- coding: utf-8 -*-
"""test_Disk_class test module

Created on Nov 5, 2021

@author: Tom Blackshaw

Usage:-
    $ python3 -m unittest test.test_fructify.test_simple_creation_stuff

"""


import unittest
from my.globals import call_binary
import os
from my.exceptions import DestinationDeviceTooSmallError
from my.fructify import generate_blank_output_image


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass


class TestCreateAnUnpopulatedWorkingCopyOfTheSourceImage(unittest.TestCase):

    def setUp(self):
#        os.environ['PATH'] = os.environ['PATH']+':'+os.getenv('PATH')
#        import pydevd; pydevd.settrace("192.168.0.139", port=5678, stdoutToServer=True, stderrToServer=True)
        self.stubf = "/root/.tmp/testsimplecreationstuff"
        call_binary(['mkdir','-p', os.path.dirname(self.stubf)])
        os.system("rm %s* 2> /dev/null" % self.stubf)
        self.temp_input_fsize = 80
        self.temp_output_fsize = int(32 + self.temp_input_fsize * 1.5)
        self.temp_input_fname = "%s%s" % (self.stubf, '_in') # generate_random_string(32))
        self.temp_output_fname ="%s%s" % (self.stubf, '_out') # generate_random_string(32))
        self.input_loopdev="/dev/loop4"
        self.output_loopdev="/dev/loop5"
        self.assertTrue(os.path.exists(self.input_loopdev))
        self.assertTrue(os.path.exists(self.output_loopdev))
        os.system("losetup -d {loopdev} 2> /dev/null".format(loopdev=self.input_loopdev))
        os.system("losetup -d {loopdev} 2> /dev/null".format(loopdev=self.output_loopdev))
        os.system("losetup -D")
        _retval, _stdout_txt, _stderr_txt = call_binary(['dd', 
                                                                  'if=/dev/urandom',
                                                                  'of=%s' % self.temp_input_fname,
                                                                  'bs=1024k',
                                                                  'count=%d' % self.temp_input_fsize])
#        self.assertEqual(retval, 0)
        _retval, _stdout_txt, _stderr_txt = call_binary(['dd', 
                                                                  'if=/dev/urandom',
                                                                  'of=%s' % self.temp_output_fname,
                                                                  'bs=1024k',
                                                                  'count=%d' % self.temp_output_fsize])
#        self.assertEqual(retval, 0)
        _retval, _stdout_txt, _stderr_txt = call_binary(['losetup',self.input_loopdev, self.temp_input_fname])
#        self.assertEqual(retval, 0)
        _retval, _stdout_txt, _stderr_txt = call_binary(['losetup',self.output_loopdev, self.temp_output_fname])
#        self.assertEqual(retval, 0)

    def tearDown(self):
        os.system("rm %s* 2> /dev/null" % self.stubf)
        os.system("losetup -d {loopdev} 2> /dev/null".format(loopdev=self.input_loopdev))
        os.system("losetup -d {loopdev} 2> /dev/null".format(loopdev=self.output_loopdev))
        os.system("rm %s* 2> /dev/null" % self.stubf)     
        os.system("losetup -D 2> /dev/null")   

    def testInvalidParams(self):
        with self.assertRaises(ValueError): generate_blank_output_image(None, None, None)
        with self.assertRaises(ValueError): generate_blank_output_image(source=None, destination=None, size_in_MB=None)
        with self.assertRaises(ValueError): generate_blank_output_image(source=None, destination=None, size_in_MB='fish')
        with self.assertRaises(ValueError): generate_blank_output_image(source='None', destination='None', size_in_MB='fish')
        with self.assertRaises(ValueError): generate_blank_output_image(source='None', destination='None', size_in_MB=-1)
        with self.assertRaises(ValueError): generate_blank_output_image(source='None', destination='None', size_in_MB=127)

    def testFaultyParams(self):
        with self.assertRaises(ValueError): generate_blank_output_image(source=self.input_loopdev, destination=self.input_loopdev, size_in_MB=1)
        with self.assertRaises(ValueError): generate_blank_output_image(source=self.output_loopdev, destination=self.output_loopdev, size_in_MB=1)
        with self.assertRaises(ValueError): generate_blank_output_image(source=self.input_loopdev, destination=self.output_loopdev, size_in_MB=1)

    # def testFaultMountpointSource(self):
    #     src_mtpt = '/root/.tmp/qqqq'
    #     dest_mtpt = '/root/.tmp/rrrr'
    #     call_binary(['mkdir','-p',src_mtpt])
    #     call_binary(['mkdir','-p',dest_mtpt])
    #     call_binary(['mkfs.btrfs', '-f', self.input_loopdev])
    #     call_binary(['mkfs.btrfs', '-f', self.output_loopdev])
    #     call_binary(['mount', self.input_loopdev, src_mtpt])
    #     with self.assertRaises(ValueError): generate_blank_output_image(source=src_mtpt, destination=src_mtpt, size_in_MB=1)
    #     generate_blank_output_image(source=src_mtpt, destination=self.output_loopdev, size_in_MB=self.temp_input_fsize) #  os.path.getsize(self.temp_output_fsize)//1024//1024)
    #     call_binary(['umount', self.input_loopdev])
    #     call_binary(['mount', self.output_loopdev, dest_mtpt])
    #     with self.assertRaises(ValueError): generate_blank_output_image(source=dest_mtpt, destination=dest_mtpt, size_in_MB=1)
    #     generate_blank_output_image(source=dest_mtpt, destination=self.output_loopdev, size_in_MB=self.temp_input_fsize) # size_in_MB=os.path.getsize(self.temp_output_fsize)//1024//1024)
    #     call_binary(['umount', self.output_loopdev])

    def testNerdyButSoundParams(self):       
        generate_blank_output_image(source=self.input_loopdev, destination=self.output_loopdev, size_in_MB=128)
        generate_blank_output_image(source=self.input_loopdev, destination=self.output_loopdev, size_in_MB=self.temp_input_fsize)
        generate_blank_output_image(source=self.input_loopdev, destination=self.output_loopdev, size_in_MB=self.temp_output_fsize)
        generate_blank_output_image(source=self.temp_input_fname, destination=self.input_loopdev, size_in_MB=self.temp_input_fsize)
        generate_blank_output_image(source=self.input_loopdev, destination=self.temp_output_fname, size_in_MB=128)
        generate_blank_output_image(source=self.temp_input_fname, destination=self.temp_output_fname, size_in_MB=128)
        generate_blank_output_image(source=self.temp_input_fname, destination=self.input_loopdev, size_in_MB=self.temp_input_fsize)
        generate_blank_output_image(source=self.input_loopdev, destination=self.temp_output_fname, size_in_MB=self.temp_input_fsize)
        generate_blank_output_image(source=self.temp_input_fname, destination=self.temp_output_fname, size_in_MB=self.temp_input_fsize)
        with self.assertRaises(DestinationDeviceTooSmallError): generate_blank_output_image(source=self.temp_input_fname, destination=self.input_loopdev, size_in_MB=self.temp_output_fsize)
        generate_blank_output_image(source=self.input_loopdev, destination=self.temp_output_fname, size_in_MB=self.temp_output_fsize)
        generate_blank_output_image(source=self.temp_input_fname, destination=self.temp_output_fname, size_in_MB=self.temp_output_fsize)

    def testActualCopyingOfData(self):
        generate_blank_output_image(source=self.input_loopdev, destination=self.output_loopdev, size_in_MB=self.temp_output_fsize)
        



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


# :-)
