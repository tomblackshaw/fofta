'''
Created on Oct 16, 2021

@author: Tom Blackshaw

'''
from my.partitiontools import Disk

'''

'''

if __name__ == '__main__':
    d = Disk('/dev/sda')
    d.delete_all_partitions()
    d.add_partition(1, 50000, 99999)
    d.add_partition(2, 0, d.partitions[0].start)
    d.add_partition(2, 0, d.partitions[0].start - 1)
    d.delete_partition(2)
    d.add_partition(2, d.partitions[0].end + 1, d.partitions[0].end + 99999)
    d.add_partition(3, d.partitions[1].end + 1, d.partitions[1].end + 99999)
    d.add_partition(4, d.partitions[2].end + 1, d.partitions[2].end + 99999)
    d.delete_partition(3)
