# -*- coding: utf-8 -*-
"""my

My library

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test/test_disktools

https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html



##mycmd="python3 -m unittest ${chunk}.TestLogicalPartitions_ONE ${chunk}.TestLogicalPartitions_TWO ${chunk}.TestSettingDiskID"


c10() {
    local mycmd="$1" res
    res=0
    python3 -m unittest $mycmd; res1=$?; [ "$res1" != "0" ] && res=$(($res+1))
    echo -en "...10%"
    python3 -m unittest $mycmd; res2=$?; [ "$res2" != "0" ] && res=$(($res+1))
    echo -en "...20%"
    python3 -m unittest $mycmd; res3=$?; [ "$res3" != "0" ] && res=$(($res+1))
    echo -en "...30%"
    python3 -m unittest $mycmd; res4=$?; [ "$res4" != "0" ] && res=$(($res+1))
    echo -en "...40%"
    python3 -m unittest $mycmd; res5=$?; [ "$res5" != "0" ] && res=$(($res+1))
    echo -en "...50%"
    python3 -m unittest $mycmd; res6=$?; [ "$res6" != "0" ] && res=$(($res+1))
    echo -en "...60%"
    python3 -m unittest $mycmd; res7=$?; [ "$res7" != "0" ] && res=$(($res+1))
    echo -en "...70%"
    python3 -m unittest $mycmd; res8=$?; [ "$res8" != "0" ] && res=$(($res+1))
    echo -en "...80%"
    python3 -m unittest $mycmd; res9=$?; [ "$res9" != "0" ] && res=$(($res+1))
    echo -en "...90%"
    python3 -m unittest $mycmd; resA=$?; [ "$resA" != "0" ] && res=$(($res+1))
    echo -en "...100%"
    return $res
}

c10nn() {
    c10 "$1"
    res=$?
    echo "
$((10-$res))/10: $1
"
}

b="test.test_disktools.test_Disk_class"

4/10: c10nn "$b.TestLogicalPartitions_TWO $b.TestLogicalPartitions_ONE $b.TestSettingDiskID"
7/10: c10nn "$b.TestLogicalPartitions_ONE $b.TestLogicalPartitions_TWO $b.TestSettingDiskID"
9/10: c10nn "$b.TestMakeFourAndFiddleWithP2 $b.TestCreateDeliberatelyOverlappingPartitions"

two=$b.TestLogicalPartitions_TWO
one=$b.TestLogicalPartitions_ONE
python3 -m unittest $one.testBreakSomething


python3 -m unittest $two $one         # $one $one.testBreakSomething

$two.testDeleteHighestLogical $two.testDeleteNonhighestLogical

# c10nn "$two.testDeleteHighestLogical $two.testDeleteNonhighestLogical"

# c10nn              "$two $one"
# c10nn              "$two.testMake56765 $one"
# c10nn              "$two.testMake5And6 $one"
/mnt/fofta/src/my/disktools/partitions/__init__.py", line 984, in delete_partition
    raise PartitionDeletionError






# python3 -m unittest $two.testMakeFive $two.testMake5And6 $one
# python3 -m unittest $one $two.testMakeFive $two.testMake5And6

c10nn "$b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO $b.TestSettingDiskID"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE $b.TestSettingDiskID"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO"
c10nn "$b.TestMakeFourAndFiddleWithP2 $b.TestCreateDeliberatelyOverlappingPartitions"
c10nn "$b.TestCreateFullThenAddOne    $b.TestCreate12123"
c10nn "$b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE $b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO $b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestCreate12123           $b.TestLogicalPartitions_TWO"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestCreate12123           $b.TestLogicalPartitions_ONE"
c10nn "$b.TestCreate12123             $b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO"
c10nn "$b.TestCreate12123             $b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE"
c10nn "$b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO $b.TestSettingDiskID"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE $b.TestSettingDiskID"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO"
c10nn "$b.TestMakeFourAndFiddleWithP2 $b.TestCreateDeliberatelyOverlappingPartitions"
c10nn "$b.TestCreateFullThenAddOne    $b.TestCreate12123"
c10nn "$b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE $b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO $b.TestAAADiskClassCreation"
c10nn "$b.TestLogicalPartitions_ONE   $b.TestCreate12123           $b.TestLogicalPartitions_TWO"
c10nn "$b.TestLogicalPartitions_TWO   $b.TestCreate12123           $b.TestLogicalPartitions_ONE"
c10nn "$b.TestCreate12123             $b.TestLogicalPartitions_ONE   $b.TestLogicalPartitions_TWO"
c10nn "$b.TestCreate12123             $b.TestLogicalPartitions_TWO   $b.TestLogicalPartitions_ONE"




"""

