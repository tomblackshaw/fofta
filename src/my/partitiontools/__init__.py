'''
Created on Oct 18, 2021

@author: Tom Blackshaw
TODO Write inline docs & comments
TODO Write unit tests
'''

from collections import namedtuple
import json
import os
import random
import subprocess

FS_EXTENDED = '5'
FS_DEFAULT = '83'


def is_this_a_disk(device_path, insist_on_this_existence_state=None):
    '''
    Is this a disk (not a partition)?
    e.g. /dev/sda     YES
         /dev/sda1    NO
    '''
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
    elif search_for_this_stub[:2] in ('sd', 'hd', 'scd', 'md'):
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


def set_disk_id(node, new_diskid):
    os.system('''echo "x\ni\n{new_diskid}\nr\nw" | fdisk {node}'''.format(node=node, new_diskid=new_diskid))


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
    '''
from my.partitiontools import *
d = Disk('/dev/disk/by-id/usb-Mass_Storage_Device_121220160204-0:0')  # d = Disk('/dev/sda')
add_partition_SUB(node='/dev/sda', partno=5, start=125042688, with_partno_Q=False, end=None, size_in_MiB=100)
    '''
    node = os.path.realpath(node)
    if debug:
        print("add_partition_SUB() -- node=%s; partno=%s; start=%s; end=%s; size_in_MiB=%s" % (str(node), str(partno), str(start), str(end), str(size_in_MiB)))
    if end is not None and size_in_MiB is not None:
        raise AttributeError("Specify either end=... or size_in_MIB... but don't specify both")
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
                'e' if fstype == FS_EXTENDED else 'l' if partno >= 5 else 'p',
                '' if not partno else str(partno),
                '' if not start else str(start),
                '' if not end_str else end_str, node, debug_str))
    else:
        res = os.system('''echo "p\nn\n%s\n%s\n%s\nw" | fdisk %s %s''' % (
                'e' if fstype == FS_EXTENDED else 'l' if partno >= 5 else 'p',
                '' if not start else str(start),
                '' if not end_str else end_str, node, debug_str))
    res += os.system('''sfdisk --part-type {node} {partno} {fstype} {debug}'''.format(node=node, partno=partno, fstype=fstype,
                                                                                     debug='' if debug else '> /dev/null 2> /dev/null'))


def add_partition(node, partno, start, end=None, fstype=FS_DEFAULT, debug=False, size_in_MiB=None):
    '''
    add_partition('/dev/sda', 1, 32768, 65535)
    '''
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
        raise AttributeError("Because partition #%d of %s does not exist, I cannot create #%d. Logical partitions cannot be added without screwing up their order. Sorry." % (partno - 1, node, partno))
    else:
        res = add_partition_SUB(node, partno, start, end, fstype, debug=debug, size_in_MiB=size_in_MiB)
    return 0 if was_this_partition_created(node, partno) else 1


def delete_partition(node, partno):
    if partno >= 5 and was_this_partition_created(node, partno + 1):
        raise AttributeError("Because partition #%d of %s exists, I cannot create #%d. Logical partitions cannot be removed without screwing up their order. Sorry." % (partno + 1, node, partno))

    return os.system('''sfdisk %s --del %d > /dev/null 2> /dev/null''' % (node, partno))


def get_list_of_all_disks():
    all_dev_entries = []
    with open('/proc/partitions', 'r') as f:
        s = f.read().split('\n')
        for r in [r.split(' ')[-1] for r in s]:
            pth = os.path.join('/dev/', r)
            if r != '' and os.path.exists(pth) and is_this_a_disk(pth):
                all_dev_entries.append(pth)
    return all_dev_entries


def get_altpath_from_node_path(node_path, searchby):
    if not os.path.exists(node_path):
        raise FileNotFoundError("Node path %s not found" % node_path)
    altdir = "/dev/disk/by-%s" % searchby
    if not os.path.exists(altdir):
        raise FileNotFoundError("Cannot search by %s -- directory %s not found" % (searchby, altdir))
    for p in os.listdir(altdir):
        fullpath = os.path.join(altdir, p)
        try:
            linked_to = os.path.realpath(fullpath)
            if node_path == linked_to:
                return fullpath
        except FileNotFoundError:
            pass
    return None


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


def find_node_to_which_a_partition_belongs(path_of_partition):
    if not os.path.exists(path_of_partition):
        raise FileNotFoundError("%s does not exist" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_record_our_partition(path_of_partition, p):
                return d.partitiontable.node
    return None


def is_this_partition_record_our_partition(path_of_partition, p):
    if path_of_partition == p.node \
    or path_of_partition == p.partuuid \
    or path_of_partition == p.uuid \
    or path_of_partition == p.label \
    or path_of_partition == p.path:
        return True
    else:
        return False


def find_partition_record(path_of_partition):
    if not os.path.exists(path_of_partition):
        raise FileNotFoundError("Cannot find partition %s" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_record_our_partition(path_of_partition, p):
                return p
    return None

#
# def write_new_disk_record_via_sfdisk(disk):


class DiskPartition:

    def __init__(self, devpath):
        self.__user_specified_node = devpath
        self._owner = find_node_to_which_a_partition_belongs(self.__user_specified_node)
        if self._owner is None:
            raise AttributeError("%s does not belong to any disk" % self.__user_specified_node)
        self.__cache = None
        self.update()

        # TODO: QQQ add locking
    def __str__(self):
        return """node=%s partno=%d owner=%s start=%d size=%d fstype=%s label=%s partuuid=%s path=%s uuid=%s""" % \
            (self._node, self._partno, self._owner, self._start, self._size, self._fstype, self._label, self._partuuid, self._path, self._uuid)

    def __repr__(self):
        return f'DiskPartition(node="%s")' % self.node

    def update(self):
        self.__cache = find_partition_record(self.__user_specified_node)
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
        """I'm the 'node' property."""
        return self._node

    @node.setter
    def node(self, value):
        raise AttributeError("Not permitted")

    @node.deleter
    def node(self):
        raise AttributeError("Not permitted")

    @property
    def partno(self):
        """I'm the 'partno' property."""
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
        """I'm the 'owner' property."""
        return self._owner

    @owner.setter
    def owner(self, value):
        raise AttributeError("Not permitted")

    @owner.deleter
    def owner(self):
        raise AttributeError("Not permitted")

    @property
    def start(self):
        """I'm the 'start' property."""
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @start.deleter
    def start(self):
        raise AttributeError("Not permitted")

    @property
    def end(self):
        """I'm the 'end' property."""
        return self._start + self._size - 1

    @end.setter
    def end(self, value):
        raise AttributeError("Not permitted")

    @end.deleter
    def end(self):
        raise AttributeError("Not permitted")

    @property
    def size(self):
        """I'm the 'size' property."""
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @size.deleter
    def size(self):
        raise AttributeError("Not permitted")

    @property
    def fstype(self):
        """I'm the 'type' property."""
        return self._fstype

    @fstype.setter
    def fstype(self, value):
        self._fstype = value

    @fstype.deleter
    def fstype(self):
        raise AttributeError("Not permitted")

    @property
    def id(self):
        """I'm the 'id' property."""
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def label(self):
        """I'm the 'label' property."""
        return self._label

    @label.setter
    def label(self, value):
        raise AttributeError("Not permitted")

    @label.deleter
    def label(self):
        raise AttributeError("Not permitted")

    @property
    def partuuid(self):
        """I'm the 'partuuid' property."""
        return self._partuuid

    @partuuid.setter
    def partuuid(self, value):
        raise AttributeError("Not permitted")

    @partuuid.deleter
    def partuuid(self):
        raise AttributeError("Not permitted")

    @property
    def path(self):
        """I'm the 'path' property."""
        return self._path

    @path.setter
    def path(self, value):
        raise AttributeError("Not permitted")

    @path.deleter
    def path(self):
        raise AttributeError("Not permitted")

    @property
    def uuid(self):
        """I'm the 'uuid' property."""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        raise AttributeError("Not permitted")

    @uuid.deleter
    def uuid(self):
        raise AttributeError("Not permitted")


class Disk:

    def __init__(self, node):
        self.__user_specified_node = os.path.realpath(node)
        if not is_this_a_disk(self.__user_specified_node):
            raise AttributeError("Nope -- %s is not a disk" % self.__user_specified_node)
        self.__cache = None
        self.update()

        # TODO: QQQ add locking
    def __str__(self):
        return """Disk=%s node=%s  id=%s device=%s  unit=%s  partitions:%d""" % \
            (self.__user_specified_node, self._node, self._id, self._device, self._unit, len(self.partitions))

    def __repr__(self):
        return f'Disk(node="%s")' % self.node

    def partprobe(self):
        os.system("sync;sync;sync;partprobe %s;sync;sync;sync" % self.__user_specified_node)

    def update(self, partprobe=False):
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
        """I'm the 'disk_id' property."""
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
        """I'm the 'disk_label' property."""
        return self._disk_label

    @disk_label.setter
    def disk_label(self, value):
        raise AttributeError("Not permitted")

    @disk_label.deleter
    def disk_label(self):
        raise AttributeError("Not permitted")

    @property
    def node(self):
        """I'm the 'node' property."""
        return self._node

    @node.setter
    def node(self, value):
        raise AttributeError("Not permitted")

    @node.deleter
    def node(self):
        raise AttributeError("Not permitted")

    @property
    def id(self):
        """I'm the 'id' property."""
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("Not permitted")

    @id.deleter
    def id(self):
        raise AttributeError("Not permitted")

    @property
    def unit(self):
        """I'm the 'unit' property."""
        return self._unit

    @unit.setter
    def unit(self, value):
        raise AttributeError("Not permitted")

    @unit.deleter
    def unit(self):
        raise AttributeError("Not permitted")

    @property
    def device(self):
        """I'm the 'dev' property."""
        return self._device

    @device.setter
    def device(self, value):
        raise AttributeError("Not permitted")

    @device.deleter
    def device(self):
        raise AttributeError("Not permitted")

    @property
    def partitions(self):
        """I'm the 'partitions' property."""
        return self._partitions

    @partitions.setter
    def partitions(self, value):
        raise AttributeError("Not permitted")

    @partitions.deleter
    def partitions(self):
        raise AttributeError("Not permitted")

    @property
    def sector_size(self):
        """I'm the 'sector_size' property."""
        return self._sector_size

    @sector_size.setter
    def sector_size(self, value):
        raise AttributeError("Not permitted")

    @sector_size.deleter
    def sector_size(self):
        raise AttributeError("Not permitted")

    @property
    def size_in_sectors(self):
        """I'm the 'size_in_sectors' property."""
        return self._size_in_sectors

    @size_in_sectors.setter
    def size_in_sectors(self, value):
        raise AttributeError("Not permitted")

    @size_in_sectors.deleter
    def size_in_sectors(self):
        raise AttributeError("Not permitted")

    @property
    def overlapping(self):
        for p_prev in self.partitions:
            for p_next in self.partitions:
                if p_prev.start < p_next.start \
                and p_prev.end >= p_next.start \
                and p_prev.fstype != FS_EXTENDED \
                and p_next.fstype != FS_EXTENDED:
                    return True
        return False

    @overlapping.setter
    def overlapping(self, value):
        raise AttributeError("Not permitted")

    @overlapping.deleter
    def overlapping(self):
        raise AttributeError("Not permitted")

    def add_partition(self, partno=None, start=None, end=None, fstype=FS_DEFAULT, debug=False, size_in_MiB=None):
        if end is not None and size_in_MiB is not None:
            raise AttributeError("Specify either end=... or size_in_MIB... but don't specify both")
        if partno is None:
            if len(self.partitions) == 0:
                partno = 1
            else:
                partno = max([r.partno for r in self.partitions]) + 1
        if partno < 1 or partno > 63:
            raise AttributeError("The specified partno %d is too low/high" % partno)
        if partno in [r.partno for r in self.partitions]:
            raise AttributeError("Partition %d exists already. I cannot create two of them." % partno)
        if partno >= 5:
            pass
            # if start is None:
            #     try:
            #         start = [p for p in self.partitions if p.fstype == FS_EXTENDED][0].start + 2048 // self.sector_size
            #         print("p%d will begin at %d" % (partno, start))
            #     except IndexError:
            #         raise AttributeError("Please specify start serctor of partition #%d of %s" % (partno, self.node))
            # if end is None and size_in_MiB is None:
            #     try:
            #         end = [p for p in self.partitions if p.fstype == FS_EXTENDED][0].end
            #         print("p%d will end at %d" % (partno, end))
            #     except IndexError:
            #         raise AttributeError("Please specify end serctor of partition #%d of %s" % (partno, self.node))
        else:
            if start is None and partno > 1:
                try:
                    start = [r for r in self.partitions if r.partno == partno - 1][0].end + 1
                except IndexError:
                    raise AttributeError("Please specify start serctor of partition #%d of %s" % (partno, self.node))
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
                raise AttributeError("Refusing to create partition #%d for %s -- it would overlap with another partition" % (partno, self.node))
        finally:
            self.update(partprobe=True)
        if not was_this_partition_created(self.node, partno):
            raise AttributeError("Failed to create partition #%d for %s" % (partno, self.node))

    def delete_all_partitions(self):
        delete_all_partitions(self.node)
        self.update(partprobe=True)

    def delete_partition(self, partno, update=True):
        if was_this_partition_created(self.node, partno):
#            print("Deleting partition #%d from %s" % (partno, self.node))
            try:
                delete_partition(self.node, partno)
            finally:
                self.update(partprobe=update)
        else:
            print("No need to delete partition #%d from %s --- that partition does not exist" % (partno, self.node))

    def dump(self):
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
