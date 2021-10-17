'''
Created on Oct 17, 2021

@author: Tom Blackshaw
'''

from collections import namedtuple
import json
import os
import random
import subprocess


def is_this_a_disk(device_path):
    '''
    Is this a disk (not a partition)?
    e.g. /dev/sda     YES
         /dev/sda1    NO
    '''
    if not os.path.exists(device_path):
        raise FileNotFoundError("%s not found" % device_path)
    if b'' != subprocess.run(['sfdisk', '-J', device_path], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE).stdout:
        return True
    else:
        return False


def set_disk_id(node, new_diskid):
    os.system('''echo "x\ni\n{new_diskid}\nr\nw" | fdisk {node}'''.format(node=node, new_diskid=new_diskid))


def was_this_partition_created(node, partno):
    if 0 == os.system('''sfdisk -d %s | grep -x "%s.*%d :.*" > /dev/null''' % (node, node, partno)):
        return True
    else:
        return False


def add_partition_SUB(node, partno, start, end, fstype, with_partno_Q=True):
    print('aaa')
    if with_partno_Q:
        res = os.system('''echo "p\nn\np\n%s\n%s\n%s\nw" | fdisk %s >/dev/null 2>/dev/null''' % (
                            '' if not partno else str(partno),
                '' if not start else str(start),
                '' if not end else str(end), node))
    else:
        res = os.system('''echo "p\nn\np\n%s\n%s\nw" | fdisk %s >/dev/null 2>/dev/null''' % (
                '' if not start else str(start),
                '' if not end else str(end), node))
    print('bbb')
    res += os.system('''
tmpfile=/tmp/blah.txt # /tmp/$(printf "%08x" 0x$(dd if=/dev/urandom bs=1 count=200 2>/dev/null | tr -dc 'a-f0-9' | cut -c-8))
sfdisk -d {node} | grep -vx "{node}.*{partno} :.*" > $tmpfile
sfdisk -d {node} | grep -x "{node}.*{partno} :.*" | sed 's|type=.*|type={fstype}|' >> $tmpfile
cat $tmpfile | grep -vx "{node}.* :.*" > $tmpfile.final
cat $tmpfile | grep -x "{node}.* :.*" | sort > $tmpfile.final

sfdisk -f {node} < $tmpfile.final >/dev/null 2>/dev/null
#rm -f $tmpfile $tmpfile.final
'''.format(node=node, partno=partno, fstype=fstype))


def add_partition(node, partno, start, end, fstype=83):
    '''
    add_partition('/dev/sda', 1, 32768, 65535)
    '''
    if end is not None and end <= start:
        raise ValueError("The partition must end after it starts")
    if partno == 1:
        res = add_partition_SUB(node, partno, start, end, fstype, with_partno_Q=False)
        if res != 0:
            res = add_partition_SUB(node, partno, start, end, fstype)
    else:
        res = add_partition_SUB(node, partno, start, end, fstype)
    return res


def delete_partition(node, partno):
    return os.system('''sfdisk -d %s 2> /dev/null| grep -vx "%s.*%d :.*" | sfdisk -f %s >/dev/null 2>/dev/null''' % (node, node, partno, node))


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
        linked_to = os.path.realpath(fullpath)
        if node_path == linked_to:
            return fullpath
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
                partition[i] = get_altpath_from_node_path(partition['node'], i)
    return json_rec


def get_disk_record(node_path):
    if not os.path.exists(node_path):
        raise FileNotFoundError('Cannot get disk record -- %s not found', node_path)
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
        return """node=%s owner=%s start=%d size=%d fstype=%s label=%s partuuid=%s path=%s uuid=%s""" % \
            (self._node, self._owner, self._start, self._size, self._fstype, self._label, self._partuuid, self._path, self._uuid)

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
    def size_in_MiB(self):
        """I'm the 'size_in_MiB' property."""
        return self._size / 1024 / 1024

    @size_in_MiB.setter
    def size_in_MiB(self, value):
        self._size = value * 1024 * 1024

    @size_in_MiB.deleter
    def size_in_MiB(self):
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
        self.__user_specified_node = node
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

    def update(self):
        os.system("sync;sync;sync;partprobe %s;sync;sync;sync" % self.__user_specified_node)
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
        for p in self.__cache.partitiontable.partitions:
            self.partitions.append(DiskPartition(p.node))
        if self.overlapping:
            print("Warning -- partitions in %s are overlapping" % self.node)

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
                and p_prev.end >= p_next.start:
                    return True
        return False

    @overlapping.setter
    def overlapping(self, value):
        raise AttributeError("Not permitted")

    @overlapping.deleter
    def overlapping(self):
        raise AttributeError("Not permitted")

    def add_partition(self, partno, start=None, end=None, fstype='83', size_in_MiB=None):
        if len(self.partitions) == 4:
            raise AttributeError("Cannot have >%d partitions in %s" % (len(self.partitions), self.node))
        if start is None and len(self.partitions) >= 1:
            start = 1 + [r for r in self.partitions if r.node[-1:] == str(partno - 1)][0].end
            partno_start_after_me_lst = [r.start for r in self.partitions if r.node[-1:] == str(partno + 1)]
            if len(partno_start_after_me_lst) > 0:
                end = partno_start_after_me_lst[0] - 1
        if size_in_MiB is not None:
            assert end is None, "Specify either end=... or size_in_MIB... but don't specify both"
            end = start + (size_in_MiB * 1024 * 1024) // self.sector_size
        try:
            add_partition(self.node, partno, start, end, fstype)
            self.update()
            if self.overlapping:
                delete_partition(self.node, partno)
                raise AttributeError("Refusing to create partition #%d for %s -- it would overlap with another partition" % (partno, self.node))
        finally:
            self.update()
        if not was_this_partition_created(self.node, partno):
            raise AttributeError("Failed to create partition #%d for %s" % (partno, self.node))

    def delete_all_partitions(self):
        for i in range(5, -1, -1):
            self.delete_partition(partno=i + 1)
        self.update()

    def delete_partition(self, partno):
        try:
            delete_partition(self.node, partno)
        finally:
            self.update()

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
