# -*- coding: utf-8 -*-
"""main.py

Created on Oct 16, 2021
@author: Tom Blackshaw

FOFTA - from one filesystem to another!

Example:
    To run a unit test::

        $ python3 -m unittest discover
    ...or...
        $ python3 -m unittest test.test_disktools.test_Disk_class.TestCreateDeliberatelyOverlappingPartitions

    To reformat::

        $ cd .../src && black *.py */*.py */*/*.py */*/*/*.py */*/*/*/*.py

Todo:
    * QQQ Finish me QQQ
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""


# import os
# import sys

# from my.fructify import fructify_me


#import getopt


def main():
    print("FOFTA --- OS backup and migration tool")
#    getopt.getopt


#     outputimage_serial_number = '''$(printf "%08x" 0x$(dd if=/dev/urandom bs=1 count=200 2>/dev/null | tr -dc 'a-f0-9' | cut -c-8))'''
#     fourdig_serno = outputimage_serial_number[-4:]
#     boot_partition_label = "ambn{fourdig_serno}boot".format(fourdig_serno)
#     root_partition_label = "ambn{fourdig_serno}root".format(fourdig_serno)
#     xtra_partition_label = "ambn{fourdig_serno}xtra".format(fourdig_serno)  # p3 (ZFS only)
#     source_img_file = '/root/build_here_on_neo3/source/Armbian_21.08.1_Nanopineo3_focal_current_5.10.60.img'
# #    source_img_file = '/'
#     root_FS_format = 'zfs'
#     output_image_fname = '/dev/sda'
# #    output_image_fname= '$(my_bootroot_disk_dev)'
# #    output_image_fname = '/root/out.$root_FS_format.img'
#     cwd = os.getcwd()
#     builddir = '/tmp/my_builddir_{fourdig_serno}'.format(fourdig_serno)
#     os.system('mkdir -p "{builddir}"'.format(builddir=builddir))
#     if 0 != os.system('which lzop > /dev/null'):
#         raise SystemError("Please install lzop")
#     if len(sys.argv) > 1 and sys.argv[1] == 'rclocal':
#         fructify_me(rclocal=True)
#     elif 1 == len(sys.argv):
#         fructify_me(gui=True)
#     elif 3 == len(sys.argv):
#         fructify_me(sys.argv[0], sys.argv[1], sys.argv[2])
#     else:
#         raise SystemError('''
# {parm0} <incoming image filename> <btrfs|zfs|xfs|ext4> <output image filename>
#
# e.g. $0 /root/armbian.img btrfs /root/out.img
# '''.format(parm0=sys.argv[0]))
#     os.system('''cd "{cwd}"'''.format(cwd=cwd))
#     sys.exit(0)


if __name__ == "__main__":
    main()
