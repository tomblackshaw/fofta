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

from collections import namedtuple
import json
import os
import subprocess

from my.disktools.both import get_altpath_from_node_path
from my.disktools.partitions import was_this_partition_created, add_partition, \
    delete_partition, deduce_partno, is_this_partition_instance_our_partition, \
    DiskPartition, delete_all_partitions
from my.exceptions import PartitionCreationError
from my.globals import _FS_EXTENDED, _FS_DEFAULT


def is_this_a_disk(device_path, insist_on_this_existence_state=None):
    """Figure out if the supplied path is a disk (True) or a partition (False).

    Examine the supplied path. If it doesn't exist or if we can't figure out
    its nature by examining its path string, raise an exception. Otherwise,
    return True if it's a disk or False if it's a partition.

    Args:
        device_path (:obj:`str`): Full path to the node in question. The
            path may be a simple /dev entry, e.g. /dev/sda or /dev/sda1,
            or it may be /dev/disk/by-uuid/..... etc. The end result is
            the same. If it's a disk (a node that holds partitions), then
            the result returned will be True. If it's a partition, False.
            If we can't figure it out, we raise an exception.
        insist_on_this_existence_state (:obj:`bool`, optional): For debugging
            purposes, it forces the subroutine to assume that the device does
            (or does not) exist. Do not set unless debugging the subroutine.

    Returns:
        bool: True if a disk, False if a partition.

    Raises:
        ValueError: If the device doesn't exist, or is a softlink to a
            nonexistent file, or is a directory, or has an unfamiliar
            name structure.

    """
    if insist_on_this_existence_state is not None:
        exists = insist_on_this_existence_state
    else:
        exists = os.path.exists(device_path)
    if device_path in (None, '/') or not exists:
        raise ValueError("%s not found" % str(device_path))
    linked_to = os.path.realpath(device_path)
    search_for_this_stub = os.path.basename(linked_to)
    if device_path.count('/') > 3 and linked_to.count('/') <= 3:
        return is_this_a_disk(linked_to, insist_on_this_existence_state=insist_on_this_existence_state)
    elif deduce_partno(device_path) in (None, '') and search_for_this_stub.startswith('mmc'):
        return True
    elif search_for_this_stub.startswith('mmc'):
        if ('p' in search_for_this_stub[-4:-1]) \
        and search_for_this_stub[-1].isdigit():
            return False
        else:
            return True
    elif len(search_for_this_stub) >= 2 and search_for_this_stub[1] == 'd':
        if deduce_partno(device_path) not in (None, ''):
            return False
        else:
            return True
    elif os.path.isdir(device_path):
        raise ValueError("%s is a directory, not a device")
    elif 'zram' in os.path.basename(device_path):
        return False
    else:
        raise ValueError("I do not know if %s is a disk or not" % device_path)


def set_disk_id(node, new_diskid):
    """Set the serial number of the specified disk.

    If you run fdisk {node}, you'll see a field that says, "Disk ID: 0x....."
    or similar. That's the disk's serial number. Using fdisk, I can change it

    Args:
        node (:obj:`str`): The /dev entry (e.g. /dev/sda) of the node.
        new_diskid (:obj:`str`): A ten-character string, composed of the
            prefix '0x' and then eight hexadecimal characters, e.g.
            "0x1234ABCD".

    Returns:
        None

    Raises:
        None

    Todo:
        * Add a meaningful check --- did our serial-change succeed or fail?

    """
    os.system('''echo "x\ni\n{new_diskid}\nr\nw" | fdisk {node}'''.format(node=node, new_diskid=new_diskid))


def get_node_diskID_sizeB_sizeSecs_and_sectorsize(node_path):
    just_fdisk_op = subprocess.run(['fdisk', '-l', node_path], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
    (disk_length_in_bytes, lab1, disk_length_in_sectors, lab2) = just_fdisk_op.stdout.decode('UTF-8').split('\n')[0].split(' ')[-4:]
    disk_id = [r for r in just_fdisk_op.stdout.decode('UTF-8').split('\n') if ': 0x' in r][0].split(' ')[-1]
    del lab1, lab2
    sector_size = int(disk_length_in_bytes) / int(disk_length_in_sectors)
    assert int(sector_size) == float(sector_size), "Sector size should be an integer. My disk-analyzing script appears to be broken."
    return (disk_id, int(disk_length_in_bytes), int(disk_length_in_sectors), int(sector_size))


def get_raw_json_record_from_sfdisk(node_path):

    sfdisk_output = subprocess.run(['sfdisk', '-J', node_path], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
    res = json.loads(sfdisk_output.stdout.decode('UTF-8'))
    return res


def get_list_of_all_disks():

    all_dev_entries = []
    with open('/proc/partitions', 'r') as f:
        s = f.read().split('\n')
        for r in [r.split(' ')[-1] for r in s]:
            pth = os.path.join('/dev/', r)
            if r != '' and os.path.exists(pth) and is_this_a_disk(pth):
                all_dev_entries.append(pth)
    return all_dev_entries


def add_useful_info_to_raw_json_record_from_sfdisk(node_path, json_rec):

    disk_id, node_size_in_bytes, node_size_in_sectors, sector_size = get_node_diskID_sizeB_sizeSecs_and_sectorsize(node_path)
    json_rec['partitiontable']['sector_size'] = sector_size
    json_rec['partitiontable']['size_in_bytes'] = node_size_in_bytes
    json_rec['partitiontable']['size_in_sectors'] = node_size_in_sectors
    json_rec['partitiontable']['node'] = node_path
    json_rec['partitiontable']['disk_label'] = json_rec['partitiontable']['label']
    del json_rec['partitiontable']['label']
    json_rec['partitiontable']['disk_id'] = disk_id
    for i in ('id', 'label', 'partuuid', 'path', 'uuid'):
        json_rec['partitiontable'][i] = get_altpath_from_node_path(node_path, i)
        for partition in json_rec['partitiontable']['partitions']:
            for i in ('id', 'label', 'partuuid', 'path', 'uuid'):
                partition[i] = get_altpath_from_node_path(node_path, i)
    return json_rec


def get_disk_record(node_path):

    if node_path in (None, '/', '') or not os.path.exists(node_path) or os.path.isdir(node_path):
        raise ValueError('Cannot get disk record -- %s not found', str(node_path))
    json_rec = get_raw_json_record_from_sfdisk(node_path)
    _ = add_useful_info_to_raw_json_record_from_sfdisk(node_path, json_rec)
    res = json.loads(json.dumps(json_rec), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return res


def get_disk_record_from_all_disks():
    disks = []
    for devpath in get_list_of_all_disks():
        disks.append(get_disk_record(devpath))
    return disks


class Disk:
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

    def __init__(self, node):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        # TODO: QQQ add locking
        self.__user_specified_node = os.path.realpath(node)
        if not is_this_a_disk(self.__user_specified_node):
            raise ValueError("Nope -- %s is not a disk" % self.__user_specified_node)
        self.__cache = None
        self.update()

    def __str__(self):
        return """Disk=%s node=%s  id=%s device=%s  unit=%s  partitions:%d""" % \
            (self.__user_specified_node, self._node, self._id, self._device, self._unit, len(self.partitions))

    def __repr__(self):
        return f'Disk(node="%s")' % self.node

    def partprobe(self):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        os.system("sync;sync;sync;partprobe %s;sync;sync;sync" % self.__user_specified_node)

    def update(self, partprobe=False):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
#        print("Initializing Disk(%s)" % self.__user_specified_node)
        if partprobe:
            self.partprobe()
        self.__cache = get_disk_record(self.__user_specified_node)
        self._id = self.__cache.partitiontable.id
        self._node = self.__cache.partitiontable.node
        self._device = self.__cache.partitiontable.device
        self._unit = self.__cache.partitiontable.unit
        self._disk_label = self.__cache.partitiontable.disk_label
        self._disk_id = self.__cache.partitiontable.disk_id
        self._sector_size = self.__cache.partitiontable.sector_size
        self._size_in_sectors = self.__cache.partitiontable.size_in_sectors
        self._partitions = []
#        print('==> node:', self.node)
        for p in self.__cache.partitiontable.partitions:
#            print('Initializing partition %s' % p.node)
            self.partitions.append(DiskPartition(p.node))
        if self.overlapping:
            print("Warning -- partitions in %s are overlapping" % self.node)
#        print("Finished initializing Disk(node=%s)" % self.node)

        # for p in self.__cache.partitiontable.partitions:
        #     for q in self.__cache.partitiontable.partitions:
        #         if p is not q and
    @property
    def disk_id(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._disk_id

    @disk_id.setter
    def disk_id(self, value):
        _ = int(value, 16)
        if len(value) != 10 or value[:2] != '0x':
            raise ValueError("%s is an invalid disk id string" % value)
        try:
            set_disk_id(self.node, value)
        finally:
            self.update()
        assert(self._disk_id == value)

    @disk_id.deleter
    def disk_id(self):
        raise AttributeError("Not permitted")

    @property
    def disk_label(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._disk_label

    @disk_label.setter
    def disk_label(self, value):
        raise AttributeError("Not permitted")

    @disk_label.deleter
    def disk_label(self):
        raise AttributeError("Not permitted")

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
    def id(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("Not permitted")

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def unit(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._unit

    @unit.setter
    def unit(self, value):
        raise AttributeError("Not permitted")

    @unit.deleter
    def unit(self):
        raise AttributeError("Not permitted")

    @property
    def device(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._device

    @device.setter
    def device(self, value):
        raise AttributeError("Not permitted")

    @device.deleter
    def device(self):
        raise AttributeError("Not permitted")

    @property
    def partitions(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._partitions

    @partitions.setter
    def partitions(self, value):
        raise AttributeError("Not permitted")

    @partitions.deleter
    def partitions(self):
        raise AttributeError("Not permitted")

    @property
    def sector_size(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._sector_size

    @sector_size.setter
    def sector_size(self, value):
        raise AttributeError("Not permitted")

    @sector_size.deleter
    def sector_size(self):
        raise AttributeError("Not permitted")

    @property
    def size_in_sectors(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        return self._size_in_sectors

    @size_in_sectors.setter
    def size_in_sectors(self, value):
        raise AttributeError("Not permitted")

    @size_in_sectors.deleter
    def size_in_sectors(self):
        raise AttributeError("Not permitted")

    @property
    def overlapping(self):
        """:obj:`list` of :obj:`str`: Properties with both a getter and setter
        should only be documented in their getter method.

        If the setter method contains notable behavior, it should be
        mentioned here.
        """
        for p_prev in self.partitions:
            for p_next in self.partitions:
                if p_prev.start < p_next.start \
                and p_prev.end >= p_next.start \
                and p_prev.fstype != _FS_EXTENDED \
                and p_next.fstype != _FS_EXTENDED:
                    return True
        return False

    @overlapping.setter
    def overlapping(self, value):
        raise AttributeError("Not permitted")

    @overlapping.deleter
    def overlapping(self):
        raise AttributeError("Not permitted")

    def add_partition(self, partno=None, start=None, end=None, fstype=_FS_DEFAULT, debug=False, size_in_MiB=None):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        if end is not None and size_in_MiB is not None:
            raise ValueError("Specify either end=... or size_in_MIB... but don't specify both")
        if partno is None:
            if len(self.partitions) == 0:
                partno = 1
            else:
                partno = max([r.partno for r in self.partitions]) + 1
        if partno < 1 or partno > 63:
            raise ValueError("The specified partno %d is too low/high" % partno)
        if partno in [r.partno for r in self.partitions]:
            raise ValueError("Partition %d exists already. I cannot create two of them." % partno)
        if partno >= 5:
            pass
        else:
            if start is None and partno > 1:
                try:
                    start = [r for r in self.partitions if r.partno == partno - 1][0].end + 1
                except IndexError:
                    raise ValueError("Please specify start sector of partition #%d of %s" % (partno, self.node))
            if end is None and size_in_MiB is None:
                try:
                    end = [r for r in self.partitions if r.partno == partno + 1][0].start - 1
                except IndexError:
                    pass
        try:
            add_partition(self.node, partno=partno, start=start, end=end, fstype=fstype, debug=debug, size_in_MiB=size_in_MiB)
            self.update()
            if self.overlapping:
                delete_partition(self.node, partno)
                raise PartitionCreationError("Refusing to create partition #%d for %s -- it would overlap with another partition" % (partno, self.node))
        finally:
            self.update(partprobe=True)
        if not was_this_partition_created(self.node, partno):
            raise PartitionCreationError("Failed to create partition #%d for %s" % (partno, self.node))

    def delete_all_partitions(self):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        delete_all_partitions(self.node)
        self.update(partprobe=True)

    def delete_partition(self, partno, update=True):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        if was_this_partition_created(self.node, partno):
#            print("Deleting partition #%d from %s" % (partno, self.node))
            try:
                delete_partition(self.node, partno)
            finally:
                self.update(partprobe=update)
        else:
#            raise PartitionDeletionError("Failed to delete #%d from %s" % (partno, self.node)))
            print("No need to delete partition #%d from %s --- that partition does not exist" % (partno, self.node))

    def dump(self):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        outtxt = '''label: {disk_label}
label-id: {disk_id}
device: {node}
unit: sectors

'''.format(disk_label=self.disk_label, disk_id=self.disk_id,
                     node=self.node)
        for p in self.partitions:
            outtxt += '''%-10s: start=%12d, size=%12d, fstype=%s
''' % (p.node, p.start, p.size, p.fstype)
        return outtxt
