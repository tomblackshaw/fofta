# -*- coding: utf-8 -*-
"""my.disktools.both

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains subroutines for viewing and modifying both partitions
and disks. They are here because they do not fit neatly into either
category.

Todo:
    * Add more TODOs

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from collections import namedtuple
import os



def devdiskbyxxxx_path(device_path, searchby):
    """Locate the /dev/disk/by-____/ softlink to the specified device path.

    Each disk node and partition node -- e.g. /dev/sda, /dev/mmcblk0p2, etc. --
    is also listed in /dev/disk/by-uuid, /dev/disk/by-partuuid, etc. via soft-
    links. I search the specified subdirectory -- /dev/disk/by-{searchby} --
    and look for any softlinks to the specified node path. If I find it, I
    return it. If I can't find it, I return None.

    Args:
        device_path (:obj:`str`): The /dev/... entry, e.g. /dev/sdx1
        searchby (:obj:`str`): The search field:
            partuuid, uuid, id, label, or path

    Returns:
        str or None: The alternate path if found, None otherwise.

    Raises:
        ValueError: If `searchby` is invalid.

    Examples:
        $ devdiskbyxxxx_path('/dev/sda', 'id')
        '/dev/disk/by-id/usb-Mass_Storage_Device_121291847283-0:0'
        $ devdiskbyxxxx_path('/dev/sda', 'partuuid')
        $ # ^^^ It returns a None ^^^
        $ devdiskbyxxxx_path('/dev/mmcblk0p1', 'partuuid')
        '/dev/disk/by-partuuid/bbc1bbc2-01'
        $ devdiskbyxxxx_path('/dev/foo', 'id')
        ValueError: Device path /dev/foo does not exist
        $ devdiskbyxxxx_path('/dev/sda', 'height')
        ValueError: Cannot search by height -- directory /dev/disk/by-height not found

    """
    if not os.path.exists(device_path):
        raise ValueError("Device path %s does not exist" % device_path)
    altdir = "/dev/disk/by-%s" % searchby
    if not os.path.exists(altdir):
        raise ValueError(
            "Cannot search by %s -- directory %s not found" % (searchby, altdir)
        )
    for p in os.listdir(altdir):
        fullpath = os.path.join(altdir, p)
        try:
            linked_to = os.path.realpath(fullpath)
            if device_path == linked_to:
                return fullpath
        except FileNotFoundError:
            pass
    return None





def has_legible_parttable(node):
    from my.globals import call_binary
    """Return True if supplied disk path contains a legible partition table; else, False."""
    retcode, _stdouf_txt, _stderr_txt = call_binary(['sfdisk','-d',node])
    return True if retcode == 0 else False



