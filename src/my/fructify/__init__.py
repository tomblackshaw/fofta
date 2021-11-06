# -*- coding: utf-8 -*-
"""test_fructify

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test.test_fructify

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from my.globals import call_binary
import os
from my.exceptions import BlankFileCreationError, DestinationPaddingWriteError, \
            DestinationDeviceTooSmallError, DestinationImageWriteError, MBRCopyError, \
            FilesystemCopyError
from my.disktools.disks import is_this_a_disk





def generate_blank_output_image(source, destination, size_in_MB=None):
    """Create a blank output image on which for me to store the source's contents.

    If there is an existing & satisfactory copy of the disk image, use it.
    ('Satisfactory' means 'of a sensible length'. We can re-use almost
    any image, as long as it's long enough and is formattable.) If there
    isn't one, take a copy of the source image. Either way, get a workable
    block of formattable bytes & supply it as the working copy. THIS HAS
    NOTHING TO DO WITH COPYING THE FILESYSTEM. We just want to copy the
    boot sector etc. and make sure our working image is long enough.
    
    Oh, and add 1GB of blank data if the image is a fresh copy of the
    original source material. That way, we've extra room for new files.

    Example:
        $ generate_blank_output_image('/root/in.img', '/dev/sda')
        $ generate_blank_output_image('/dev/mmcblk0', '/root/out.img')
        $ generate_blank_output_image('/root/in.img', '/root/out.img')

    Args:
        source (:obj:`str`): Full path to the input disk or image.
        destination (:obj:`str`): Full path to the output disk or image.
        size_in_MB (int, optional): Desired size of output. If the
            destination is not a disk image, isize_in_MB is ignored.

    Returns:
        None.

    Raises:
        ValueError: Invalid parameters.
    
    Todo:
        * Better TODO lists
        * Don't use global _disks_dct; do something smarter

    """
    # if isize_in_MB is None:
    #     try:
    #         isize_in_MB = 1 + os.path.getsize(source) // 1024 // 1024
    #     except (ValueError, TypeError, FileNotFoundError):
    #         pass
    if source is None or destination is None or not os.path.exists(source) or not os.path.exists(os.path.dirname(destination)):
        raise ValueError("Bad parameters. Please specify sane values for source and destination.")
    if source == destination:
        raise ValueError("Bad parameters. The input name must not be identical to the output.")
    if 0 == os.system('''mount | grep "%s " | grep " %s "''' % (source, destination)) \
    or 0 == os.system('''mount | grep "%s " | grep " %s "''' % (destination, source)):
        raise ValueError("It appears that the source and destination are the same.")
    if size_in_MB:
        if size_in_MB < 70:
            raise ValueError("The image size will be laughably small.")
        retval, _stdout_txt, stderr_txt=call_binary(['dd', 'iflag=fullblock', 'status=progress', 'bs=1024k', 'if=/dev/zero', 'of=%s.tmp' % destination, \
                                               'count=%d' % size_in_MB])
    else:
        retval, _stdout_txt, stderr_txt=call_binary(['dd', 'iflag=fullblock', 'status=progress', 'bs=1024k', 'if=/dev/zero', 'of=%s.tmp' % destination])
    if retval != 0:
        raise BlankFileCreationError("Unable to write out temp blank file\n{stderr_txt}".format(stderr_txt=stderr_txt))
    retval, _stdout_txt, stderr_txt= call_binary(['cp', '-f', destination+'.tmp', destination])
    os.system('rm -f "%s.tmp"' % destination)
    if retval != 0:
        raise DestinationDeviceTooSmallError("Destination device is too small for the temp image you've created.")
    retval, _stdout_txt, stderr_txt= call_binary(['dd','status=progress','iflag=fullblock','bs=1024k','count=64',
                                                     'conv=notrunc','if='+source, 'of='+destination])
    if retval != 0:
        raise MBRCopyError( "Failed to copy the master boot record (including boot sector) across.\n%s" % stderr_txt)
    if size_in_MB is not None and not destination.startswith('/dev/') and os.path.getsize(destination)//1024//1024 < size_in_MB:
        retval = os.system('''dd if=/dev/zero bs=1024k count={how_many_MBs} >> "{dest}" 2> /dev/null'''.format(\
                                           how_many_MBs=size_in_MB-os.path.getsize(destination)//1024//1024,\
                                           dest=destination))
        if retval != 0:
            raise DestinationPaddingWriteError("Failed to pad out and rightsize the destination image")




def fructify_me(source, destination, fstype, phase):
    # if is_this_a_disk(source) or not os.path.exists(source) or os.path.isdir(source):
    #     raise ValueError("Please specify a source disk image, e.g. /root/somethingsomething.img.gz or /root/blah.img")
    # if is_this_a_disk(destination) or os.path.isdir(source):
    #     raise ValueError("Please specify an output file, e.g. /root/output.img or /root/op.img.xz")
    generate_blank_output_image(source, destination, fstype)
    # repartition_and_losetup_our_working_copy(destination)
    # format_and_mount_root(destination, fstype)
    # format_and_mount_our_wkg_copy_boot_partition(destination, fstype)
    # populate_working_copy(source, destination)
    # modify_diskresizer_script(destination)
    # adjust_bootup_configuration(destination)
    # if fstype == 'zfs':
    #     os.system("systemctl stop zed")
    #     do_the_legwork()
    #     losetup -D
    # else
    #     echo -en "succeeded.\nUnmounting everything..."
    #     unmount_disk_image_and_loopdevs
    # fi
    return 0


