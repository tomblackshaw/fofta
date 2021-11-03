# -*- coding: utf-8 -*-
"""my.disktools.partitions

Functions and classes that operate on partitions (not disks).

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains functions that deal with partitions: creating them,
deleting them, scanning their attributes, changing their attributes, and
wrapping them in instances of the Partition class.

Example:
    p = Partition('/dev/sda1')

Disk() is not threadsafe, but threadsafeDisk() is.

Attributes:

    _FS_DEFAULT (:obj:`str`): The two- or three-char code that fdisk utilizes
        to indicate an ext4fs partition.

    _FS_EXTENDED (:obj:`str`): The two- or three-char code that fdisk utilizes
        to indicate an external partition.
        
Todo:
    * Better TODO lists
    * Replace os.system() with call_binary()

# TODO: Replace os.system() with call_binary()

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from collections import namedtuple
import json
import os
import string

from my.disktools.both import devdiskbyxxxx_path
from my.exceptions import (
    StartEndAssBackwardsError,
    PartitionWasNotCreatedError,
    MissingPriorPartitionError,
    PartitionsOverlapError,
    PartitionDeletionError,
    ExistentPriorPartitionError,
    PartitionAttributeWriteFailureError,
    PartitionAttributeReadFailureError,
    PartitionTableReorderingError,
)
from my.globals import call_binary, pause_until_true
import subprocess
import time


_FS_EXTENDED = "5"
_FS_DEFAULT = "83"


class DiskPartition:
    """This class wraps around a specified partition disk_path (a /dev entry).

    You pass me a /dev entry; the resultant class instance will make it
    easy for you to retrieve information about the specified partition.
    DiskPartition is not threadsafe.

    Args:
        node (:obj:`str`): The /dev entry of the partition in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdXNN
            or /dev/mmcblkXpNN) and use that as my node path.

    Returns:
        DiskPartition if successful; else, raise an exception.
        bool: True if successful, False otherwise.

    Raises:
        AttributeError: You attempted to write a readonly attribute, read
            something that's unreadable, or do something equally silly).
        ValueError: If `param2` is equal to `param1`.

    Todo:
        * Add more TODOs
        * Add read- and write-locking

    """

    def __init__(self, node):
        self._user_specified_node = node
        self._node = os.path.realpath(self._user_specified_node)
        self.__cache = None
        self.update()
        if self.parentnode is None:
            raise ValueError(
                "%s does not belong to any disk" % self._user_specified_node
            )

    def __repr__(self):
        return f'DiskPartition(node="%s")' % self.node

    def __str__(self):
        return (
            """node=%s partno=%d parentnode=%s start=%d size=%d fstype=%s label=%s partuuid=%s path=%s uuid=%s"""
            % (
                self.node,
                self.partno,
                self.parentnode,
                self.start,
                self.size,
                self.fstype,
                self.label,
                self.partuuid,
                self.path,
                self.uuid,
            )
        )

    def update(self):
        """Update the fields by reading sfdisk's output and processing it."""
        self.__cache = partition_namedtuple(self.node)
        self._start = self.__cache.start
        self._size = self.__cache.size
        self._fstype = self.__cache.type
        self._id = devdiskbyxxxx_path(self.node, "id")  # self.__cache.id
        self._label = devdiskbyxxxx_path(self.node, "label")  # etc.
        self._partuuid = devdiskbyxxxx_path(self.node, "partuuid")
        self._path = devdiskbyxxxx_path(self.node, "path")
        self._uuid = devdiskbyxxxx_path(self.node, "uuid")

    @property
    def node(self):
        """:obj:`str`: The /dev path of this partition."""
        return self._node

    @node.setter
    def node(self, value):
        raise AttributeError("Not permitted")

    @node.deleter
    def node(self):
        raise AttributeError("Not permitted")

    @property
    def parentnode(self):
        """str: The disk to which I belong. This is a class instance."""
        if not os.path.exists(self.node):
            raise AttributeError("%s does not exist" % self.node)
        from my.disktools.disks import namedtuples_for_all_disks

        for d in namedtuples_for_all_disks():
            for p in d.partitiontable.partitions:
                if self.node in partition_paths(p):
                    return d.partitiontable.node
        return None

    @parentnode.setter
    def parentnode(self, value):
        raise AttributeError("Not permitted")

    @parentnode.deleter
    def parentnode(self):
        raise AttributeError("Not permitted")

    @property
    def partno(self):
        """int: My partition# in the disk to which I belong."""
        n = deduce_partno(self.node)
        return n

    @partno.setter
    def partno(self, value):
        raise AttributeError("Not permitted")

    @partno.deleter
    def partno(self):
        raise AttributeError("Not permitted")

    @property
    def start(self):
        """int: first sector# of this partition."""
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @start.deleter
    def start(self):
        raise AttributeError("Not permitted")

    @property
    def end(self):
        """int: final sector# of this partition."""
        return self._start + self._size - 1

    @end.setter
    def end(self, value):
        raise AttributeError("Not permitted")

    @end.deleter
    def end(self):
        raise AttributeError("Not permitted")

    @property
    def size(self):
        """int: Size of this partition, in sectors."""
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @size.deleter
    def size(self):
        raise AttributeError("Not permitted")

    @property
    def fstype(self):
        """:obj:`str`: Filesystem code, e.g. 83, 5, 82, ..."""
        return self._fstype

    @fstype.setter
    def fstype(self, value):
        self._fstype = value

    @fstype.deleter
    def fstype(self):
        raise AttributeError("Not permitted")

    @property
    def id(self):
        """:obj:`str`: id."""
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def label(self):
        """:obj:`str`: label."""
        return self._label

    @label.setter
    def label(self, value):
        raise AttributeError("Not permitted")

    @label.deleter
    def label(self):
        raise AttributeError("Not permitted")

    @property
    def partuuid(self):
        """:obj:`str`: partuuid."""
        return self._partuuid

    @partuuid.setter
    def partuuid(self, value):
        raise AttributeError("Not permitted")

    @partuuid.deleter
    def partuuid(self):
        raise AttributeError("Not permitted")

    @property
    def uuid(self):
        """:obj:`str`: uuid."""

        return self._uuid

    @uuid.setter
    def uuid(self, value):
        raise AttributeError("Not permitted")

    @uuid.deleter
    def uuid(self):
        raise AttributeError("Not permitted")

    @property
    def path(self):
        """:obj:`str`: path."""

        return self._path

    @path.setter
    def path(self, value):
        raise AttributeError("Not permitted")

    @path.deleter
    def path(self):
        raise AttributeError("Not permitted")


def deduce_partno(partition_path):
    """Deduce the partition# from the supplied /dev partition entry.

    Note:
        None.

    Args:
        partition_path (:obj:`str`): The /dev entry (e.g. /dev/sda1) of the partition.

    Returns:
        int: Partition# of the specified partition (e.g. 1 if /dev/sda1).

    """
    if (
        partition_path in (None, "")
        or os.path.isdir(partition_path)
        or not partition_path.startswith("/dev/")
        or partition_path == "/dev/"
    ):
        raise ValueError("partition_path %s is a silly value" % str(partition_path))
    try:
        s = partition_path.split("/")[-1]
        i = len(s) - 1
        while i >= 0 and s[i].isdigit():
            i = i - 1
        return int(s[i + 1 :])
    except (AttributeError, ValueError):
        return ""


def overlapping(disk_path, hypothetically=None):
    """Are two or more partitions overlapping on the specified disk?

    Examing the specified disk. If its partitions are overlapping, *or* if
    the hypothetical modification would cause an overlap, return True.
    Else, return False.

    Note:
        This isn't perfect. It's good but it's not perfect.

    Args:
        disk_path (:obj:`str`): The /dev entry (e.g. /dev/sda1) of the disk.
        hypothetically ([partno,start,end,fstype], optional): The proposed
            modification to the parton table. If such a modification would
            cause an overlap then return True, as if such an overlap already
            existed.

    Returns:
        True if overap is/would be, False otherwise.

    """
    from my.disktools.disks import disk_namedtuple

    rec = disk_namedtuple(disk_path)
    partitions_data_lst = []
    for partrec in rec.partitiontable.partitions:
        p = DiskPartition(partrec.node)
        partitions_data_lst.append([p.partno, p.start, p.end, p.fstype])
    if len(partitions_data_lst) <= (0 if hypothetically else 1):
        return False
    if hypothetically:
        hypo_partno, hypo_start, hypo_end, hypo_fstype = hypothetically
        if hypo_partno is None:
            hypo_partno = partitions_data_lst[-1][0] + 1
        if hypo_start is None:
            hypo_start = partitions_data_lst[-1][2] + 1
        if hypo_end is None:
            hypo_end = hypo_start + 99999999
        partitions_data_lst.append([hypo_partno, hypo_start, hypo_end, hypo_fstype])
    for a in range(0, len(partitions_data_lst)):
        partnoA, startA, endA, fstypeA = partitions_data_lst[a]
        for b in range(0, len(partitions_data_lst)):
            partnoB, startB, endB, fstypeB = partitions_data_lst[b]
            if (
                a != b
                and startA <= endB
                and endA >= startB
                and fstypeA != _FS_EXTENDED
                and fstypeB != _FS_EXTENDED
            ):
                return True
    del partnoA, partnoB
    return False


def delete_all_partitions(partition_path):
    """Delete all partitions from specified disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.

    Returns:
        None.

    Raises:
        PartitionDeletionError: Failed to delete partition `disk_path`.

    """
    realpartition_path = os.path.realpath(partition_path) 
    os.system(
        """sfdisk -d {partition_path}| grep -vx "{partition_path}.*[0-9] : .*"| sfdisk -f {partition_path} 2>/dev/null >/dev/null""".format(
            partition_path=realpartition_path
        )
    )
    call_binary(['partprobe',realpartition_path])


def NEW_partition_exists(disk_path, partno):
    """Does this partno# exist on this disk?

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.

    Returns:
        True if `disk_path` exists, False if it doesn't.

    """
    if not os.path.exists(disk_path):
        raise FileNotFoundError("Disk %s not found" % disk_path)
    disk_path = os.path.realpath(disk_path)
    for t in ' ' + string.ascii_lowercase:
        dev_str = ('%s%s%d' % (disk_path, t, partno)).replace(' ','')
#        print(dev_str)
        if os.path.exists(dev_str):
            return True
    return False        


def partition_exists(disk_path, partno):
    """Does this partno# exist on this disk?

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.

    Returns:
        True if partition exists, False if it doesn't.

    """
    disk_path = os.path.realpath(disk_path)
#     res, __, ___ = call_binary(['bash','-c', '''
# disk_path=%s
# partno=%d
# fullpartitiondev=$(sfdisk -d $disk_path | grep -x "$disk_path.*$partno :.*" | head -n1 | cut -d' ' -f1)
# [ -e "$fullpartitiondev" ] && exit 0 || exit 1
#     '''% (disk_path, partno)])
    res = os.system('''
disk_path=%s
partno=%d
fullpartitiondev=$(sfdisk -d $disk_path | grep -x "$disk_path.*$partno :.*" | head -n1 | cut -d' ' -f1)
[    ''' % (disk_path, partno)) 
 TODO: Replace os.system() with call_binary()
    # if resA != resB:
    #     raise SystemError( "resA and resB differ. You suck at programming.")
    if res == 0:
        return True
    else:
        return False
    
    

def get_partition_fstype(disk_path, partno):
    """Get partition type -- '83', '5', ...? -- of partno# of the disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.

    Returns:
        :obj:`str`: What was found.

    """
    from my.disktools.disks import is_this_a_disk

    if not is_this_a_disk(disk_path):
        raise ValueError(
            "{disk_path} is not a disk. Please specify a disk.".format(
                disk_path=disk_path
            )
        )
    return get_disk_partition_field_value(disk_path, partno, 2)


def get_disk_partition_table(disk_path):
    """Get sfdisk's (std)output for the specified disk_path string.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.

    Returns:
        :obj:`str`: The partition table.

    Raises:
        PartitionAttributeReadFailureError: Failed to read the partition table.

    """
    disk_path = os.path.realpath(disk_path)
    retcode, stdout_txt, stderr_txt = call_binary(
        param_lst=["sfdisk", "-d", disk_path], input_str=None
    )
    if retcode != 0:
        # print(stderr_txt)
        raise PartitionAttributeReadFailureError(
            "Unable to retrieve disk partitiontable of %s" % disk_path
        )
    return stdout_txt


def get_disk_partition_table_line(disk_path, partno):
    """Get sfdisk's (std)output for a partition on the specified disk.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.

    Returns:
        :obj:`str`: What was found.

    Raises:
        PartitionAttributeReadFailureError: Failed to read the line from the partition table.

    """
    sfdisk_op_text_lst = get_disk_partition_table(disk_path).split("\n")
    try:
        sfdisk_op_line_number = [
            i
            for i in range(len(sfdisk_op_text_lst))
            if sfdisk_op_text_lst[i].startswith(disk_path)
            and sfdisk_op_text_lst[i].find("%d : " % partno) >= 0
        ][0]
    except IndexError:
        raise PartitionAttributeReadFailureError(
            "Failed to retrieve info on partition#%d from %s" % (partno, disk_path)
        )
    return sfdisk_op_text_lst[sfdisk_op_line_number]


def get_disk_partition_field_value(disk_path, partno, fieldno):
    """Get sfdisk's (std)output for a field of a partition from a disk.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.
        fieldno (int): The field#. Probably 0, 1, or 2 (start, size, type).

    Returns:
        :obj:`str`: What was found.

    Raises:
        None.

    """
    return (
        get_disk_partition_table_line(disk_path, partno)
        .split(",")[fieldno]
        .split("=")[-1]
        .strip()
    )


def set_disk_partition_field_value(disk_path, partno, fieldno, newval):
    """Set a field of a partition of a disk, using sfdisk.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.
        fieldno (int): The field#. Probably 0, 1, or 2 (start, size, type).
        newval (str): The new value.

    Returns:
        None.

    Raises:
        None.

    """
    oldcurr_line = get_disk_partition_table_line(disk_path, partno)
    oldval = get_disk_partition_field_value(disk_path, partno, fieldno)
    itemno = 0
    dct = {}
    for this_pair in [
        r.split("=")
        for r in oldcurr_line.replace(" : ", " ,")
        .replace("/dev/", "node=/dev/")
        .split(",")
    ]:
        dct[itemno] = [this_pair[0].strip(), this_pair[1].strip()]
        itemno = itemno + 1
    if itemno != 4:
        raise SystemError(
            "I am unable to process the output of sfdisk. \
There is a strange number of fields in this line. \
disk_path=%s partno=%d fieldno=%d"
            % (disk_path, partno, fieldno)
        )
    dct[fieldno + 1][1] = newval
    newcurr_line = """%-10s: start=%12s, size=%12s, type=%s""" % (
        dct[0][1],
        dct[1][1],
        dct[2][1],
        dct[3][1],
    )
    old_txt = get_disk_partition_table(disk_path)
    new_txt = old_txt.replace(oldcurr_line, newcurr_line)
    retcode, stdout_txt, stderr_txt = call_binary(
        param_lst=["sfdisk", "-f", disk_path], input_str=new_txt
    )
    if retcode != 0:
        # print(stdout_txt)
        # print(stderr_txt)
        raise PartitionAttributeWriteFailureError(
            "Failed to change field {fieldno} of partno#{partno} of {disk_path} from {oldval} to {newval}".format(
                fieldno=fieldno,
                partno=partno,
                disk_path=disk_path,
                oldval=oldval,
                newval=newval,
            )
        )


def set_partition_fstype(disk_path, partno, fstype):
    """Set partition type -- '83', '5', ...? -- of partno# of the disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.
        fstype (:obj:`str`): The string (e.g. '5', '83') for the type
            of the filesystem.

    Returns:
        None.

    """
    try:
        set_disk_partition_field_value(disk_path, partno, 2, fstype)
    except PartitionTableReorderingError:
        raise PartitionAttributeWriteFailureError(
            "Unable to change fstype of partno#{partno} of {disk_path}".format(
                partno=partno, disk_path=disk_path
            )
        )


def add_partition_SUB(
    disk_path,
    partno,
    start,
    end,
    fstype,
    with_partno_Q=True,
    size_in_MiB=None,
    debug=False,
):
    """Low-level subreoutine to add partition to specified disk.

    Note:
        Do not call me. Call add_partition() instead.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int, optional): The partition#. If it is unspecified, the
            next one will be used. For example, if the last partition is #2,
            then #3 will be the new partition's number.
        start (int): The first sector of the partition.
        end (int, optional): The final cylinder of the partition. If it is
            unspecified, the last possible cylinder on the disk.
        fstype (:obj:`str`, optional): The hex code for fdisk to set the
            filesystem type, broadly speaking. The default is probably 83.
        size_in_MiB (int, optional): The size of the partition in mibibibbly
            whatever.

    Returns:
        None.

    Raises:
        ValueError: Bad parameters supplied.

    """
    disk_path = os.path.realpath(disk_path)
    res = 0
    if debug:
        print(
            "add_partition_SUB() -- disk_path=%s; partno=%s; start=%s; end=%s; size_in_MiB=%s"
            % (str(disk_path), str(partno), str(start), str(end), str(size_in_MiB))
        )
    if end is not None and size_in_MiB is not None:
        raise ValueError(
            "Specify either end=... or size_in_MIB... but don't specify both"
        )
    elif end is None and size_in_MiB is not None:
        end_str = "+%dM" % size_in_MiB
    elif end is not None and size_in_MiB is None:
        end_str = "%d" % end
    else:
        end_str = None
    if debug:
        print("end_str is", end_str)
        debug_str = ""
    else:
        debug_str = " >/dev/null 2>/dev/null"
    if with_partno_Q: # TODO: Replace os.system() with call_binary()
        res = os.system(
            """echo "p\nn\n%s\n%s\n%s\n%s\nw" | fdisk %s %s"""
            % (
                "e" if fstype == _FS_EXTENDED else "l" if partno >= 5 else "p",
                "" if not partno else str(partno),
                "" if not start else str(start),
                "" if not end_str else end_str,
                disk_path,
                debug_str,
            )# TODO: Replace os.system() with call_binary()
        )
    else:
        res = os.system(
            """echo "p\nn\n%s\n%s\n%s\nw" | fdisk %s %s"""
            % (
                "e" if fstype == _FS_EXTENDED else "l" if partno >= 5 else "p",
                "" if not start else str(start),
                "" if not end_str else end_str,
                disk_path,
                debug_str,
            )# TODO: Replace os.system() with call_binary()
        )
    call_binary(['partprobe',disk_path])
    res += os.system(
        """sfdisk --part-type {disk_path} {partno} {fstype} {debug}""".format(
            disk_path=disk_path,
            partno=partno,
            fstype=fstype,
            debug="" if debug else "> /dev/null 2> /dev/null",
        )# TODO: Replace os.system() with call_binary()
    )
    return res


def add_partition(
    disk_path, partno, start, end=None, fstype=None, debug=False, size_in_MiB=None
):
    """Add a partition to the specified disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int, optional): The partition#. If it is unspecified, the
            next one will be used. For example, if the last partition is #2,
            then #3 will be the new partition's number.
        start (int): The first sector of the partition.
        end (int, optional): The final cylinder of the partition. If it is
            unspecified, the last possible cylinder on the disk.
        fstype (:obj:`str`, optional): The hex code for fdisk to set the
            filesystem type, broadly speaking. The default is probably 83.
        size_in_MiB (int, optional): The size of the partition in mibibibbly
            whatever.

    Returns:
        None.

    Raises:
        PartitionsOverlapError: Partitions overlap (or would overlap).
        StartEndAssBackwardsError: The start and end numbers are backwards.
        MissingPriorPartitionError: We can't create #N if #(N-1) is missing.
        ExistantPriorPartitionError: We can't create an existing partition.
        PartitionWasNotCreatedError: Creation of the partition failed.

    """
    if overlapping(disk_path):
        raise PartitionsOverlapError(
            "I cannot create a new partition until you've fixed the overlapping old ones."
        )
    if end is not None and size_in_MiB is not None:
        raise ValueError(
            "Specify either end=... or size_in_MIB... but don't specify both"
        )
    if fstype is None:
        fstype = _FS_DEFAULT
    disk_path = os.path.realpath(disk_path)
    if debug:
        print(
            "add_partition() -- disk_path=%s; partno=%s; start=%s; end=%s; fstype=%s; size_in_MiB=%s"
            % (
                str(disk_path),
                str(partno),
                str(start),
                str(end),
                fstype,
                str(size_in_MiB),
            )
        )
    if end is not None and start is not None and end <= start:
        raise StartEndAssBackwardsError("The partition must end after it starts")
    res = 0
    if overlapping(disk_path, [partno, start, end, fstype]):
        raise PartitionsOverlapError(
            "We would overlap if we tried to make this partition"
        )
    if partno in (1, 5):
        res = add_partition_SUB(
            disk_path,
            partno,
            start,
            end,
            fstype,
            with_partno_Q=False,
            debug=debug,
            size_in_MiB=size_in_MiB,
        )
        if not partition_exists(disk_path, partno):
            res = add_partition_SUB(
                disk_path,
                partno,
                start,
                end,
                fstype,
                debug=debug,
                size_in_MiB=size_in_MiB,
            )
    elif partno > 5 and not partition_exists(disk_path, partno - 1):
        raise MissingPriorPartitionError(
            "Because partition #%d of %s does not exist, I cannot create #%d. Logical partitions cannot be added without screwing up their order. Sorry."
            % (partno - 1, disk_path, partno)
        )
    elif partition_exists(disk_path, partno):
        raise ExistentPriorPartitionError(
            "Partition #%d of %s already exists" % (partno, disk_path)
        )
    else:
        res = add_partition_SUB(
            disk_path, partno, start, end, fstype, debug=debug, size_in_MiB=size_in_MiB
        )
    try:
        pause_until_true(timeout=15, test_func=(lambda x=disk_path, y=partno: partition_exists(x,y)),
                                      nudge_func=(lambda x=disk_path: call_binary(['partprobe', x])))
    except TimeoutError:
        raise PartitionWasNotCreatedError(
            "Failed to add partition #{partno} to {disk_path} (res={res})".format(
                partno=partno, disk_path=disk_path, res=res)
            )
    del res
    return 0  # Throw away res if the partition was successfully created


def partition_paths(partition):
    """Get a list of all potential nodenames (/dev/.../etc.) for this partition.

    A subroutine calls me, supplies a Partition() class instance, and asks me
    to provide a list of all /dev links+nodes associated with this partition.

    Example:
        Ask partition_paths() for a list of paths associated with /dev/sda1::

            $ partition = DiskPartition('/dev/sda')
            $ partition_paths(partition)
            ['/dev/sda1', '/dev/disk/by-partuuid/1234abcd-01',
            '/dev/disk/by-uuid/2bcf1a74-0d10-4edd-ac70-30892798ecfc',
            '/dev/disk/by-label/MY_LAB84',
            '/dev/disk/by-path/platform-xhci-hcd.0.auto-usb-0:1:1.0-scsi-0:0:0:0-part1']

    Note:
        None.

    Args:
        partition (DiskPartition): The disk partition in question.

    Returns:
        List of strings: All applicable /dev paths.

    Raises:
        None.

    """
    lst = []
    for i in (
        partition.node,
        partition.partuuid,
        partition.uuid,
        partition.label,
        partition.path,
    ):
        if i not in (None, ""):
            lst.append(i)
    return lst


def partition_namedtuple(node):
    """Use sfdisk to get info; enhance it w/ more info; return it as a namedtiple.

    The specified node, a /dev string, will be sent to sfdisk, fdisk, etc. and
    so on. The result is stored in a JSON quasi-dictionary. Then, it is turned
    into a namedtuple and returned by me.

    Example:
        Ask partition_paths() for an enhanced amedtuple associated with /dev/sda1::

            $ node = '/dev/sda1'
            $ t = partition_namedtuple(node)
            $ t
            X(node='/dev/sda1', start=2048, size=125040640, type='83',
                id=None, label=None, partuuid=None, path=None, uuid=None)

    Note:
        None.

    Args:
        node (str): The path of the partition in question.

    Returns:
        namedtuple: A sfdisk/fdisk-derived namedtuple of the partition in question.

    Raises:
        ValueError: Path doesn't exist.

    """
    if not os.path.exists(node):
        raise ValueError("Partition devpath %s does not exist" % node)
    from my.disktools.disks import (
        all_disk_paths,
        enhance_the_sfdisk_output,
        sfdisk_output,
    )

    for this_disk_path in all_disk_paths():
        json_rec = sfdisk_output(this_disk_path)
        # Changes are saved to json_rec
        _ = enhance_the_sfdisk_output(this_disk_path, json_rec)
        rec = json.loads(
            json.dumps(json_rec),
            object_hook=lambda d: namedtuple("X", d.keys())(*d.values()),
        )
        for p in rec.partitiontable.partitions:
            if node in partition_paths(p):
                return p
    return None


def delete_partition(disk_path, partno):
    """Delete the specified partition from the specified disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int, optional): The partition#. If it is unspecified, the
            next one will be used. For example, if the last partition is #2,
            then #3 will be the new partition's number.

    Returns:
        None.

    Raises:
        PartitionDeletionError: Failed to delete partition.

    """
    if partno >= 5 and partition_exists(disk_path, partno + 1):
        raise PartitionDeletionError(
            "Because partition #%d of %s exists, I cannot delete #%d. \
Logical partitions cannot be removed without screwing up their order. \
Sorry."
            % (partno + 1, disk_path, partno)
        )
    res =    )
l 2> /dev/null""" % (disk_path, partno)
    )# TODO: Replace os.system() with call_binary()
    try:
        pause_until_true(timeout=15, test_func=(lambda x=disk_path, y=partno: not partition_exists(x,y)),
                                      nudge_func=(lambda x=disk_path: call_binary(['partprobe', x])))
    except TimeoutError:
        raise PartitionDeletionError(
            "Failed to delete partition #{partno} to {disk_path}".format(
                partno=partno, disk_path=disk_path
            )
        )
    del res
    return 0  # Throw away res if the partition was successfully deleted
