# -*- coding: utf-8 -*-
"""
Created on Nov 2, 2021

@author: Tom Blackshaw
"""
#from my.disktools.partitions import DiskPartition, partition_namedtuple
import os
from my.globals import call_binary, _GPT, _DOS






if __name__ == '__main__':
    os.environ['PATH'] = os.environ['PATH']+':'+os.getenv('PATH')
    import pydevd; pydevd.settrace("192.168.0.139", port=5678, stdoutToServer=True, stderrToServer=True)
    MY_DISK_IMGSIZE_IN_MB = 160
    MY_DISK_LOOPDEV  = '/dev/loop5'
    MY_DISK_IMGFILE = '/tmp/.fofta.temp.image.file'
    from my.disktools.disks import Disk
    s = call_binary(['df','-m','/tmp'])[1].split('\n')[1].split('tmpfs')[1].strip(' ')
    if int(s.split(' ')[0]) < MY_DISK_IMGSIZE_IN_MB:
        MY_DISK_IMGFILE = MY_DISK_IMGFILE.replace('/tmp/','/root/')
    retcode, stdout_txt, stderr_txt = call_binary(['dd', 'bs=1024k', 'if=/dev/zero', 'of='+MY_DISK_IMGFILE,
                                                   'count=%d'%MY_DISK_IMGSIZE_IN_MB])
    retcode, stdout_txt, stderr_txt = call_binary(['losetup', '-d', MY_DISK_LOOPDEV])
    retcode, stdout_txt, stderr_txt = call_binary(['losetup', MY_DISK_LOOPDEV, MY_DISK_IMGFILE])
    os.system("partprobe " + MY_DISK_LOOPDEV)
    d = Disk(MY_DISK_LOOPDEV, new_partition_table=_DOS)
    try:
        d.add_partition()
    except AttributeError:
        pass   
    # nt =    partition_namedtuple(d.node)
    # p = DiskPartition(d._cache.partitiontable.partitions[0].node)
    
    
    

