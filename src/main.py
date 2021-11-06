# -*- coding: utf-8 -*-
"""main.py

Created on Oct 16, 2021
@author: Tom Blackshaw

FOFTA - from one filesystem to another!

To fix my SAMBA mount:
    On host:-
        sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.smbd.plist
        sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.smbd.plist
    Then, on guest:-
        bash /etc/rc.local



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


#import os
import sys

from my.fructify import fructify_me


def main(arguments):
    print("FOFTA --- OS backup and migration tool")
    if len(arguments) not in (4, 5):
        print("fofta <input> <output> <ext4|btrfs|xfs|zfs> (<phase>)")
        sys.exit(254)
    else:
        res = fructify_me(source=sys.argv[1], destination=sys.argv[2], fstype=sys.argv[3], \
                    phase=None if len(arguments) == 4 else sys.argv[4])
        return res


if __name__ == "__main__":
    sys.exit(main(sys.argv))
