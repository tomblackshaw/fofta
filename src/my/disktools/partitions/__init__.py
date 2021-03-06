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

    # _DOS_DEFAULT (:obj:`str`): The two- or three-char code that fdisk utilizes
    #     to indicate an ext4fs partition.
    #
    # _DOS_EXTENDED (:obj:`str`): The two- or three-char code that fdisk utilizes
    #     to indicate an external partition.
        
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
from my.globals import call_binary, pause_until_true, _DOS_DEFAULT, _DOS_EXTENDED, _GPT_DEFAULT,\
    _DOS
import subprocess
import time
import sys




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
        self.update()
        if self.parentnode is None:
            raise ValueError(
                "%s does not belong to any disk" % self._user_specified_node
            )

    def __repr__(self):
        return 'DiskPartition(node="%s")' % self.node

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
        self._cache = partition_namedtuple(self.node)
        self._start = self._cache.start  
        self._size = self._cache.size
        self._fstype = self._cache.type
        self._myid = devdiskbyxxxx_path(self.node, "id")  if self.isdev else None
        self._label = devdiskbyxxxx_path(self.node, "label")  if self.isdev else None
        self._partuuid =devdiskbyxxxx_path(self.node, "partuuid") if self.isdev else None
        self._path = devdiskbyxxxx_path(self.node, "path") if self.isdev else None
        self._uuid = devdiskbyxxxx_path(self.node, "uuid") if self.isdev else None

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
    def isdev(self):
        """:obj:`str`: The /dev path of this partition."""
        return True if self.node.startswith("/dev/") else False

    @isdev.setter
    def isdev(self, value):
        raise AttributeError("Not permitted")

    @isdev.deleter
    def isdev(self):
        raise AttributeError("Not permitted")
    
    @property
    def parentnode(self):
        """str: The disk to which I belong."""
        from my.disktools.disks import namedtuples_for_all_disks
        if not self.isdev:
            return self.node.rstrip('01234567890')
        else:
            if not os.path.exists(self.node):
                raise AttributeError("%s does not exist" % self.node)
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
    def myid(self):
        """:obj:`str`: id."""
        return self._myid

    @myid.setter
    def myid(self, value):
        self._myid = value

    @myid.deleter
    def myid(self):
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
        or (not partition_path.startswith("/dev/") and not os.path.exists(partition_path) and not os.path.exists(partition_path.rstrip('01234567890')))
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
                and fstypeA != _DOS_EXTENDED
                and fstypeB != _DOS_EXTENDED
            ):
                return True # FIXME: Test w/ GPT partitiontable 
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


def partition_exists(disk_path, partno):
    """Does this partno# exist on this disk?

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk or file in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path. Or, it may
            be /root/image.img or whatnot.
        partno (int): The partition#.

    Returns:
        True if `disk_path` exists, False if it doesn't.

    """
    _retcode, stdout_txt, _stderr_txt = call_binary(['sfdisk','-d',disk_path])
#    if _retcode == 0:
    relevant_lines = [r for r in stdout_txt.split('\n') if r.find(disk_path)==0 and len(disk_path) <= r.find('%d :'%partno) <= len(disk_path)+5]
    if relevant_lines not in (None, []):
#        relevant_line = relevant_lines[0]
#        print("disk %s partno %d ==> %s" % (disk_path, partno, relevant_line.split(' ')[0]))
        return True
    return False


def OLD_BUT_GOOD_partition_exists(disk_path, partno):
    disk_path = os.path.realpath(disk_path)
    res = os.system('''
disk_path=%s
partno=%d
fullpartitiondev=$(sfdisk -d $disk_path | grep -x "$disk_path.*$partno :.*" | head -n1 | cut -d' ' -f1)
[ -e "$fullpartitiondev" ] && exit 0 || exit 1
    ''' % (disk_path, partno)) 
    if res == 0:
        return True
    else:
        return False
    
    

def get_partition_fstype(disk_path, partno):
    """Get partition type of partno# of the disk.

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
        :obj:`str`: What was found: _DOS_DEFAULT, _DOS_EXTENDED, or
            GPT-compatible hyphenated hex string.

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
    retcode, stdout_txt, _stderr_txt = call_binary(
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
    except IndexError as e:
        raise PartitionAttributeReadFailureError(
            "Failed to retrieve info on partition#%d from %s" % (partno, disk_path)
        ) from e
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
    retcode, _stdout_txt, _stderr_txt = call_binary(
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
    """Set partition type -- _DOS_EXTENDED, _DOS_DEFAULT, ...? -- of partno# of the disk.

    Note:
        None.

    Args:
        disk_path (:obj:`str`): The /dev entry of the disk in
            question. This may be almost any /dev entry (including
            softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
            but I'll always deduce the real entry (probably /dev/sdX
            or /dev/mmcblkN) and use that as my node path.
        partno (int): The partition#.
        fstype (:obj:`str`): The string (e.g. _DOS_EXTENDED, _DOS_DEFAULT, or
            a GPT-compatible hyphenated hexstring) for the type of the filesystem.

    Returns:
        None.

    """
    try:
        set_disk_partition_field_value(disk_path, partno, 2, fstype)
    except PartitionTableReorderingError as e:
        raise PartitionAttributeWriteFailureError(
            "Unable to change fstype of partno#{partno} of {disk_path}".format(
                partno=partno, disk_path=disk_path
            )
        ) from e


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
    """Low-level subroutine to add partition to specified disk.

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
    if debug:
        sys.stderr.write(
            "add_partition_SUB() -- disk_path=%s; partno=%s; start=%s; end=%s; size_in_MiB=%s\n"
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
        sys.stderr.write("end_str is" + end_str + "\n")
        debug_str = ""
    else:
        debug_str = " >/dev/null 2>/dev/null"
    from my.disktools.disks import get_partitiontable_type
    partitiontable_type = get_partitiontable_type(disk_path)
    if fstype is None and partitiontable_type == 'dos':
        fstype = _DOS_DEFAULT
    res = os.system(
            """echo "p\nn\n{kind_of_partition}{partno}{start}{end}w" | fdisk {disk_path} {debug_str}""".format(
                kind_of_partition="e\n" if fstype == _DOS_EXTENDED else "l\n" if partno >= 5 else "p\n" if partitiontable_type == _DOS else "",
                partno="" if not with_partno_Q else ("%s\n" % ('' if partno is None else str(partno))),
                start="%s\n" % ('' if start is None else str(start)),
                end="%s\n" % ('' if end_str is None else str(end_str)),
                disk_path=disk_path,
                debug_str=debug_str
                )
        )
    call_binary(['partprobe',disk_path])
    if fstype == None:
        pass
    elif partitiontable_type == _DOS:
        res += os.system(
            """sfdisk --part-type {disk_path} {partno} {fstype} {debug}""".format(
                disk_path=disk_path,
                partno=partno,
                fstype=fstype,
                debug="" if debug else "> /dev/null 2> /dev/null",
            )
        )
    else:
        sys.stderr.write("Ignoring fstype {fstype} because this is a {partitiontable_type} partitiontable\r".format(fstype=fstype, partitiontable_type=partitiontable_type))
    return res




# def add_partition_SUB(
#     disk_path,
#     partno,
#     start,
#     end,
#     fstype,
#     with_partno_Q=True,
#     size_in_MiB=None,
#     debug=False,
# ):
#     """Low-level subroutine to add partition to specified disk.
#
#     Note:
#         Do not call me. Call add_partition() instead.
#
#     Args:
#         disk_path (:obj:`str`): The /dev entry of the disk in
#             question. This may be almost any /dev entry (including
#             softlinks such as /dev/disk/by-{id,partuuid,label,...}/etc.),
#             but I'll always deduce the real entry (probably /dev/sdX
#             or /dev/mmcblkN) and use that as my node path.
#         partno (int): The partition#.
#         start (int): The first sector of the partition.
#         end (int): The final cylinder of the partition.
#         fstype (:obj:`str`): The hex code for fdisk to set the
#             filesystem type, broadly speaking.
#         size_in_MiB (int, optional): The size of the partition in mibibibbly
#             whatever.
#
#     Returns:
#         None.
#
#     Raises:
#         ValueError: Bad parameters supplied.
#
#     """
#     from my.disktools.disks import sfdisk_compatible_text_line
#     disk_path = os.path.realpath(disk_path)
#     if debug:
#         print(
#             "add_partition_SUB() -- disk_path=%s; partno=%s; start=%s; end=%s; size_in_MiB=%s"
#             % (str(disk_path), str(partno), str(start), str(end), str(size_in_MiB))
#         )
#     if end is not None and size_in_MiB is not None:
#         raise ValueError(
#             "Specify either end=... or size_in_MIB... but don't specify both"
#         )
#     from my.disktools.disks import Disk
#     d = Disk(disk_path)
#     sftxt = d.dump()
#     sftxt += sfdisk_compatible_text_line(node='{node}{ppp}{partno}'.format( 
#                                          node=d.node, ppp='p' if (d.node.startswith('/dev/loop')  or d.node.startswith('/dev/mmcblk')) else ''), 
#                                          start=start, size=end-start, fstype=fstype, partno=partno)
#     retcode, stdout_txt, stderr_txt = call_binary(['sfdisk','-a',d.node], sftxt)
#     call_binary(['partprobe',disk_path])
#     if debug is True and retcode != 0:
#         print("Warning --- failed to create partition")
#         print("stdout:", stdout_txt)
#         print("stderr:", stderr_txt)
#     return retcode
        


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
    from my.disktools.disks import get_partitiontable_type, disk_namedtuple, get_how_many_partitions
    if overlapping(disk_path):
        raise PartitionsOverlapError(
            "I cannot create a new partition until you've fixed the overlapping old ones."
        )
    if end is not None and size_in_MiB is not None:
        raise ValueError(
            "Specify either end=... or size_in_MIB... but don't specify both"
        )
    disk_path = os.path.realpath(disk_path)
    if debug:
        sys.stderr.write(
            "add_partition() -- disk_path=%s; partno=%s; start=%s; end=%s; fstype=%s; size_in_MiB=%s"
            % (
                str(disk_path),
                str(partno),
                str(start),
                str(end),
                str(fstype),
                str(size_in_MiB),
            )
        )
    partition_type = get_partitiontable_type(disk_path)
    if end is not None and start is not None and end <= start:
        raise StartEndAssBackwardsError("The partition must end after it starts")
    res = 0
    if overlapping(disk_path, [partno, start, end, fstype]):
        raise PartitionsOverlapError(
            "We would overlap if we tried to make this partition"
        )
    if (partition_type == _DOS and partno in (1, 5)):
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
    elif partition_type == _DOS and partno > 5 and not partition_exists(disk_path, partno - 1):
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
        pause_until_true(timeout=2, test_func=(lambda x=disk_path, y=partno: partition_exists(x,y)),
                                      nudge_func=(lambda x=disk_path: call_binary(['partprobe', x])))
    except TimeoutError as e:
        raise PartitionWasNotCreatedError(
            "Failed to add partition #{partno} to {disk_path} (res={res})".format(
                partno=partno, disk_path=disk_path, res=res)
            ) from e
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

    The specified node, a /dev string or image path, will be sent to sfdisk, 
    fdisk, etc. and so on. The result is stored in a JSON quasi-dictionary. Then,
    it is turned into a namedtuple and returned by me.

    Example:
        Ask partition_paths() for an enhanced amedtuple associated with /dev/sda1::

            $ node = '/dev/sda1'
            $ t = partition_namedtuple(node)
            $ t
            X(node='/dev/sda1', start=2048, size=125040640, type=_DOS_DEFAULT,
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
    res = dev_namedtuple(node) if node.startswith('/dev/') else image_namedtuple(node)
    if res is None:
        raise ValueError("Partition {node} cannot be found/analyzed".format(node=node))
    return res

def image_namedtuple(node):
    """Get info on partition (in disk image); enhance it w/ more info; return namedtiple."""
    if not os.path.isfile(os.path.realpath(node.rstrip('01234567890'))):
        raise ValueError("File %s does not list this partition" % node)
    imgfile = node.rstrip('01234567890')
    if not os.path.exists(imgfile):
        raise ValueError("File %s does not list this partition" % node)
    return find_matching_namedtuple(imgfile, node)


def dev_namedtuple(node):
    """Get info on partition (/dev entry); enhance it w/ more info; return namedtiple."""
    from my.disktools.disks import all_disk_paths
    if not os.path.exists(node):
        raise ValueError("Partition devpath %s does not exist" % node)
    for this_disk_path in all_disk_paths():
        res = find_matching_namedtuple(the_disk=this_disk_path, the_partition=node)
        if res is not None:
            return res
    return None



def find_matching_namedtuple(the_disk, the_partition):
    from my.disktools.disks import enhanced_sfdisk_output_rec
    rec = enhanced_sfdisk_output_rec(the_disk)
    for p in rec.partitiontable.partitions:
        if the_partition in partition_paths(p):
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
    from my.disktools.disks import get_partitiontable_type
    if get_partitiontable_type(disk_path) == _DOS and partno >= 5 and partition_exists(disk_path, partno + 1):
        raise PartitionDeletionError(
            "Because partition #%d of %s exists, I cannot delete #%d. \
Logical partitions cannot be removed without screwing up their order. \
Sorry."
            % (partno + 1, disk_path, partno)
        )
    res = os.system(
        """sfdisk %s --del %d > /dev/null 2> /dev/null""" % (disk_path, partno)
    )
    try:
        pause_until_true(timeout=5, test_func=(lambda x=disk_path, y=partno: not partition_exists(x,y)),
                                      nudge_func=(lambda x=disk_path: call_binary(['partprobe', x])))
    except TimeoutError as  e:
        raise PartitionDeletionError(
            "Failed to delete partition #{partno} to {disk_path}".format(
                partno=partno, disk_path=disk_path
            )
        ) from e
    del res
    return 0  # Throw away res if the partition was successfully deleted
