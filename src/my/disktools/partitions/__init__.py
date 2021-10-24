"""FOFTA - from one filesystem to another

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test/test_partitiontools

https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
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

import os

from my.disktools.disks import get_disk_record_from_all_disks
from my.exceptions import PartitionDeletionError, PartitionCreationError
from my.globals import _FS_EXTENDED, _FS_DEFAULT


class DiskPartition:
    """This is an example of a module level function.

    Function parameters should be documented in the ``Args`` section. The name
    of each parameter is required. The type and description of each parameter
    is optional, but should be included if not obvious.

    If \*args or \*\*kwargs are accepted,
    they should be listed as ``*args`` and ``**kwargs``.

    The format for a parameter is::

        name (type): description
            The description may span multiple lines. Following
            lines should be indented. The "(type)" is optional.

            Multiple paragraphs are supported in parameter
            descriptions.

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

    def __init__(self, devpath):
        from my.disktools.both import find_node_to_which_a_partition_belongs
        self.__user_specified_node = devpath
        self._owner = find_node_to_which_a_partition_belongs(self.__user_specified_node)
        if self._owner is None:
            raise ValueError("%s does not belong to any disk" % self.__user_specified_node)
        self.__cache = None
        self.update()

    def __repr__(self):
        # TODO: QQQ add locking
        return f'DiskPartition(node="%s")' % self.node

    def __str__(self):
        return """node=%s partno=%d owner=%s start=%d size=%d fstype=%s label=%s partuuid=%s path=%s uuid=%s""" % \
            (self._node, self.partno, self._owner, self._start, self._size, self._fstype, self._label, self._partuuid, self._path, self._uuid)

    def update(self):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        self.__cache = find_partition_instance(self.__user_specified_node)
        self._node = self.__cache.node
        self._start = self.__cache.start
        self._size = self.__cache.size
        self._fstype = self.__cache.type
        self._id = self.__cache.id
        self._label = self.__cache.label
        self._partuuid = self.__cache.partuuid
        self._path = self.__cache.path
        self._uuid = self.__cache.uuid

    @property
    def node(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._node

    @node.setter
    def node(self, value):
        raise AttributeError("Not permitted")

    @node.deleter
    def node(self):
        raise AttributeError("Not permitted")

    @property
    def partno(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        n = deduce_partno(self.node)
        return n

    @partno.setter
    def partno(self, value):
        raise AttributeError("Not permitted")

    @partno.deleter
    def partno(self):
        raise AttributeError("Not permitted")

    @property
    def owner(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._owner

    @owner.setter
    def owner(self, value):
        raise AttributeError("Not permitted")

    @owner.deleter
    def owner(self):
        raise AttributeError("Not permitted")

    @property
    def start(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @start.deleter
    def start(self):
        raise AttributeError("Not permitted")

    @property
    def end(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._start + self._size - 1

    @end.setter
    def end(self, value):
        raise AttributeError("Not permitted")

    @end.deleter
    def end(self):
        raise AttributeError("Not permitted")

    @property
    def size(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @size.deleter
    def size(self):
        raise AttributeError("Not permitted")

    @property
    def fstype(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._fstype

    @fstype.setter
    def fstype(self, value):
        self._fstype = value

    @fstype.deleter
    def fstype(self):
        raise AttributeError("Not permitted")

    @property
    def id(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def label(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._label

    @label.setter
    def label(self, value):
        raise AttributeError("Not permitted")

    @label.deleter
    def label(self):
        raise AttributeError("Not permitted")

    @property
    def partuuid(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._partuuid

    @partuuid.setter
    def partuuid(self, value):
        raise AttributeError("Not permitted")

    @partuuid.deleter
    def partuuid(self):
        raise AttributeError("Not permitted")

    @property
    def path(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._path

    @path.setter
    def path(self, value):
        raise AttributeError("Not permitted")

    @path.deleter
    def path(self):
        raise AttributeError("Not permitted")

    @property
    def uuid(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        raise AttributeError("Not permitted")

    @uuid.deleter
    def uuid(self):
        raise AttributeError("Not permitted")


def deduce_partno(node):

    if node in (None, '') or os.path.isdir(node) or not node.startswith('/dev/') or node == '/dev/':
        raise ValueError("Node %s is a silly value" % str(node))
    try:
        s = node.split('/')[-1]
        i = len(s) - 1
        while i >= 0 and s[i].isdigit():
            i = i - 1
        return int(s[i + 1:])
    except (AttributeError, ValueError):
        return ''


def delete_all_partitions(node):

    realnode = os.path.realpath(node)
    os.system('''sfdisk -d {node}| grep -vx "{node}.*[0-9] : .*"| sfdisk -f {node} 2>/dev/null >/dev/null'''.format(node=realnode))
    os.system("partprobe {node}".format(node=realnode))


def was_this_partition_created(node, partno):

    node = os.path.realpath(node)
    res = os.system('''
node=%s
partno=%d
fullpartitiondev=$(sfdisk -d $node | grep -x "$node.*$partno :.*" | head -n1 | cut -d' ' -f1)
[ -e "$fullpartitiondev" ] && return 0 || return 1
    ''' % (node, partno))
    if res == 0:
        return True
    else:
        return False


def add_partition_SUB(node, partno, start, end, fstype, with_partno_Q=True, size_in_MiB=None, debug=False):

    node = os.path.realpath(node)
    res = 0
    if debug:
        print("add_partition_SUB() -- node=%s; partno=%s; start=%s; end=%s; size_in_MiB=%s" % (str(node), str(partno), str(start), str(end), str(size_in_MiB)))
    if end is not None and size_in_MiB is not None:
        raise ValueError("Specify either end=... or size_in_MIB... but don't specify both")
    elif end is None and size_in_MiB is not None:
        end_str = "+%dM" % size_in_MiB
    elif end is not None and size_in_MiB is None:
        end_str = "%d" % end
    else:
        end_str = None
    if debug:
        print("end_str is", end_str)
        debug_str = ''
    else:
        debug_str = ' >/dev/null 2>/dev/null'
    # if start is None and partno == 5:
    #     raise AttributeError("Please specify the starting sector for partition %d of %s" % (partno, node))
    if with_partno_Q:
        res = os.system('''echo "p\nn\n%s\n%s\n%s\n%s\nw" | fdisk %s %s''' % (
                'e' if fstype == _FS_EXTENDED else 'l' if partno >= 5 else 'p',
                '' if not partno else str(partno),
                '' if not start else str(start),
                '' if not end_str else end_str, node, debug_str))
    else:
        res = os.system('''echo "p\nn\n%s\n%s\n%s\nw" | fdisk %s %s''' % (
                'e' if fstype == _FS_EXTENDED else 'l' if partno >= 5 else 'p',
                '' if not start else str(start),
                '' if not end_str else end_str, node, debug_str))
    res += os.system('''sfdisk --part-type {node} {partno} {fstype} {debug}'''.format(node=node, partno=partno, fstype=fstype,
                                                                                     debug='' if debug else '> /dev/null 2> /dev/null'))
    return res


def add_partition(node, partno, start, end=None, fstype=_FS_DEFAULT, debug=False, size_in_MiB=None):

    node = os.path.realpath(node)
    if debug:
        print("add_partition() -- node=%s; partno=%s; start=%s; end=%s; fstype=%s; size_in_MiB=%s" % (str(node), str(partno), str(start), str(end), fstype, str(size_in_MiB)))
    if end is not None and start is not None and end <= start:
        raise ValueError("The partition must end after it starts")
    res = 0
    if partno in (1, 5):
        res = add_partition_SUB(node, partno, start, end, fstype, with_partno_Q=False, debug=debug, size_in_MiB=size_in_MiB)
        if not was_this_partition_created(node, partno):
            res = add_partition_SUB(node, partno, start, end, fstype, debug=debug, size_in_MiB=size_in_MiB)
    elif partno > 5 and not was_this_partition_created(node, partno - 1):
        raise ValueError("Because partition #%d of %s does not exist, I cannot create #%d. Logical partitions cannot be added without screwing up their order. Sorry." % (partno - 1, node, partno))
    else:
        res = add_partition_SUB(node, partno, start, end, fstype, debug=debug, size_in_MiB=size_in_MiB)
    if not was_this_partition_created(node, partno):
        os.system('sync;sync;sync;partprobe;sync;sync;sync')
    if not was_this_partition_created(node, partno):
        raise PartitionCreationError(
            "Failed to add partition #{partno} to {node}".format(
                partno=partno, node=node))
    del res
    return 0  # Throw away res if the partition was successfully created


def find_partition_instance(path_of_partition):

    if not os.path.exists(path_of_partition):
        raise ValueError("Cannot find partition %s" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_instance_our_partition(path_of_partition, p):
                return p
    return None

#


def is_this_partition_instance_our_partition(path_of_partition, p):

    if path_of_partition == p.node \
    or path_of_partition == p.partuuid \
    or path_of_partition == p.uuid \
    or path_of_partition == p.label \
    or path_of_partition == p.path:
        return True
    else:
        return False


def delete_partition(node, partno):

    if partno >= 5 and was_this_partition_created(node, partno + 1):
        raise PartitionDeletionError(
            "Because partition #%d of %s exists, I cannot create #%d. \
Logical partitions cannot be removed without screwing up their order. \
Sorry." % (partno + 1, node, partno))
    res = os.system('''sfdisk %s --del %d > /dev/null 2> /dev/null''' % (
        node, partno))
    if was_this_partition_created(node, partno):
        os.system('sync;sync;sync;partprobe;sync;sync;sync')
    if was_this_partition_created(node, partno):
        raise PartitionDeletionError(
            "Failed to delete partition #{partno} to {node}".format(
                partno=partno, node=node))
    del res
    return 0  # Throw away res if the partition was successfully deleted

