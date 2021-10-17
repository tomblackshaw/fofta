'''
Created on Oct 16, 2021

@author: Tom Blackshaw

'''
# from my.partitiontools import *

# if __name__ == '__main__':

from my.partitiontools import *
d = Disk('/dev/sda')
d.delete_all_partitions()
d.add_partition(partno=1, start=50000, end=99999)
d.add_partition(partno=2, start=0, end=d.partitions[-1].start)
d.add_partition(partno=2, start=0, end=d.partitions[-1].start - 1)
d.delete_partition(2)
d.add_partition(2, size_in_MiB=400)
d.add_partition(3, size_in_MiB=300)
d.add_partition(4, size_in_MiB=200)
d.delete_partition(3)
d.add_partition(3)
d.add_partition(3, start=d.partitions[1].end + 1)

[r for r in d.partitions if r.node[-1:] == str(1)]

d.delete_partition(3)
d.add_partition(3)
