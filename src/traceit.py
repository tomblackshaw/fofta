# -*- coding: utf-8 -*-
"""
Created on Nov 2, 2021

@author: Tom Blackshaw
"""
from my.disktools.disks import is_this_a_disk, Disk




def my_copy_of_TestCreate12123():
    MY_TESTDISK_PATH='/dev/sda'
    assert(is_this_a_disk(MY_TESTDISK_PATH))
    d = Disk(MY_TESTDISK_PATH)
    d.delete_all_partitions()
    if [] != d.partitions:
        print("WARNING --- TestCreatte12123 -- testName --- some partitions exist already")
    if d.partitions != d.partitions:
        print("WARNING --- TestCreatte12123 -- testName --- d=", d.partitions, "but self.disk=", d.partitions)
    d.add_partition(partno=1, size_in_MiB=100)
    d.add_partition(partno=2, size_in_MiB=100)
    try:
        d.add_partition(partno=1, size_in_MiB=100)
        raise SystemError("WE SHOULD FAIL HERE")
    except ValueError:
        pass
    try:
        d.add_partition(partno=2, size_in_MiB=100)
        raise SystemError("WE SHOULD FAIL HERE")
    except ValueError:
        pass
    d.add_partition(partno=3, size_in_MiB=100)
    d.delete_all_partitions()


if __name__ == '__main__':
#    os.environ['PATH'] = os.environ['PATH']+':'+os.getenv('PATH')
#    import pydevd; pydevd.settrace("192.168.0.139", port=5678, stdoutToServer=True, stderrToServer=True)
    for i in range(0,10):
        my_copy_of_TestCreate12123()
        print("%%%d complete" % (i*10))
    print("Done.")


