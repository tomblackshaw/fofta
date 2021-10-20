'''
Created on Oct 16, 2021

@author: Tom Blackshaw


FOFTA - from one filesystem to another

To run a unit test:-
# python3 -m unittest test/test_partitiontools

'''
# from my.partitiontools import *
from my.partitiontools import get_list_of_all_disks

# if __name__ == '__main__':

'''
lst = get_list_of_all_disks()
unmatched_devs = []
for line in [t for t in txt.split('\n')]:
    dev = line.split(' ')[-1]
    if dev != '' \
    and os.path.exists(os.path.join('/dev', dev)) \
    and dev not in ([os.path.basename(p.node) for p in d.partitions]):
        unmatched_devs.append(dev)
'''
