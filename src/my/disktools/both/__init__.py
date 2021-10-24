# -*- coding: utf-8 -*-
"""my.disktools.both

Created on Oct 16, 2021
@author: Tom Blackshaw

https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

onii0-ko9j0py18gt79fg6`p2ekm0    qu89Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from collections import namedtuple
import os

from my.globals import _FS_EXTENDED, _FS_DEFAULT


# .path, os.listdir
def find_node_to_which_a_partition_belongs(path_of_partition):
    """This is an example of a module level function.

    Function parameters should be documented in the ``Args`` section. The name
    of each parameter is required. The type and description of each parameter
    is optional, but should be included if not obvious.

    Args:
        param1 (int): The first parameter.
        param2 (:obj:`str`, optional): The second parameter. Defaults to None.
            Second line of description should be indented.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        bool: True if successful, False otherwise.

        The return type is optional and may be specified at the beginning of
        the ``Returns`` section followed by a colon.

        The ``Returns`` section may span multiple lines and paragraphs.
        Following lines should be indented to match the first line.

        The ``Returns`` section supports any reStructuredText formatting,
        including literal blocks::

            {
                'param1': param1,
                'param2': param2
            }

    Raises:
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `param2` is equal to `param1`.

    """
    from my.disktools.partitions import deduce_partno, delete_all_partitions, \
                was_this_partition_created, delete_partition, add_partition, \
                is_this_partition_instance_our_partition
    from my.disktools.disks import get_disk_record_from_all_disks
    if not os.path.exists(path_of_partition):
        raise ValueError("%s does not exist" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_instance_our_partition(path_of_partition, p):
                return d.partitiontable.node
    return None


def get_altpath_from_node_path(node_path, searchby):
    """Locate the /dev/disk/by-____/ softlink to the specified node.

    Each disk node and partition node -- e.g. /dev/sda, /dev/mmcblk0p2, etc. --
    is also listed in /dev/disk/by-uuid, /dev/disk/by-partuuid, etc. via soft-
    links. I search the specified subdirectory -- /dev/disk/by-{searchby} --
    and look for any softlinks to the specified node path. If I find it, I
    return it. If I can't find it, I return None.

    Args:
        node_path (:obj:`str`): The /dev/... entry, e.g. /dev/sdx1
        searchby (:obj:`str`): The search field:
            partuuid, uuid, id, label, or path

    Returns:
        str or None: The alternate path if found, None otherwise.

    Raises:
        ValueError: If `searchby` is invalid.

    """
    if not os.path.exists(node_path):
        raise ValueError("Node path %s not found" % node_path)
    altdir = "/dev/disk/by-%s" % searchby
    if not os.path.exists(altdir):
        raise ValueError("Cannot search by %s -- directory %s not found" % (searchby, altdir))
    for p in os.listdir(altdir):
        fullpath = os.path.join(altdir, p)
        try:
            linked_to = os.path.realpath(fullpath)
            if node_path == linked_to:
                return fullpath
        except FileNotFoundError:
            pass
    return None

# def write_new_disk_record_via_sfdisk(disk):

