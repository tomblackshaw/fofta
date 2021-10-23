'''
Created on Oct 18, 2021

@author: Tom Blackshaw
TODO: Write inline docs & comments
TODO: Write Google-style doc header

Usage:
    $ import my.disktools.both

'''

from collections import namedtuple
import os.path, os.listdir

from my.disktools.disks import get_disk_record_from_all_disks
from my.globals import FS_EXTENDED, FS_DEFAULT


def find_node_to_which_a_partition_belongs(path_of_partition):
    '''
    TODO: Write Google-style doc header
    '''
    from my.disktools.partitions import deduce_partno, delete_all_partitions, \
                was_this_partition_created, delete_partition, add_partition, \
                is_this_partition_instance_our_partition
    if not os.path.exists(path_of_partition):
        raise FileNotFoundError("%s does not exist" % path_of_partition)
    for d in get_disk_record_from_all_disks():
        for p in d.partitiontable.partitions:
            if is_this_partition_instance_our_partition(path_of_partition, p):
                return d.partitiontable.node
    return None


def get_altpath_from_node_path(node_path, searchby):
    '''
    TODO: Write Google-style doc header
    '''
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

# def write_new_disk_record_via_sfdisk(disk):

