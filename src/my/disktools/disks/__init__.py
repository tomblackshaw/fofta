# -*- coding: utf-8 -*-
"""my.disktools.disks

Functions and classes that operate on disks (not partitions).

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains subroutines for viewing and modifying disks (but
not partitions themselves). In particular, it contains the Disk class,
which is used to control individual disks. The device's path is sent
as a parameter (e.g. /dev/sda) to the class instance creator.

Todo:
    * Add more TODOs

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from collections import namedtuple
import json
import os
import io
import subprocess

from my.disktools.both import devdiskbyxxxx_path
from my.disktools.partitions import deduce_partno, add_partition, _FS_EXTENDED
from my.exceptions import (
    PartitionsOverlapError,
    StartEndAssBackwardsError,
    MissingPriorPartitionError,
    PartitionWasNotCreatedError,
    DiskIDSettingFailureError,
    ExistentPriorPartitionError,
    WeNeedAnExtendedPartitionError,
    PartitionTableReorderingError,
)
from my.globals import call_binary
import threading

_disks_dct = {}
the_threadsafeDisk_lock = threading.Lock()


def threadsafeDisk(node):
    """Return a threadsafe singleton (single/common instance) for one specific disk.

    It is true that d=Disk('/dev/sda') generates one class instance that wraps around
    one specific disk. That's great. Unfortunately, e=Disk('/dev/sda') does the same
    thing; changes to d's properties don't update e's properties. This is a problem.

    If you use d=threadsafeDisk('/dev/sda') instead, the function will return the
    same Disk('/dev/sda') instance whenever the function is called.

    Example:
        $ d = threadsafeDisk('/dev/sda')
        $ d.node
        '/dev/sda'

    Args:
        device_path (:obj:`str`): Full path to the disk in question. The
            path may be a simple /dev entry, e.g. /dev/sda or /dev/sda1,
            or it may be /dev/disk/by-uuid/..... etc. The end result is
            the same. If it's a disk that holds partitions), then the
            result returned will be True. If it's a partition, False.
            If we can't figure it out, we raise an exception.

    Returns:
        bool: True if a disk, False if a partition.

    Raises:
        ValueError: If the device doesn't exist, or is a softlink to a
            nonexistent file, or is a directory, or has an unfamiliar
            name structure.

    """
    global _disks_dct
    try:
        the_threadsafeDisk_lock.acquire()
        if node not in _disks_dct:
            _disks_dct[node] = Disk(node)
        retval = _disks_dct[node]
    finally:
        the_threadsafeDisk_lock.release()
    return retval


def is_this_a_disk(device_path, insist_on_this_existence_state=None):
    """Figure out if the supplied path is a disk (True) or a partition (False).

    Examine the supplied path. If it doesn't exist or if we can't figure out
    its nature by examining its path string, raise an exception. Otherwise,
    return True if it's a disk or False if it's a partition.

    Args:
        device_path (:obj:`str`): Full path to the disk in question. The
            path may be a simple /dev entry, e.g. /dev/sda or /dev/sda1,
            or it may be /dev/disk/by-uuid/..... etc. The end result is
            the same. If it's a disk that holds partitions), then the
            result returned will be True. If it's a partition, False.
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
    if device_path in (None, "/") or not exists:
        raise ValueError("%s not found" % str(device_path))
    linked_to = os.path.realpath(device_path)
    search_for_this_stub = os.path.basename(linked_to)
    if device_path.count("/") > 3 and linked_to.count("/") <= 3:
        return is_this_a_disk(
            linked_to, insist_on_this_existence_state=insist_on_this_existence_state
        )
    elif deduce_partno(device_path) in (None, "") and search_for_this_stub.startswith(
        "mmc"
    ):
        return True
    elif search_for_this_stub.startswith("mmc"):
        if ("p" in search_for_this_stub[-4:-1]) and search_for_this_stub[-1].isdigit():
            return False
        else:
            return True
    elif len(search_for_this_stub) >= 2 and search_for_this_stub[1] == "d":
        if deduce_partno(device_path) not in (None, ""):
            return False
        else:
            return True
    elif os.path.isdir(device_path):
        raise ValueError("%s is a directory, not a device")
    elif "zram" in os.path.basename(device_path):
        return False
    else:
        raise ValueError("I do not know if %s is a disk or not" % device_path)


def fix_order_of_disk_partitiontable_entries(disk_path):
    """If the disk's partitions are in a silly order, re-sort them.

    This subroutine uses fdisk to sort a disk's partitions if they're in
    a weird order. If they're not, nothing will change.

    Args:
        disk_path (:obj:`str`): The /dev entry (e.g. /dev/sda) of the disk.

    Note:
        This subroutine assumes that the host OS runs in English.

    Returns:
        (int, str, None|str):
            int: The code returned by sfdisk. 0=success; nonzero=error.
            str: Stdout text.
            None|str: Purpose unknown.

    Raises:
        ValueError: Disk not found.

    Todo:
        * Add more TODOs
        * Test me (write a unit test)!

    """
    if not os.path.exists(disk_path):
        raise ValueError(
            "Please specify an existent disk whose partition table you want \
me to sort; {disk_path} does not exist".format(
                disk_path=disk_path
            )
        )
    retcode, stdout_txt, stderr_txt = call_binary(
        ["fdisk", disk_path],
        """x
f
w
q
""",
    )
    if retcode != 0:
        raise PartitionTableReorderingError(
            "Failed to sort {disk_path}'s partitions".format(disk_path=disk_path)
        )
    return (retcode, stdout_txt, stderr_txt)


def diskid_sizeinbytes_sizeinsectors_and_sectorsize(disk_path):
    """Retrieve the disk ID, disk size (bytes and sectors), and sector size.

    This subroutine interrogates the disk device path via fdisk and obtains
    the disk ID (its eight-digit hexadecimal string), its size in bytes,
    its size in disk sectors, and the sector size.

    Args:
        disk_path (:obj:`str`): The /dev entry (e.g. /dev/sda) of the disk_path.

    Returns:
        tuple (
            :obj:`str` - A ten-character string, composed of the
                prefix '0x' and then eight hexadecimal characters, e.g.
                "0x1234ABCD".
            int - The maximum capacity of the disk, in bytes.
            int - The maximum capacity of the disk, in sectors.
            int - The size of each sector, in bytes.
            )

    Raises:
        None

    Todo:
        * Add more TODOs

    """
    retcode, stdout_txt, stderr_txt = call_binary(
        param_lst=["sfdisk", "-l", disk_path], input_str=None
    )
    if retcode != 0:
        print(stderr_txt)
        print("Warning -- diskid_sizein_...et. - nonzero retcode")
    disk_length_in_bytes, lab1, disk_length_in_sectors, lab2 = stdout_txt.split("\n")[
        0
    ].split(" ")[-4:]
    disk_id = [r for r in stdout_txt.split("\n") if ": 0x" in r][0].split(" ")[-1]
    #    just_fdisk_op = subprocess.run(['fdisk', '-l', disk_path], \
    #                                stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
    #    (disk_length_in_bytes, lab1, disk_length_in_sectors, lab2) = \
    #                                just_fdisk_op.stdout.decode('UTF-8').split('\n')[0].split(' ')[-4:]
    #    disk_id = [r for r in just_fdisk_op.stdout.decode('UTF-8').split('\n') if ': 0x' in r][0].split(' ')[-1]
    sector_size = int(disk_length_in_bytes) / int(disk_length_in_sectors)
    assert int(sector_size) == float(
        sector_size
    ), "Sector size should be an integer. My disk-analyzing script appears to be broken."
    del lab1, lab2
    return (
        disk_id,
        int(disk_length_in_bytes),
        int(disk_length_in_sectors),
        int(sector_size),
    )


def set_disk_id(node, new_diskid):
    """Set the serial number of the specified disk.

    If you run fdisk {node}, you'll see a field that says, "Disk ID: 0x....."
    or similar. That's the disk's serial number. Using fdisk, I can change it

    Args:
        node (:obj:`str`): The path (e.g. /dev/sda) of the disk's node.
        new_diskid (:obj:`str`): A ten-character string, composed of the
            prefix '0x' and then eight hexadecimal characters, e.g.
            "0x1234ABCD".

    Returns:
        None

    Raises:
        DiskIDSettingFailureError: Failed to set the disk ID.

    Todo:
        * Add more TODOs

    """
    retcode, stdout_txt, stderr_txt = call_binary(
        ["fdisk", node],
        """x
i
{new_diskid}
r
w
""".format(
            new_diskid=new_diskid
        ),
    )
    os.system("""sync;sync;sync;partprobe {node}; sync;sync;sync""".format(node=node))
    resultant_id = diskid_sizeinbytes_sizeinsectors_and_sectorsize(node)[0]
    if resultant_id != new_diskid:
        print(retcode)
        print(stdout_txt)
        print(stderr_txt)
        raise DiskIDSettingFailureError(
            "Failed to set disk ID of {node} to {id}".format(node=node, id=new_diskid)
        )


def sfdisk_output(node):
    """Call sfdisk, collect information in JSON format, and return it.

    This subroutine calls sfisk and asks for a JSON-formatted output of
    information pertaining to the disk specified in node.

    Args:
        node (:obj:`str`): The /dev entry (e.g. /dev/sda) of the node.

    Returns:
        json dictionary {
            partiontable dictionary {
                id
                device
                unit
                partitions
                    [
                    0: {node, start, size, type, id, label, partuuid, path, uuid}
                    1: {node, start, size, type, id, label, partuuid, path, uuid}
                    2: {...}
                    ...
                    ]
                }

    Raises:
        None

    Todo:
        * Add more TODOs

    """
    retcode, stdout_txt, stderr_txt = call_binary(
        param_lst=["sfdisk", "-J", node], input_str=None
    )
    if retcode != 0:
        print("sfdisk_output({node}) ==>".format(node=node))
        print(stderr_txt)
    return json.loads(stdout_txt)


#    my_oput = subprocess.run(['sfdisk', '-J', node], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
#    res = json.loads(my_oput.stdout.decode('UTF-8'))
#    return res


def all_disk_paths():
    """Derive a complete list of disks (not partitions) from /proc/partitions.

    Interrogate /proc/partitions. Gather a list of disks (not partitions) from
    that file. Return the list as, well, a list of /dev/... entries.

    Args:
        None

    Returns:
        list of strings, e.g. ['/dev/sda', '/dev/mmcblk0', '/dev/sdb']

    Raises:
        None

    Todo:
        * Add a meaningful check --- did our serial-change succeed or fail?

    """
    all_dev_entries = []
    with open("/proc/partitions", "r") as f:
        s = f.read().split("\n")
        for r in [r.split(" ")[-1] for r in s]:
            pth = os.path.join("/dev/", r)
            if r != "" and os.path.exists(pth) and is_this_a_disk(pth):
                all_dev_entries.append(pth)
    return all_dev_entries


def namedtuples_for_all_disks():
    """Obtain list of namedtuples of all *disk* listed in /proc/partitions.

    Scan /proc/partitions. Create a namedtuple for each disk (not the
    partitions but the *disks*) and make a list of them all. The
    namedtuples are generated by disk_namedtuple(), which in turn uses
    the JSON library and calls sfdisk -J (get JSON-friendly output).

    Args:
        None.

    Returns:
        list of namedtuples: One per disk listed in /proc/partitions.

    Raises:
        None.

    Todo:
        * Add more TODOs.

    """
    disks = []
    for devpath in all_disk_paths():
        disks.append(disk_namedtuple(devpath))
    return disks


def enhance_the_sfdisk_output(node, json_rec):
    """Add sector size, disk size, etc. to the supplied JSON record.

    Using fdisk, we interrogate the specified disk, obtain additional
    information, and add it to the supplied JSON record. You see, the JSON
    record was the result of a call to sfdisk. Well, it is missing a few
    things, such as Disk ID. That's why we're calling fdisk and adding its
    info to the JSON record.

    Args:
        node (:obj:`str`): The /dev entry (e.g. /dev/sda) of the disk.
        json_rec (json record): The existing JSON-formatted record that
            sfdisk returned when asked about node. THIS IS MODIFIED
            BY ME. The new data is added to json_rec, which will retain
            its new data.

    Returns:
        None, although json_rec has been modified by me to include the new data.

    Raises:
        None

    Todo:
        * Add more TODOs.

    """
    (
        disk_id,
        node_size_in_bytes,
        node_size_in_sectors,
        sector_size,
    ) = diskid_sizeinbytes_sizeinsectors_and_sectorsize(node)
    json_rec["partitiontable"]["sector_size"] = sector_size
    json_rec["partitiontable"]["size_in_bytes"] = node_size_in_bytes
    json_rec["partitiontable"]["size_in_sectors"] = node_size_in_sectors
    json_rec["partitiontable"]["disk_label"] = json_rec["partitiontable"]["label"]
    del json_rec["partitiontable"]["label"]
    json_rec["partitiontable"]["disk_id"] = disk_id
    for disk_searchby in ("id", "label", "partuuid", "path", "uuid"):
        json_rec["partitiontable"][disk_searchby] = devdiskbyxxxx_path(
            node, disk_searchby
        )
        for partition_rec in json_rec["partitiontable"]["partitions"]:
            for partition_searchby in ("id", "label", "partuuid", "path", "uuid"):
                partition_rec[partition_searchby] = devdiskbyxxxx_path(
                    partition_rec["node"], partition_searchby
                )
    json_rec["partitiontable"]["node"] = node
    return json_rec


def disk_namedtuple(node):
    """Get a namedtuple of info from sfdisk and fdisk, re: the disk specified.

    The binary 'sfdisk' can generate a JSON record containing information about
    a specified disk and all its partitions. I, disk_namedtuple(), call that
    binary and process its output. I turn it from a JSON-esque dictionary
    into a named tuple. For example, rec['partitiontable'] becomes
    becomes rec.partitiontable and so on.

    Args:
        node (:obj:`str`): The /dev entry (e.g. /dev/sda) of the node.

    Returns:
        namedtuple(
            partitiontable:[]
            ...
            ...
        )

    Raises:
        ValueError: If node is an invalid string or points to a
            nonexistent disk.

    Todo:
        * Add more TODOs.

    """
    if node in (None, "/", "") or not os.path.exists(node) or os.path.isdir(node):
        raise ValueError("Cannot get disk record -- %s not found" % str(node))
    json_rec = sfdisk_output(node)
    # Changes are saved to json_rec
    _ = enhance_the_sfdisk_output(node, json_rec)
    res = json.loads(
        json.dumps(json_rec),
        object_hook=lambda d: namedtuple("X", d.keys())(*d.values()),
    )
    return res


class Disk:
    """Class instance that wraps around /dev/sda, /dev/mmcblk0, or whichever.

    Note:
        None.

    Args:
        node (:obj:`str`): The path (/dev/etc.) of the disk that
            we care about.

    Returns:
        None.

    Raises:
        ValueError: If node is invalid.

    Todo:
        * Add more TODOs
        * Add proper read- and write-locking.

    """

    def __init__(self, node):
        self._user_specified_node = node
        self._node = os.path.realpath(self._user_specified_node)
        if not is_this_a_disk(self._user_specified_node):
            raise ValueError("Nope -- %s is not a disk" % self._user_specified_node)
        self.__cache = None
        self.update()

    def __str__(self):
        return """fisk_path=%s  id=%s device=%s  unit=%s  partitions:%d""" % (
            self.node,
            self.id,
            self.device,
            self.unit,
            len(self.partitions),
        )

    def __repr__(self):
        return f'Disk(node="%s")' % self.node

    def partprobe(self):
        """Run partprobe binary on my own disk (self.node).

        Note:
            None.

        Args:
            None.

        Returns:
            None.

        """
        d = self.node if os.path.exists(self.node) else ""
        os.system("sync;sync;sync;partprobe %s;sync;sync;sync" % d)

    def update(self, partprobe=True):
        """Re-read the paths, disk ID, etc. for this disk.

        Note:
            None.

        Args:
            partprobe (:obj:`bool`): Should I run partprobe first?

        Returns:
            None

        """
        #        print("Initializing Disk(%s)" % self.__user_specified_node)
        from my.disktools.partitions import DiskPartition

        if partprobe:
            self.partprobe()
        self.__cache = disk_namedtuple(self.node)
        self._id = self.__cache.partitiontable.id
        self._device = self.__cache.partitiontable.device
        self._unit = self.__cache.partitiontable.unit
        self._disk_label = self.__cache.partitiontable.disk_label
        self._disk_id = self.__cache.partitiontable.disk_id
        self._sector_size = self.__cache.partitiontable.sector_size
        self._size_in_sectors = self.__cache.partitiontable.size_in_sectors
        self._partitions = []
        for p in self.__cache.partitiontable.partitions:
            self.partitions.append(DiskPartition(p.node))
        if self.overlapping:
            print("Warning -- partitions in %s are overlapping" % self.node)
        for p in self.partitions:
            p.update()

    @property
    def disk_id(self):
        """str: the hexadecimal ID (from sfdisk's output) of the disk itself"""
        return self._disk_id

    @disk_id.setter
    def disk_id(self, value):
        _ = int(value, 16)
        if len(value) != 10 or value[:2] != "0x":
            raise ValueError("%s is an invalid disk id string" % value)
        try:
            set_disk_id(self.node, value)
        finally:
            self.update()
        assert self._disk_id == value

    @disk_id.deleter
    def disk_id(self):
        raise AttributeError("Not permitted")

    @property
    def disk_label(self):
        """str: the /dev/disk/by-label/... (from sfdisk's output) of the disk"""
        return self._disk_label

    @disk_label.setter
    def disk_label(self, value):
        raise AttributeError("Not permitted")

    @disk_label.deleter
    def disk_label(self):
        raise AttributeError("Not permitted")

    @property
    def node(self):
        """str: the /dev path of the disk itself."""
        return self._node

    @node.setter
    def node(self, value):
        raise AttributeError("Not permitted")

    @node.deleter
    def node(self):
        raise AttributeError("Not permitted")

    @property
    def id(self):
        """str: the ID (from sfdisk's output) of the disk itself"""
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("Not permitted")

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def unit(self):
        """str: the human-readable name of the unit of measurement that
        fdisk, sfdisk, etc. will use when reading and writing the
        settings for the disk partitions. Probably 'sector'."""
        return self._unit

    @unit.setter
    def unit(self, value):
        raise AttributeError("Not permitted")

    @unit.deleter
    def unit(self):
        raise AttributeError("Not permitted")

    @property
    def device(self):
        """str: the /dev path of the disk itself"""
        return self._device

    @device.setter
    def device(self, value):
        raise AttributeError("Not permitted")

    @device.deleter
    def device(self):
        raise AttributeError("Not permitted")

    @property
    def partitions(self):
        """list[] of DiskPartition records: All the partitions
        that belong to this disk."""
        return self._partitions

    @partitions.setter
    def partitions(self, value):
        raise AttributeError("Not permitted")

    @partitions.deleter
    def partitions(self):
        raise AttributeError("Not permitted")

    @property
    def sector_size(self):
        """int: the sector size that the disk uses. Probably 512."""
        return self._sector_size

    @sector_size.setter
    def sector_size(self, value):
        raise AttributeError("Not permitted")

    @sector_size.deleter
    def sector_size(self):
        raise AttributeError("Not permitted")

    @property
    def size_in_sectors(self):
        """int: The maximum capacity of the disk, in sector."""
        return self._size_in_sectors

    @size_in_sectors.setter
    def size_in_sectors(self, value):
        raise AttributeError("Not permitted")

    @size_in_sectors.deleter
    def size_in_sectors(self):
        raise AttributeError("Not permitted")

    @property
    def overlapping(self):
        """Tell you if this disk's partitions overlap."""
        from my.disktools.partitions import overlapping

        return overlapping(self.node)

    @overlapping.setter
    def overlapping(self, value):
        raise AttributeError("Not permitted")

    @overlapping.deleter
    def overlapping(self):
        raise AttributeError("Not permitted")

    def add_partition(
        self,
        partno=None,
        start=None,
        end=None,
        fstype=None,
        debug=False,
        size_in_MiB=None,
    ):
        """Add a disk partition to this disk.

        I, a class that wraps around the specified disk, will use fdisk/sfdisk
        to add a partition to my disk. I do not format the partition.

        Args:
            partno (int, optional): The partition#. If it is unspecified, the
                next one will be used. For example, if the last partition is #2,
                then #3 will be the new partition's number.
            start (int, optional): The first sector of the partition. If it is
                unspecified, the first cylinder on the disk *after* the last
                partition. A value of 0 is permitted even if partno>1 but it is
                *strongly* discouraged.
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
            ExistentPriorPartitionError: We can't create an existing partition.
            PartitionWasNotCreatedError: Creation of the partition failed.
            ValueError: Other bad parameters were supplied.
            PartitionWasNotCreatedError: Although the creation process
                returned no errors, a partition was not created.
        Notes:
            None.

        """
        from my.disktools.partitions import delete_partition, partition_exists

        if partno is None:
            if len(self.partitions) == 0:
                partno = 1
            else:
                partno = max([r.partno for r in self.partitions]) + 1
        if partno < 1 or partno > 63:
            raise ValueError("The specified partno %d is too low/high" % partno)
        if partno in [r.partno for r in self.partitions]:
            raise ValueError(
                "Partition %d exists already. I cannot create two of them." % partno
            )
        if partno >= 5:
            pass
        # If partition# is 2, 3, or 4, we'll run some 'start'/'end' checks.
        else:
            if start is None:
                try:
                    previous_partition = [
                        r for r in self.partitions if r.partno == partno - 1
                    ][0]
                    start = previous_partition.end + 1
                except IndexError:
                    start = None
            if partno > 1 and start is None:
                raise ValueError(
                    "Specify start sector of partition #%d of %s" % (partno, self.node)
                )
            if end is None and size_in_MiB is None:
                try:
                    end = [r for r in self.partitions if r.partno == partno + 1][
                        0
                    ].start - 1
                except IndexError:
                    pass
        if partno >= 5 and [] == [
            p for p in self.partitions if p.fstype == _FS_EXTENDED
        ]:
            raise WeNeedAnExtendedPartitionError(
                "Please create an extended partition first."
            )
        try:
            add_partition(
                self.node,
                partno=partno,
                start=start,
                end=end,
                fstype=fstype,
                debug=debug,
                size_in_MiB=size_in_MiB,
            )
        except (
            PartitionsOverlapError,
            StartEndAssBackwardsError,
            MissingPriorPartitionError,
            PartitionWasNotCreatedError,
            ValueError,
            ExistentPriorPartitionError,
        ) as e:
            if self.overlapping and type(e) is not PartitionsOverlapError:
                e = PartitionsOverlapError(
                    "Changing exception from %s to PartitionsOverlapError" % str(e)
                )
            delete_partition(self.node, partno)
            raise e
        else:
            if not partition_exists(self.node, partno):
                print("Partition creation failed... and I don't know why.")
                raise PartitionWasNotCreatedError(
                    "Failed to create partition #%d for %s" % (partno, self.node)
                )
        finally:
            self.update()

    def delete_all_partitions(self):
        """Delete all partitions that I, a disk, contain."""
        from my.disktools.partitions import delete_all_partitions
        delete_all_partitions(self.node)  # Also runs partprobe.
        self.update(partprobe=False)  # No need to run partprobe again.

    def delete_partition(self, partno, update=True):
        """Delete the specified partition#.

        As I (this class instance) am a disk, only the partition number
            need be specified. I already know which disk I'm to modify.

        Note:
            Do not insult a dragon's mother.

        Args:
            partno (int): The partition# to be deleted.
            update (bool): True if you want me to run self.update()
                after deleting the partition; otherwise, False.

        Returns:
            None

        """
        from my.disktools.partitions import delete_partition, partition_exists

        if partition_exists(self.node, partno):
            try:
                delete_partition(self.node, partno)
            finally:
                self.update(partprobe=update)
        else:
            print(
                "No need to delete partition #%d from %s --- that partition does not exist"
                % (partno, self.node)
            )

    def dump(self):
        """Derive information about me and my partitions.

        Returns:
            :obj:`str`: Human-readable info dump.

        """
        outtxt = """label: {disk_label}
label-id: {disk_id}
device: {node}
unit: sectors

""".format(
            disk_label=self.disk_label, disk_id=self.disk_id, node=self.node
        )
        for p in self.partitions:
            outtxt += """%-10s: start=%12d, size=%12d, type=%s
""" % (
                p.node,
                p.start,
                p.size,
                p.fstype,
            )
        return outtxt
