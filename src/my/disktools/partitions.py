'''
Created on Oct 22, 2021

@author: Tom Blackshaw

Usage:
    $ import my.disktool.partitions

'''
import os

from my.disktools.disks import get_disk_record_from_all_disks
from my.globals import FS_EXTENDED, FS_DEFAULT


class DiskPartition:
    '''
    TODO: Write Google-style doc header
    '''

    def __init__(self, devpath):
        from my.disktools.both import find_node_to_which_a_partition_belongs
        self.__user_specified_node = devpath
        self._owner = find_node_to_which_a_partition_belongs(self.__user_specified_node)
        if self._owner is None:
            raise SystemError("%s does not belong to any disk" % self.__user_specified_node)
        self.__cache = None
        self.update()

        # TODO: QQQ add locking
    def __str__(self):
        return """node=%s partno=%d owner=%s start=%d size=%d fstype=%s label=%s partuuid=%s path=%s uuid=%s""" % \
            (self._node, self._partno, self._owner, self._start, self._size, self._fstype, self._label, self._partuuid, self._path, self._uuid)

    def __repr__(self):
        return f'DiskPartition(node="%s")' % self.node

    def update(self):
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


def deduce_partno(node):
    '''
    TODO: Write Google-style doc header
    '''
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
    '''
    TODO: Write Google-style doc header
    '''
    realnode = os.path.realpath(node)
    os.system('''sfdisk -d {node}| grep -vx "{node}.*[0-9] : .*"| sfdisk -f {node} 2>/dev/null >/dev/null'''.format(node=realnode))
    os.system("partprobe {node}".format(node=realnode))


def was_this_partition_created(node, partno):
    '''
    TODO: Write Google-style doc header
    '''
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
    TODO: Write Google-style doc header
    '''
    node = os.path.realpath(node)
    res = 0
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
    return res


def add_partition(node, partno, start, end=None, fstype=FS_DEFAULT, debug=False, size_in_MiB=None):
    '''
    TODO: Write Google-style doc header
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
        raise SystemError("Because partition #%d of %s does not exist, I cannot create #%d. Logical partitions cannot be added without screwing up their order. Sorry." % (partno - 1, node, partno))
    else:
        res = add_partition_SUB(node, partno, start, end, fstype, debug=debug, size_in_MiB=size_in_MiB)
    if not was_this_partition_created(node, partno):
        os.system('sync;sync;sync;partprobe;sync;sync;sync')
    if not was_this_partition_created(node, partno):
        raise SystemError("Failed to add partition #{partno} to {node}".format(partno=partno, node=node))
    del res
    return 0  # Throw away res if the partition was successfully created


def find_partition_instance(path_of_partition):
    '''
    TODO: Write Google-style doc header
    '''
    if not os.path.exists(path_of_partition):
        raise FileNotFoundError("Cannot find partition %s" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_instance_our_partition(path_of_partition, p):
                return p
    return None

#


def is_this_partition_instance_our_partition(path_of_partition, p):
    '''
    TODO: Write Google-style doc header
    '''
    if path_of_partition == p.node \
    or path_of_partition == p.partuuid \
    or path_of_partition == p.uuid \
    or path_of_partition == p.label \
    or path_of_partition == p.path:
        return True
    else:
        return False


def delete_partition(node, partno):
    '''
    TODO: Write Google-style doc header
    '''
    if partno >= 5 and was_this_partition_created(node, partno + 1):
        raise SystemError("Because partition #%d of %s exists, I cannot create #%d. Logical partitions cannot be removed without screwing up their order. Sorry." % (partno + 1, node, partno))

    res = os.system('''sfdisk %s --del %d > /dev/null 2> /dev/null''' % (node, partno))
    if was_this_partition_created(node, partno):
        os.system('sync;sync;sync;partprobe;sync;sync;sync')
    if was_this_partition_created(node, partno):
        raise SystemError("Failed to delete partition #{partno} to {node}".format(partno=partno, node=node))
    del res
    return 0  # Throw away res if the partition was successfully deleted


class MyClass(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
