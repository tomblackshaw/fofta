# -*- coding: utf-8 -*-
"""main.py

Created on Oct 16, 2021
@author: Tom Blackshaw

FOFTA - from one filesystem to another!

To fix my SAMBA mount:
    On host:-
        sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.smbd.plist
        sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.smbd.plist
    Then, on guest:-
        bash /etc/rc.local



Example:
    To run a unit test::

        $ python3 -m unittest discover
    ...or...
        $ python3 -m unittest test.test_disktools.test_Disk_class.TestCreateDeliberatelyOverlappingPartitions

    To reformat::

        $ cd .../src && black *.py */*.py */*/*.py */*/*/*.py */*/*/*/*.py

Todo:
    * QQQ Finish me QQQ
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""


import os

# -*- coding: utf-8 -*-
"""test_fructify

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test.test_fructify

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from my.globals import call_binary
from my.exceptions import BlankFileCreationError, DestinationPaddingWriteError, \
            DestinationDeviceTooSmallError, MBRCopyError,\
    FilesystemFormattingError
from my.disktools.disks import Disk






def MAIN_rejig_the_currently_running_ALREADYINUSE_armbian_filesystem(
    source_img_fname, root_FS_format, output_image_fname
):

    pass





def execute_most_of_the_original_script(source, destination, fstype, bootdev, rootdev, old_dev):
    os.system(""""




die() {
# Echo the supplied string to STDERR.
# Then, quit w/ nonzero error code.
#
########
    echo "$1" >> /dev/stderr
    exit 1
}





DESIRED_IMAGE_SIZE_IN_MB=2700

check_our_incoming_parameters_sanity() {
# Validate incoming parameters of this script.
# Abort the script if the parameters aren't valid.
#
########
    for i in zstd mkfs.btrfs mkfs.xfs; do
        which $i > /dev/null || die "Please install $i"
    done 
    if [ ! -f "$source_img_fname" ]; then
        die "Your source image file does not exist"
    elif [ -e "$pooldev" ] && [ "$rootfs_format" == "zfs" ]; then
        die "$pooldev already exists. I cannot support ZFS because of that. Sorry."
    elif [ "$source_img_fname" == "" ] || [ ! -e "$source_img_fname" ]; then
        die "Source image filename (parameter 1) is bogus"
    elif [ "$output_image_fname" == "" ]; then
        die "Output image fname (parameter 2) is bogus"
    elif [ "$rootfs_format" != "ext4" ] && [ "$rootfs_format" != "btrfs" ] && [ "$rootfs_format" != "zfs" ] && [ "$rootfs_format" != "xfs" ]; then
        die "Parameter #2 should be the destination format: btrfs, xfs, or zfs"
    elif ! fdisk -l "$source_img_fname" > /dev/null 2> /dev/null; then
        die "The source image file has no partition table. That is weird. Are you sure it's a valid image?"
    elif fdisk -l "$source_img_fname" | grep $source_img_fname[1-9] | grep -v $source_img_fname"1" > /dev/null; then
        die "The sourfce image file has more than one partition. That is weird. Are you sure it's a pristine Armbian image?"
    elif echo "$i" | grep $source_img_fname[1-9]; then
        die "The source image file has two or more partitions."
    elif mount | grep "$mtpt" > /dev/null; then
        die "Please unmount $mtpt first and then run me again."
    elif mount | grep "$mtpt.old" > /dev/null; then
        die "Please unmount $mtpt.old first and then run me again."
    elif losetup 2> /dev/null | grep "$bootdev"; then
        die "Please free up loopback boot device $bootdev and run me again."
    elif losetup 2> /dev/null | grep "$rootdev"; then
        die "Please free up loopback root device $rootdev and run me again."
    elif losetup 2> /dev/null | grep "$old_dev"; then
        die "Please free up loopback root device $old_dev and run me again."
    elif ! which zfs > /dev/null || ! which zpool > /dev/null; then
        die "Please install ZFS etc. and run me again."
    elif echo "$output_image_fname" | grep -x "/dev/.*" > /dev/null && [ "$(fdisk -l "$output_image_fname" 2> /dev/null | head -n1 | cut -d' ' -f3 | cut -d'.' -f1)" -ge "500" ]; then
        die "I have a sneaking suspicion that $output_image_fname is NOT the device you want me to wipe."
    elif echo "$output_image_fname" | grep -x "/dev/.*" > /dev/null; then
        die "Please do not use /dev/... as an output."
    elif [ ! -e "$bootdev" ] || [ ! -e "$rootdev" ] || [ ! -e "$old_dev" ]; then
        die "Please free up the /dev/loop devices (using losetup -D perhaps) and run me again."
    else
        echo "I shall:-
- make a working copy of the source image file
- save the files and directories therein
- repartition the working copy
- repopulate the filesystem
- install additional tools

Please wait. This might take up to an hour.
"
    fi
}



mkdir_and_mount_dev_tmpfs_etc_on_mtpt() {
# Prepare the chroot jail for proper use. Create and mount
# /dev, /tmp, /run, /proc, /mnt, /media, /sys, etc. Before
# doing that, run an 'unmount' to avoid double-tapping.
#
########
    unmount_dev_tmpfs_etc_on_mtpt
    cd "$mtpt"
    mkdir -p "$mtpt"/{dev,media,mnt,proc,run,sys,tmp}
    chmod 1777 "$mtpt"/tmp || die ".......failed."
    (mount dev dev -t devtmpfs; mount proc proc -t proc; mount sys sys -t sysfs; mount tmp tmp -t tmpfs; mount run run -t tmpfs) || die "...failed to mount dev, sys, etc."
    cd /
}



unmount_dev_tmpfs_etc_on_mtpt() {
# Unmount the dev, proc, etc. folders in the chroot jail.
#
########
    cd /
    umount "$mtpt"/{dev,proc,sys,tmp,run} 2> /dev/null
}



create_a_working_copy_of_the_source_image() {
# If there is an existing & satisfactory copy of the disk image, use it.
# ('Satisfactory' means 'of a sensible length'. We can re-use almost
# any image, as long as it's long enough and is formattable.) If there
# isn't one, take a copy of the source image. Either way, get a workable
# block of formattable bytes & supply it as the working copy. THIS HAS
# NOTHING TO DO WITH COPYING THE FILESYSTEM. We just want to copy the
# boot sector etc. and make sure our working image is long enough.
#
# Oh, and add 1GB of blank data if the image is a fresh copy of the
# original source material. That way, we've extra room for new files.
#
########
    echo -en "Creating a working copy of the source image..."
    echo ""
    src_len=$DESIRED_IMAGE_SIZE_IN_MB
    dd iflag=fullblock status=progress bs=1024k if=/dev/zero of="$output_image_fname".tmp count=$src_len ||die "..Fd" 
    mv "$output_image_fname".tmp "$output_image_fname"                                   || die "........failed"
    dd status=progress iflag=fullblock bs=1024k count=64 conv=notrunc if="$source_img_fname" of="$output_image_fname" &> /dev/null || die "...failed"
}





repartition_and_losetup_our_working_copy() {
# Delete the working copy's old partitions. Install two partitions:
# one that began on the same sector on the new image as it did on
# the source image, and one that occupies the rest of the working
# copy. The first partition (on the working copy) will be 512MB long,
# whereas the first and only partition on the source image will
# take up 1GB or more.
#
########
    echo -en "succeeded.\nRepartitioning our working copy of the source image..."
    [ "$rootfs_format" == "zfs" ] && zpool destroy $POOLNAME > /dev/null 2> /dev/null
    sync;sync;sync;partprobe;sync;sync;sync
    # We derive the old partition info from the SOURCE IMAGE, not the destination image.
    raw_attribs_of_p1=$(fdisk -l "$source_img_fname" | grep $source_img_fname"1"| tr -s '\t' ' ')
    noof_attributes=$(echo "$raw_attribs_of_p1" | wc -w)
    p1_start=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-5)))
    p1_end=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-4)))
    p1_noofsectors=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-3)))
    p1_format=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes)))
    if [ "$p1_format" != "Linux" ]; then
        if [ "$p1_format" == "" ]; then
            die "Are you sure that your source disk image file is a disk image at all? Look into this, please."
        else
            die "For some reason, partition #1 is formatted $p1_format (not Linux). Weird. Look into this, please."
        fi
    fi
    echo -en "p\nd\n4\nd\n3\nd\n2\nd\n1\nd\nd\nn\np\n1\n"$p1_start"\n+512MB\ny\nw\n" | fdisk "$output_image_fname"
    sync;sync;sync;partprobe;sync;sync;sync
    raw_attribs_of_p1=$(fdisk -l "$output_image_fname" | grep $output_image_fname"1"| tr -s '\t' ' ')
    p1_end=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-4)))
    p1_noofsectors=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-3)))
    p2_start=$(($p1_end+1)) || die "Unable to calculate the start of partition #2"
    echo -en "n\np\n2\n"$p2_start"\n\nw\n" | fdisk "$output_image_fname"
    sync;sync;sync;partprobe;sync;sync;sync
    if ! fdisk -l "$output_image_fname" | grep $(basename $output_image_fname)"1" > /dev/null || ! fdisk -l "$output_image_fname" | grep $(basename $output_image_fname)"2" > /dev/null; then
        die ".....failed."
    fi
    sync;sync;sync;partprobe;sync;sync;sync
    echo -en "succeeded.\nFormatting and mounting the partitions..."
    losetup $bootdev -o $(($p1_start*512)) --sizelimit $(($p1_noofsectors*512)) "$output_image_fname"
    losetup $rootdev -o $(($p2_start*512)) "$output_image_fname"
    losetup $old_dev -o $(($p1_start*512)) "$source_img_fname"
}



set_the_new_serialno_of_our_disk_image() {
# Set a new serial number for our disk image.
# Params: <image fname> <serial number>
#
# NB: The serial number MUST BE HEX and MUST NOT include other
#     characters. This includes '0x'. DO NOT INCLUDE 0X!
#
########
    local imgfile=$1 serno=$2 itendedupbeing
    if [ "$imgfile" == "" ] || [ ! -e "$imgfile" ] || [ "$serno" == "" ]; then
        die "set_the_new_serialno_of_our_disk_image() --- bad parameters"
    fi
    echo -en "succeeded.\nChanging the disk image's serial number..."
    echo -en "x\ni\n0x${serno}\nr\np\nw\n" | fdisk $imgfile
    itendedupbeing=$(fdisk -l $imgfile | grep ":.*0x" | head -n1 | tr ' ' '\n' | grep -vx "" | tail -n1)
    [ "$itendedupbeing" == "0x${serno}" ] || die "Failed to set image serial#"
}



format_and_mount_our_wkg_copy_as_EXT4() {
    yes y | mkfs.ext4  -L $rootlbl $rootdev              || die "Failed to format $rootdev ext4"
    fsck -f -p $rootdev
    yes y | mkfs.ext4  -L $rootlbl $rootdev              || die "Failed to format $rootdev ext4"
    mount                    LABEL=$rootlbl "$mtpt"      || die "Failed to mount $mtpt"
    cat << FSTX > $mtpt/.fstab.new
#    device   mountpoint format attributes
LABEL=$bootlbl /boot     ext4  defaults,noatime                                   0 1
LABEL=$rootlbl /         ext4  defaults,noatime                                   0 2
tmpfs /tmp tmpfs defaults,nosuid 0 0
FSTX
}





format_and_mount_our_wkg_copy_as_BTRFS() {
    yes y | mkfs.btrfs -f -L $rootlbl $rootdev           || die "Failed to format $rootdev btrfs"
    yes "" | fsck.btrfs -f $rootdev
    mount -o noatime,compress=zstd $rootdev "$mtpt"
        cd "$mtpt"
    btrfs subvol create @
    btrfs subvol create @home
    btrfs subvol create @var_log
    cd @
    mkdir -p boot home var/log
    btrfs subvolume set-default $(btrfs subvolume list . | head -n1 | cut -d' ' -f2) "$mtpt"
    cd /
    umount "$mtpt"
    mount -o compress=zstd                 LABEL=$rootlbl "$mtpt"                       || die "Failed to mount $mtpt"    
    mount -o compress=zstd,subvol=@home    LABEL=$rootlbl "$mtpt"/home                  || die "Failed to mount home"
    mount -o compress=zstd,subvol=@var_log LABEL=$rootlbl "$mtpt"/var/log               || die "Failed to mount log"
       cat << FSTX > $mtpt/.fstab.new
LABEL=$bootlbl /boot     ext4  defaults,noatime                                   0 1
LABEL=$rootlbl /         btrfs defaults,noatime,compress=zstd,ssd,subvol=@        0 2
LABEL=$rootlbl /home     btrfs defaults,noatime,compress=zstd,ssd,subvol=@home    0 3
LABEL=$rootlbl /var/log/ btrfs defaults,noatime,compress=zstd,ssd,subvol=@var_log 0 4
tmpfs /tmp tmpfs defaults,nosuid 0 0
FSTX
}





format_and_mount_our_wkg_copy_as_XFS() {
    yes y | mkfs.xfs -f -L $rootlbl $rootdev             || die "Failed to format $rootdev"
    yes "" | xfs_repair   $rootdev >> /dev/null 2>> /dev/null
    yes y | mkfs.xfs -f -L $rootlbl $rootdev             || die "Failed to format $rootdev"
    mount                    LABEL=$rootlbl "$mtpt"      || die "Failed to mount $mtpt"
    cat << FSTX > $mtpt/.fstab.new
#    device   mountpoint format attributes
LABEL=$bootlbl /boot     ext4  defaults,noatime                                   0 1
LABEL=$rootlbl /         xfs   defaults,noatime                                   0 2
tmpfs /tmp tmpfs defaults,nosuid 0 0
FSTX
}



format_and_mount_our_wkg_copy_as_ZFS() {
    modprobe zfs || die "Unable to modprobe zfs"
    lsmod | grep zfs > /dev/null || die "Unable to find zfs kernel module"
    pooldev=/dev/mmcblk0p2
    ln -sf $rootdev $pooldev
    UUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)
    poolname=rpool
    zuuidpath=$poolname/ROOT/ubuntu_$UUID
    zrootpath=$poolname/ROOT
    [ ! -e "$pooldev" ] && die "I wanna know what pooldev is... and I want you to show me"
    make_my_zdisk_pool
    cat << FSTX > $mtpt/.fstab.new
LABEL=$bootlbl /boot ext4  defaults,noatime 0 1
tmpfs /tmp tmpfs defaults,nosuid 0 0
FSTX
}



format_and_mount_our_wkg_copy_boot_partition() {
    yes y | mkfs.ext4 -L $bootlbl "$bootdev" || die "failed to format p1"
    mkdir -p "$mtpt"/boot
    mount   LABEL=$bootlbl "$mtpt"/boot || die "Failed to mount $mtpt/boot"
}




format_and_mount_root() {
# Format the 1st partition as ext4 and the 2nd partition as $rootfs_format.
# For later, set $mtpt/.fstab.new reflect the needs of the latter's specific
# filesystem format.
#
########
    case $rootfs_format in
    ext4)
        format_and_mount_our_wkg_copy_as_EXT4
        ;;
    btrfs)
        format_and_mount_our_wkg_copy_as_BTRFS
        ;;
    xfs)
        format_and_mount_our_wkg_copy_as_XFS
        ;;
    zfs)
        format_and_mount_our_wkg_copy_as_ZFS
        ;;
    *)
        die "$rootfs_format is not supported yet"
    esac
}



copy_all_files_from_source_to_working_copy() {
# Assume that the working copy has been mounted already.
# Mount the source image read-only. Copy all files and 
# directoriesto the working copy. Unmount the source
# image.
#
########
    [ "$mtpt" == "" ] && die "mountpoint is blank <== that's not good"
    [ "$mtpt" == "/" ] && die "mountpoint is $mtpt <== that's bad"
    sync;sync;sync
    echo -en "...succeeded.\nMounting source image..."
#    mount | grep "$mtpt " > /dev/null || die "...why haven't you mounted $mtpt (the working copy) yet?"
    mkdir -p "$mtpt".old
    mount "$old_dev" -o ro "$mtpt".old > /dev/null || die "...failed."
    echo -en "...succeeded.\nCopying pristine filesystem across. Please wait.\n"
    sync;sync;sync
    rsync -a --info=progress2 "$mtpt".old/* "$mtpt" || echo "...nonfatal error."
    cd "$mtpt"/var
    rm -Rf lock
    cd /
    sync;sync;sync
    rsync -ai "$mtpt".old/* "$mtpt" || die "....failed."
    echo -en "...succeeded.\nDismounting source image..."
    umount "$old_dev" || die "...failed".
    echo -en "...succeeded.\nUpdating OS..."
}



use_chroot_UandU_SUB() {
    cat << 'EOF' | chroot "$mtpt" /usr/bin/env mtpt=$mtpt rootlbl=$rootlbl rootfs_format=$rootfs_format bash
 my_apt() {
  # https://serverfault.com/questions/48724/100-non-interactive-debian-dist-upgrade
  DEBIAN_FRONTEND=noninteractive APT_LISTCHANGES_FRONTEND=none apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes -o Dpkg::Options::="--force-confdef" -fuy $*
  return $?
 }
 do_update_and_upgrade_thingies() {
  apt-get -fuy --force-yes autoremove || (echo "U01"; exit 1)
  apt-get --force-yes clean           || (echo "U02"; exit 2)
  apt-get -y update                   || (echo "U03"; exit 3)
  my_apt -y install ca-certificates   || (echo "U04"; exit 4)
  apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes \
          -o Dpkg::Options::="--force-confdef" -fuy upgrade ca-certificates      || (echo "U05"; exit 5)
  my_apt -y upgrade ca-certificates      || (echo "U06"; exit 6)
  apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes \
          -o Dpkg::Options::="--force-confdef" -fuy upgrade      || (echo "U07"; exit 7)
  apt-get --force-yes -o Dpkg::Options::="--force-confold" --force-yes \
          -o Dpkg::Options::="--force-confdef" -fuy dist-upgrade     || (echo "U08"; exit 8)
  sync;sync;sync;sleep 1;sync;sync;sync
 }
 add_zfs_stuff() {
  echo "Installing ZFS stuff"
  BRANCH=$(cat /.armbian-release.host | grep BRANCH | cut -d'=' -f2)
  [ "$BRANCH" == "" ] && die "Cannnot deduce BRANCH from host's /etc/armbian-release file"
  . /.armbian-release.host
  . /etc/armbian-release
  INSTALL_PKG="linux-headers-${BRANCH}-${LINUXFAMILY}"
  my_apt install ${INSTALL_PKG} || (echo "DZT1"; exit 1)
  my_apt install dkms fakeroot linux-libc-dev menu debhelper || (echo "DZT2"; exit 2)
  my_apt install zfsutils-linux zfs-initramfs zfs-auto-snapshot zfs-zed zfs-dkms || (echo "DZT3"; exit 3)
  my_apt remove zfs-auto-snapshot ### zfs-dkms zfs-zed
  my_apt install --reinstall zfs-initramfs zfs-dkms zfs-zed || (echo "DZT4"; exit 4)
  apt-mark hold linux-image*
  cp /usr/share/systemd/tmp.mount /etc/systemd/system/
  systemctl enable tmp.mount
 }
 res=0
 apt-get remove apt-listchanges --assume-yes --force-yes          || res=$(($res+1))
 export DEBIAN_FRONTEND=noninteractive
 export APT_LISTCHANGES_FRONTEND=none
 echo 'libc6 libraries/restart-without-asking boolean true' | debconf-set-selections
 find /etc/apt -name "*.list" | xargs sed -i '/^deb/s/wheezy/jessie/g'
 do_update_and_upgrade_thingies                                   || res=$(($res+1))
 my_apt install btrfs-progs xfsprogs busybox-static pv zstd       || res=$(($res+1))
 add_zfs_stuff                                                    || res=$(($res+1))
 echo "Done"
 exit $res
EOF
    return $?
}




use_chroot_to_update_and_enhance_OS() {
# Update and upgrade the working copy's OS. Then, install
# the packages for zfs, btrfs, xfs, etc. Sometimes, the
# package 'zfsutils-linux' throws up an unavoidable
# screen that forces the user to click the OK button.
# To solve this, I'll run a 'kill whiptail' script in
# the background. (It'll kill any whiptail script that
# outstays its welcome.) Then, after installation is
# complete, I kill the script itself. Fun, eh?
#
########
    res=0
    our_random_lockfile=/tmp/$RANDOM$RANDOM$RANDOM
    (
    sleep 30
    while [ -e "$our_random_lockfile" ]; do
    i=0; while [ "$i" -lt "1800" ] && [ -e "$our_random_lockfile" ]; do sleep 1; i=$(($i+1)); done; [ -e "$our_random_lockfile" ] && echo "Killing whiptail" && killall whiptail; done
    ) &
    echo $! > $our_random_lockfile
    cp -f /etc/armbian-release "$mtpt"/.armbian-release.host
    mkdir_and_mount_dev_tmpfs_etc_on_mtpt
    use_chroot_UandU_SUB
    res=$?
    kill $(cat $our_random_lockfile)
    sleep 5
    rm -f   $mtpt/var/cache/apt/archives/*.deb
    unmount_dev_tmpfs_etc_on_mtpt

    res=0
    for f in /boot/armbianEnv.txt /etc/initramfs-tools /boot/uInitrd /usr/share/initramfs-tools/conf.d/zfs /usr/share/doc/zfs-initramfs /usr/share/initramfs-tools/zfsunlock /var/lib/dpkg/info/zfs-initramfs.list; do
        if [ ! -e "$mtpt$f" ]; then
            res=$(($res+1))
            echo "use_chroot_to_update_and_enhance_OS() is being weird. Where is $mtpt$f? Please investigate."
        fi
    done
    [ "$res" -gt "0" ] && die "use_chroot_to_update_and_enhance_OS() --- $res files missing"

    return $missing
}





populate_working_copy() {
    mount | grep " $mtpt " > /dev/null || die "Cannot populate working copy. Mount point $mtpt is not mointed."
    mount | grep " $mtpt/boot " > /dev/null || die "Cannot populate working copy. Mount point $mtpt/boot is not mointed."
    our_fscopy_tarball="$source_img_fname".finalFS.tar.lzo
    if [ -e "$our_fscopy_tarball" ]; then
        echo -en "...succeeded.\nCopying cached filesystem across. Please wait.\n"
        cd "$mtpt"
        dd iflag=fullblock status=progress bs=1024k if="$our_fscopy_tarball" | tar --lzo -x \
                                                                || die "Failed to UTOTBOTFS"
    else
        copy_all_files_from_source_to_working_copy
        use_chroot_to_update_and_enhance_OS || die "Failed to UCTUAUO"
        echo -en "Creating a cache of this upgraded filesystem. Please wait.\n"
        cd "$mtpt"
        tar -c --lzo * | dd iflag=fullblock status=progress bs=1024k of="$our_fscopy_tarball".tmp \
                                                                || die "Failed to create $our_fscopy_tarball"
        mv -f "$our_fscopy_tarball".tmp "$our_fscopy_tarball"   || die "Failed to mv  to $our_fscopy_tarball"
    fi
}







modify_diskresizer_script() {
# Modify /usr/lib/armbian/armbian-resize-filesystem to auto-resize
# p2 (xfs, btrfs, whatever). We need this because the existing
# script doesn't handle our p2 as elegantly as we'd like.
#
########
    cd /
    echo -en "succeeded.\nModifying the disk-resizer script..."
    [ "$mtpt" == "" ] && die "mountpoint is blank <== that's not good"
    [ "$mtpt" == "/" ] && die "mountpoint is $mtpt <== that's bad"
    sync;sync;sync
    myfile=$mtpt/usr/lib/armbian/armbian-resize-filesystem
    if [ ! -e "$myfile.therealone" ]; then
        mv -f $myfile $myfile.therealone
    fi
    sync;sync;sync
    cat << 'EOF' > $myfile
#!/bin/bash
adjust_fdisk() {
 mytempfile=/tmp/$RANDOM$RANDOM.txt
 sfdisk -d $my_disk | sed s/\ $p2_noofsectors/\ $p2_wewantnoofsectors/ > $mytempfile
 sfdisk -f $my_disk < $mytempfile
 sync;sync;sync;partprobe $my_disk
 sleep 1;sync;sync;sync
}
expand_filesystem() {
 tempdir=/tmp/$RANDOM$RANDOM$RANDOM
 mkdir -p $tempdir
 mount $my_second_partition_I_hope $tempdir
 diskformat=$(mount | grep "$my_second_partition_I_hope " | head -n1 | cut -d' ' -f5)
 yes "" | fsck -f $p2dev
 if [ "$diskformat" == "xfs" ]; then
  xfs_growfs -d $p2dev #$tempdir
  xfs_growfs -d /
 elif [ "$diskformat" == "btrfs" ]; then
  btrfs filesystem resize max $tempdir
 elif [ "$diskformat" == "ext4" ]; then
  resize2fs $p2dev
  echo "Unknown filesystem format -- $diskformat"
 fi
 yes "" | fsck -f $p2dev
 umount $tempdir
 rmdir $tempdir
}
do_the_calculations() {
 echo "do_the_calculations() --- starting w/ $my_first_partition_I_hope"
 if [ "$my_first_partition_I_hope" = "" ]; then
  die "SPECIFY THE SECOND PARAMETER - e.g. /dev/sda1 or /dev/mmcblk0p1"
 elif [ ! -e "$my_first_partition_I_hope" ]; then
  die "SPECIFY SECOND PARAMETER THAT EXISTS - e.g. /dev/sda1 or /dev/mmcblk0p1"
 fi
 sync;sync;sync; partprobe; sync;sync;sync
 my_disk=$(echo "$my_first_partition_I_hope" | sed s/[1-9]// | sed s/p//)
 p1dev=$(echo "$my_first_partition_I_hope"   | sed s/[1-9]//)"1"
 p2dev=$(echo "$my_first_partition_I_hope"   | sed s/[1-9]//)"2"
 p3dev=$(echo "$my_first_partition_I_hope"   | sed s/[1-9]//)"3"
 # Most of this was copied across from fructify_an_armbian_distro_image.sh
 raw_attribs_of_p1=$(fdisk -l "$my_disk" | grep "$p1dev" | tr -s '\t' ' ')
 raw_attribs_of_p2=$(fdisk -l "$my_disk" | grep "$p2dev" | tr -s '\t' ' ')
 noof_attributes=$(echo "$raw_attribs_of_p2" | wc -w)
 p1_start=$(      echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-5)))
 p1_end=$(        echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-4)))
 p1_noofsectors=$(echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-3)))
 p1_format=$(     echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes)))
 p1_fmt_hex=$(    echo "$raw_attribs_of_p1" | cut -d' ' -f$(($noof_attributes-1)))
 p2_start=$(      echo "$raw_attribs_of_p2" | cut -d' ' -f$(($noof_attributes-5)))
 p2_end=$(        echo "$raw_attribs_of_p2" | cut -d' ' -f$(($noof_attributes-4)))
 p2_noofsectors=$(echo "$raw_attribs_of_p2" | cut -d' ' -f$(($noof_attributes-3)))
 p2_format=$(     echo "$raw_attribs_of_p2" | cut -d' ' -f$(($noof_attributes)))
 p2_fmt_hex=$(    echo "$raw_attribs_of_p2" | cut -d' ' -f$(($noof_attributes-1)))
 noofsectors=$(fdisk -l "$my_disk" | head -n1 | tr -s ' ' '\n' | tail -n2 | head -n1)
 p2_wewantnoofsectors=$(($noofsectors-$p2_start))
 echo "do_the_calculations() --- leaving"
}
echo "$(date) HIII" >> /boot/hi.txt
cp -f  /.fstab.new /etc/fstab
my_first_partition_I_hope=$(mount | grep " /boot " | head -n1 | cut -d' ' -f1)
my_second_partition_I_hope=$(mount | grep " / " | head -n1 | cut -d' ' -f1)
if ! echo "$my_second_partition_I_hope" | grep /dev/; then
    my_second_partition_I_hope=$(echo $my_first_partition_I_hope | sed s/p1/p2/ | sed s/a1/s2/)
fi
do_the_calculations >> /boot/hi.txt 2>> /boot/hi.txt
# ...generates my_disk as well
echo "my_disk=$my_disk" >> /boot/hi.txt
if cat /etc/fstab | grep xfs; then
 echo "$(date) I shall resize manually for xfs" >> /boot/hi.txt
 adjust_fdisk
 expand_filesystem
elif cat /boot/armbianEnv.txt | grep ZFS; then
 echo "$(date) I shall resize manually for zfs" >> /boot/hi.txt
 pooldev=$(mount | grep " / " | cut -d'/' -f1)
 p3_start=$(($p2_end+1))
 echo "Creating $p3dev (starting at $p3_start) for $pooldev"
 echo -en "n\np\n3\n$p3_start\n\n\nw\n" | fdisk $my_disk
 zpool add $pooldev $p3dev -f
else
  echo "Calling /usr/lib/armbian/armbian-resize-filesystem.therealone $*" >> /boot/hi.txt 2>> /boot/hi.txt
  bash /usr/lib/armbian/armbian-resize-filesystem.therealone $*   >> /boot/hi.txt 2>> /boot/hi.txt
fi
echo "$(date) BYEE" >> /boot/hi.txt
EOF
    chmod +x $myfile
}


rebuild_initramfs() {
    echo -en "succeeded.\nReconfiguring the boot loader..."
    mkdir_and_mount_dev_tmpfs_etc_on_mtpt
    [ "$mtpt" == "" ] && die "mountpoint is blank <== that's not good"
    [ "$mtpt" == "/" ] && die "mountpoint is $mtpt <== that's bad"
    sync;sync;sync
    cd "$mtpt"/boot || die "..failed."
    [ -e "../etc/initramfs-tools" ] || die "Why is /etc/initramfs-tools missing? Is $mtpt/boot even mounted?"
    echo -en "\next4\nbtrfs\nxfs\nzfs\n$rootfs_format\n" >> ../etc/initramfs-tools/modules
    cat << 'EOF' | chroot "$mtpt" bash
res=0
cd /boot
ln -sf . boot
old_kernel_verno=$(ls -l uInitrd | tr ' ' '\n' | tail -n1 | sed s/uInitrd-//)
rm -f initrd uInitrd                   # ...but leave uInitrd-5.10.60-meson64 alone
mkinitramfs -c gzip -o ./initrd $(basename $(ls -d /lib/modules/* | head -n1))             || exit 1
mkimage -C none -A arm -O linux -T ramdisk  -a 0 -e 0 -n initramfs -d ./initrd uInitrd.new || exit 2
ln -sf uInitrd.new uInitrd
rm -f initrd
EOF
    [ "$?" -ne "0" ] && die ".......failed."
    sleep 1;sync;sync;sync
    unmount_dev_tmpfs_etc_on_mtpt
}



adjust_fstab() {
    echo -en "succeeded.\nAdjusting /etc/fstab..."
    cp -f "$mtpt"/.fstab.new "$mtpt"/etc/fstab || die "Unable to find $mtpt/.fstab.new"
}




tweak_armbianEnv_for_me() {
    echo -en "succeeded.\nTweaking armbianEnv.txt..."
    mkdir_and_mount_dev_tmpfs_etc_on_mtpt
    [ ! -e "$mtpt/boot/armbianEnv.txt.GOOD" ] && cp -f $mtpt/boot/armbianEnv.txt $mtpt/boot/armbianEnv.txt.GOOD
    if [ "$rootfs_format" == "zfs" ]; then
        sed -i "s|rootdev=|#rootdev=|" $mtpt/boot/armbianEnv.txt
        sed -i "s|rootfstype=|#rootfstype=|" $mtpt/boot/armbianEnv.txt
        echo -en "rootdev=ZFS=$zuuidpath\ninit_on_alloc=0\n" >> $mtpt/boot/armbianEnv.txt 
    else
        sed -i s/rootdev=.*/rootdev=LABEL=$rootlbl/              $mtpt/boot/armbianEnv.txt
        sed -i s/rootfstype=.*/rootfstype=$rootfs_format/        $mtpt/boot/armbianEnv.txt
    fi
    unmount_dev_tmpfs_etc_on_mtpt
}





adjust_bootup_configuration() {
# Rebuild initrd, uInitd, etc. so that the necessary modules - zfs,
# btrfs, whatever - are present in the initial ram filesystem.
#
########
    [ "$mtpt" == "" ] && (die "mtpt is blank --- ABORTING"; return 1)
    local f
    cd /
    mkdir -p $mtpt/boot
    mount | grep "$mtpt/boot" > /dev/null || mount $bootdev $mtpt/boot
    adjust_fstab
    rebuild_initramfs
    tweak_armbianEnv_for_me
    sleep 1;sync;sync;sync
}



delete_crap_before_unmount() {
    echo -en "succeeded. Wiping unused sectors..."
    rm -f "$mtpt"/var/cache/apt/archives/*.deb
    dd iflag=fullblock if=/dev/zero of="$mtpt"/000 bs=1024k || true
    rm -f "$mtpt"/000
}



catch_and_fix_mysterious_bootwiping_bug() {
    cd $mtpt
    mount | grep "$mtpt/boot" > /dev/null || mount $bootdev $mtpt/boot
    ls $mtpt/boot/armbianEnv.txt > /dev/null || die "NOOO! I MUST NOT BACKUP BOOT! IT IS EMPTY!"
    sync;sync;sync; sleep 1; sync;sync;sync; cd "$mtpt"; tar -c --lzo boot > "$mtpt".boot.tar.lzo; cd /

    echo "Making a backup of my recently installed filesystem"
    cd $mtpt || die "Failed to chdir to $mtpt"
    tar -c --lzo * | dd bs=1024k > /root/p2and1.tar.lzo
    cd /

    mkdir -p       "$mtpt.other"/boot
    mount $bootdev "$mtpt.other"/boot || die "Failed to mount mtpt.other/boot"

    if ! ls "$mtpt.other"/boot/armbianEnv.txt > /dev/null 2> /dev/null; then
        echo -en "A mysterious bug wiped /boot. That's OK, though. I'll fix it..."
        cd "$mtpt.other"; tar --lzo -xf "$mtpt".boot.tar.lzo 2> /dev/null || die "Failed to restore /boot from backup."
        cd /; umount "$mtpt.other"/boot
        mount $bootdev "$mtpt.other"/boot
        ls "$mtpt.other"/boot/armbianEnv.txt > /dev/null && echo -en "yay..." || die "Workaround failed utterly."
    fi
    umount "$mtpt.other"/boot "$mtpt.other" 2> /dev/null
    rmdir "$mtpt.other"/boot "$mtpt.other"
    rm -f "$mtpt".boot.tar.lzo
    cd /
}


unmount_disk_image_and_loopdevs() {
    echo -en "succeeded.\nRunning final check..."
    killall preload 2> /dev/null
    for _ in 1 2 3; do
        for i in $(mount | grep "$mtpt/" | cut -d' ' -f3,4 | tr ' ' '\n' | grep "$mtpt" | sort -r); do umount $i 2> /dev/null; done
        umount $mtpt/{var/log,home,boot} 2> /dev/null
        umount $mtpt/boot 2> /dev/null
        umount $mtpt 2> /dev/null
        sleep 1
    done
    mount | grep "$mtpt" && die "Some $mtpt partitions are still mounted"
    losetup -d $bootdev $rootdev $old_dev || die "Failed to release loopmount devs"
}


sync_and_partprobe() {
    sleep 1;sync;sync;sync;sleep 1
    echo "Running partprobe $1"
    partprobe $1
    sleep 1;sync;sync;sync;sleep 1
}


make_my_zdisk_pool() {
    echo "Making my zdisk pool"
    sync_and_partprobe $diskdev
    wipefs -a $pooldev > /dev/null 2> /dev/null
    zpool destroy $poolname 2> /dev/null
    zpool create \
        -o ashift=12 \
        -O acltype=posixacl -O canmount=off -O compression=lz4 \
        -O dnodesize=auto -O normalization=formD -O relatime=on \
        -O xattr=sa -O mountpoint=/ -R $mtpt $poolname $pooldev
    zpool set autoexpand=on $poolname
    zfs create -o canmount=off -o mountpoint=none $zrootpath
    zfs create -o canmount=noauto -o mountpoint=/ \
        -o com.ubuntu.zsys:bootfs=yes \
        -o com.ubuntu.zsys:last-used=$(date +%s) $zuuidpath
    zfs mount $zuuidpath
    zfs create -o com.ubuntu.zsys:bootfs=no $zuuidpath/srv
    zfs create -o com.ubuntu.zsys:bootfs=no -o canmount=off $zuuidpath/usr
    zfs create $zuuidpath/usr/local
    zfs create -o com.ubuntu.zsys:bootfs=no -o canmount=off $zuuidpath/var
    zfs create $zuuidpath/var/games
    zfs create $zuuidpath/var/lib
    zfs create $zuuidpath/var/lib/AccountsService
    zfs create $zuuidpath/var/lib/apt
    zfs create $zuuidpath/var/lib/dpkg
    zfs create $zuuidpath/var/lib/NetworkManager
    zfs create $zuuidpath/var/log
    zfs create $zuuidpath/var/mail
    zfs create $zuuidpath/var/snap
    zfs create $zuuidpath/var/spool
    zfs create $zuuidpath/var/www
    zfs create -o canmount=off -o mountpoint=/    $poolname/USERDATA
    zfs create -o com.ubuntu.zsys:bootfs-datasets=$zuuidpath \
               -o canmount=on -o mountpoint=/root \
                  $poolname/USERDATA/root_$UUID
    zfs set sync=disabled $poolname
}


do_the_legwork() {
    mkdir -p $mtpt/boot
    mount | grep "$mtpt/boot" > /dev/null || mount $bootdev $mtpt/boot
    mount proc $mtpt/proc -t proc
    mount sys  $mtpt/sys  -t sysfs
    mount dev  $mtpt/dev  -t devtmpfs
    mount tmp  $mtpt/tmp  -t tmpfs
    mount run  $mtpt/run  -t tmpfs
    cat << 'EOF' | chroot $mtpt /usr/bin/env UUID=$UUID poolname=$poolname zuuidpath=$zuuidpath mtpt=$mtpt bash
cp /usr/share/systemd/tmp.mount /etc/systemd/system/
systemctl enable tmp.mount
sleep 1
 mkdir /etc/zfs/zfs-list.cache
 touch /etc/zfs/zfs-list.cache/$poolname
sleep 1
 ln -s /usr/lib/zfs-linux/zed.d/history_event-zfs-list-cacher.sh /etc/zfs/zed.d 2> /dev/null
 zed -F &
 sleep 5
 zfs set canmount=noauto $zuuidpath
# cat /etc/zfs/zfs-list.cache/$poolname
sleep 5
 killall zed
sleep 1
 sed -i "s|.* / .*||" /etc/fstab
 sync;sync;sync
 for f in $(ls /etc/zfs/zfs-list.cache/*); do
  sed -i "s|$mtpt||" $f
 done
EOF
    cd /
    cp -f $mtpt/etc/zfs/zfs-list.cache/$poolname /etc/zfs/zfs-list.cache/
    sleep 1;sync;sync;sync
    umount $mtpt/boot
    sleep 1;sync;sync;sync
    umount $mtpt/{dev,proc,run,sys,tmp}
    sleep 1;sync;sync;sync
    zpool export $poolname
}


###################################################################################################################


aaaa() {
die() { echo "$1" >> /dev/stderr; }
source_img_fname=/root/build_here_on_neo3/source/Armbian_21.08.1_Nanopineo3_focal_current_5.10.60.img
rootfs_format=zfs
output_image_fname=/root/out.$rootfs_format.img
}



source_img_fname="SOURCE_IMG_FNAME"
rootfs_format="ROOTFS_FORMAT"
output_image_fname="OUTPUT_IMAGE_FNAME"
FRUCUUID=$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-z0-9' | cut -c-6)
IMGSERNO=$(printf "%08x" 0x$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-f0-9' | cut -c-8))
bootlbl="$FRUCUUID"Boot
rootlbl="$FRUCUUID"Root
bootdev=BOOTDEVLOOP
rootdev=ROOTDEVLOOP
old_dev=OLD_DEVLOOP
mtpt=/tmp/fructify_mtpt                  #/tmp/my_mtpt_"$FRUCUUID"
mkdir -p "$mtpt"
cd /
pwd="$PWD"
##check_our_incoming_parameters_sanity
##create_a_working_copy_of_the_source_image
##set_the_new_serialno_of_our_disk_image $output_image_fname $IMGSERNO
##repartition_and_losetup_our_working_copy
format_and_mount_root                              ### QQQ ZFS STUFF
format_and_mount_our_wkg_copy_boot_partition
populate_working_copy
modify_diskresizer_script
adjust_bootup_configuration                        ### QQQ ZFS STUFF
[ -e "$mtpt/boot/uInitrd.new" ] || die "$mtpt/boot/uInitrd.new is missing --- weird"
catch_and_fix_mysterious_bootwiping_bug
if [ "$rootfs_format" == "zfs" ]; then
    echo -en "succeeded.\nUpdating the zfs cache (and then unmounting everything)..."
    systemctl stop zed
    do_the_legwork                                 ### QQQ ZFS STUFF
    losetup -D
else
    echo -en "succeeded.\nUnmounting everything..."
    unmount_disk_image_and_loopdevs
fi

cd "$pwd"
echo "succeeded.
Please examine $output_image_fname and see if it is kosher.

To write this to /dev/sda, do this:-
# pv -B 1M $output_image_fname | dd of=/dev/sda bs=1024k
"
exit 0
""".replace(
    'SOURCE_IMG_FNAME', source
    ).replace(
        'OUTPUT_IMAGE_FNAME', destination
        ).replace('ROOTFS_FORMAT', fstype
                  ).replace('ROOTDEVLOOP', rootdev
                            ).replace('BOOTDEVLOOP', bootdev
                                      ).replace('OLD_DEVLOOP', old_dev
                                                ))
                                            

def mkdir_and_mount_dev_tmpfs_etc_on_mtpt(mtpt):
# Prepare the chroot jail for proper use. Create and mount
# /dev, /tmp, /run, /proc, /mnt, /media, /sys, etc. Before
# doing that, run an 'unmount' to avoid double-tapping.
#
########
    unmount_dev_tmpfs_etc_on_mtpt(mtpt)
    res = os.system("""
cd {mtpt}
mkdir -p "{mtpt}"/dev
mkdir -p "{mtpt}"/media
mkdir -p "{mtpt}"/mnt
mkdir -p "{mtpt}"/proc
mkdir -p "{mtpt}"/run
mkdir -p "{mtpt}"/sys
mkdir -p "{mtpt}"/tmp
chmod 1777 "{mtpt}"/tmp
(mount dev dev -t devtmpfs; mount proc proc -t proc; mount sys sys -t sysfs; mount tmp tmp -t tmpfs; mount run run -t tmpfs)
res=$?
cd /
exit $res
""".format(mtpt=mtpt))
    return res



def unmount_dev_tmpfs_etc_on_mtpt(mtpt):
    res = os.system("""
cd /
umount {mtpt}/dev {mtpt}/proc {mtpt}/sys {mtpt}/tmp {mtpt}/run 2> /dev/null
}""".format(mtpt=mtpt))
    return res



def sync_and_partprobe(dev):
    os.system("""
sleep 1;sync;sync;sync;sleep 1
echo "Running partprobe {dev}"
partprobe {dev}
sleep 1;sync;sync;sync;sleep 1
""".format(dev=dev))




def delete_crap_before_unmount(mtpt):
    os.system("""
rm -f "{mtpt}"/var/cache/apt/archives/*.deb
dd iflag=fullblock if=/dev/zero of="{mtpt}"/000 bs=1024k || true
rm -f "{mtpt}"/000
""".format(mtpt=mtpt))



def unmount_disk_image_and_loopdevs(mtpt, bootdev, rootdev, old_dev):
    os.system("""
killall preload 2> /dev/null
for _ in 1 2 3; do
    for i in $(mount | grep "{mtpt}/" | cut -d' ' -f3,4 | tr ' ' '\n' | grep "{mtpt}" | sort -r); do umount $i 2> /dev/null; done
    umount {mtpt}/{var/log,home,boot} 2> /dev/null
    umount {mtpt}/boot 2> /dev/null
    umount {mtpt} 2> /dev/null
    sleep 1
done
mount | grep "{mtpt}" && die "Some {mtpt} partitions are still mounted"
losetup -d {bootdev} {rootdev} {old_dev} || die "Failed to release loopmount devs"
""".format(mtpt=mtpt,bootdev=bootdev,rootdev=rootdev,old_dev=old_dev))


def generate_blank_output_image(source, destination, size_in_MB=None):
    """Create a blank output image on which for me to store the source's contents.

    If there is an existing & satisfactory copy of the disk image, use it.
    ('Satisfactory' means 'of a sensible length'. We can re-use almost
    any image, as long as it's long enough and is formattable.) If there
    isn't one, take a copy of the source image. Either way, get a workable
    block of formattable bytes & supply it as the working copy. THIS HAS
    NOTHING TO DO WITH COPYING THE FILESYSTEM. We just want to copy the
    boot sector etc. and make sure our working image is long enough.
    
    Oh, and add 1GB of blank data if the image is a fresh copy of the
    original source material. That way, we've extra room for new files.

    Example:
        $ generate_blank_output_image('/root/in.img', '/dev/sda')
        $ generate_blank_output_image('/dev/mmcblk0', '/root/out.img', 4000)
        $ generate_blank_output_image('/root/in.img', '/root/out.img', 5000)

    Args:
        source (:obj:`str`): Full path to the input disk or image.
        destination (:obj:`str`): Full path to the output disk or image.
        size_in_MB (int, optional): Desired size of output. If the
            destination is not a disk image, isize_in_MB is ignored.

    Returns:
        None.

    Raises:
        ValueError: Invalid parameters.
    
    Todo:
        * Better TODO lists
        * Don't use global _disks_dct; do something smarter

    """
    # if isize_in_MB is None:
    #     try:
    #         isize_in_MB = 1 + os.path.getsize(source) // 1024 // 1024
    #     except (ValueError, TypeError, FileNotFoundError):
    #         pass
    if source is None or destination is None or not os.path.exists(source) or not os.path.exists(os.path.dirname(destination)):
        raise ValueError("Bad parameters. Please specify sane values for source and destination.")
    if source == destination:
        raise ValueError("Bad parameters. The input name must not be identical to the output.")
    if 0 == os.system('''mount | grep "%s " | grep " %s "''' % (source, destination)) \
    or 0 == os.system('''mount | grep "%s " | grep " %s "''' % (destination, source)):
        raise ValueError("It appears that the source and destination are the same.")
    if not size_in_MB:
        size_in_MB = 200
        print("Befause you didn't specify size_in_MB, I assume that it will be {size_in_MB}MB.".format(size_in_MB=size_in_MB))
    if size_in_MB < 70:
        raise ValueError("The image size will be laughably small.")
    retval, _stdout_txt, stderr_txt=call_binary(['dd', 'iflag=fullblock', 'status=progress', 'bs=1024k', 'if=/dev/zero', 'of=%s' % destination, \
                                           'count=%d' % size_in_MB])
    if retval != 0:
        raise BlankFileCreationError("Unable to write out temp blank file\n{stderr_txt}".format(stderr_txt=stderr_txt))
    if retval != 0:
        raise DestinationDeviceTooSmallError("Destination device is too small for the temp image you've created.")
    retval, _stdout_txt, stderr_txt= call_binary(['dd','status=progress','iflag=fullblock','bs=1024k','count=64',
                                                     'conv=notrunc','if='+source, 'of='+destination])
    if retval != 0:
        raise MBRCopyError( "Failed to copy the master boot record (including boot sector) across.\n%s" % stderr_txt)
    if size_in_MB is not None and not destination.startswith('/dev/') and os.path.getsize(destination)//1024//1024 < size_in_MB:
        retval = os.system('''dd if=/dev/zero bs=1024k count={how_many_MBs} >> "{dest}" 2> /dev/null'''.format(\
                                           how_many_MBs=size_in_MB-os.path.getsize(destination)//1024//1024,\
                                           dest=destination))
        if retval != 0:
            raise DestinationPaddingWriteError("Failed to pad out and rightsize the destination image")



def check_our_incoming_parameters_sanity(source,destination, fstype, pooldev):
    pass
    '''
    if fstype == 'zfs':
        for i in zstd mkfs.btrfs mkfs.xfs; do
            which $i > /dev/null || die "Please install $i"
        done 
    if 
    if [ ! -f "$source_img_fname" ]; then
        die "Your source image file does not exist"
    elif [ -e "$pooldev" ] && [ "$rootfs_format" == "zfs" ]; then
        die "$pooldev already exists. I cannot support ZFS because of that. Sorry."
    elif [ "$source_img_fname" == "" ] || [ ! -e "$source_img_fname" ]; then
        die "Source image filename (parameter 1) is bogus"
    elif [ "$output_image_fname" == "" ]; then
        die "Output image fname (parameter 2) is bogus"
    elif [ "$rootfs_format" != "ext4" ] && [ "$rootfs_format" != "btrfs" ] && [ "$rootfs_format" != "zfs" ] && [ "$rootfs_format" != "xfs" ]; then
        die "Parameter #2 should be the destination format: btrfs, xfs, or zfs"
    elif ! fdisk -l "$source_img_fname" > /dev/null 2> /dev/null; then
        die "The source image file has no partition table. That is weird. Are you sure it's a valid image?"
    elif fdisk -l "$source_img_fname" | grep $source_img_fname[1-9] | grep -v $source_img_fname"1" > /dev/null; then
        die "The sourfce image file has more than one partition. That is weird. Are you sure it's a pristine Armbian image?"
    elif echo "$i" | grep $source_img_fname[1-9]; then
        die "The source image file has two or more partitions."
    elif mount | grep "$mtpt" > /dev/null; then
        die "Please unmount $mtpt first and then run me again."
    elif mount | grep "$mtpt.old" > /dev/null; then
        die "Please unmount $mtpt.old first and then run me again."
    elif losetup 2> /dev/null | grep "$bootdev"; then
        die "Please free up loopback boot device $bootdev and run me again."
    elif losetup 2> /dev/null | grep "$rootdev"; then
        die "Please free up loopback root device $rootdev and run me again."
    elif losetup 2> /dev/null | grep "$old_dev"; then
        die "Please free up loopback root device $old_dev and run me again."
    elif ! which zfs > /dev/null || ! which zpool > /dev/null; then
        die "Please install ZFS etc. and run me again."
    elif echo "$output_image_fname" | grep -x "/dev/.*" > /dev/null && [ "$(fdisk -l "$output_image_fname" 2> /dev/null | head -n1 | cut -d' ' -f3 | cut -d'.' -f1)" -ge "500" ]; then
        die "I have a sneaking suspicion that $output_image_fname is NOT the device you want me to wipe."
    elif echo "$output_image_fname" | grep -x "/dev/.*" > /dev/null; then
        die "Please do not use /dev/... as an output."
    elif [ ! -e "$bootdev" ] || [ ! -e "$rootdev" ] || [ ! -e "$old_dev" ]; then
        die "Please free up the /dev/loop devices (using losetup -D perhaps) and run me again."
    else
        echo "I shall:-
- make a working copy of the source image file
- save the files and directories therein
- repartition the working copy
- repopulate the filesystem
- install additional tools

Please wait. This might take up to an hour.
"
    fi
'''


def repartition_and_losetup_our_working_copy(source, destination, fstype, bootdev, rootdev, old_dev, poolname):
    """
    Delete the working copy's old partitions. Install two partitions:
    one that began on the same sector on the new image as it did on
    the source image, and one that occupies the rest of the working
    copy. The first partition (on the working copy) will be 512MB long,
    whereas the first and only partition on the source image will
    take up 1GB or more.
    """
    if fstype == 'zfs':
        _retcode, _stdout_txt, _stderr_txt = call_binary(['zpool', 'destroy', poolname])
    os.system("sync;sync;sync;partprobe;sync;sync;sync")
    srcd = Disk(source)
    if len(srcd.partitions) == 0:
        raise ValueError("Are you sure that your source disk image file is a disk image at all? Look into this, please.")
    if srcd.partitions[0].format != 'Linux':
        raise ValueError("Are you sure that your source disk image file is a Linux disk image at all? Look into this, please.")
    if srcd.partitions[0].partno != 1:
        raise ValueError("Why is the first partition not partition #1? Look into this, please.")
    disk = Disk(destination)
    disk.delete_all_partitions()
    disk.add_partition(partno=1, start=srcd.partitions[0].start, size_in_MiB=512)
    disk.add_partition(partno=2)
    res = os.system('''
    losetup {bootdev} -o {start1} --sizelimit {size1} "{output_image_fname}"
    losetup {rootdev} -o {start2} --sizelimit {size2} "{output_image_fname}"
    losetup {old_dev} -o {startOLD} "{source_img_fname}"
    '''.format(bootdev=bootdev, rootdev=rootdev, old_dev=old_dev,
                start1=disk.partitions[0].start * disk.sector_size,
                size1=disk.partitions[0].size * disk.sector_size,
                start2=disk.partitions[1].size * disk.sector_size,
                size2=disk.partitions[1].size * disk.sector_size,
                output_image_fname=destination,
                startOLD=srcd.partitions[0].start))
    assert(res==0)



def format_and_mount_our_wkg_copy_as_EXT4(mtpt, bootdev, rootdev, old_dev, bootlbl, rootlbl):
    retcode, _stdout_txt, stderr_txt = call_binary(['bash', '-c', '''
die() {
echo "$1" >> /dev/stderr
exit 1
}
    yes y | mkfs.ext4  -L {rootlbl} {rootdev}              || die "Failed to format {rootdev} ext4"
    fsck -f -p {rootdev}
    yes y | mkfs.ext4  -L {rootlbl} {rootdev}              || die "Failed to format {rootdev} ext4"
    mount                    LABEL={rootlbl} "{mtpt}"      || die "Failed to mount {mtpt}"
    cat << FSTX > {mtpt}/.fstab.new
#    device   mountpoint format attributes
LABEL={bootlbl} /boot     ext4  defaults,noatime                                   0 1
LABEL={rootlbl} /         ext4  defaults,noatime                                   0 2
tmpfs /tmp tmpfs defaults,nosuid 0 0
FSTX
'''.format(mtpt=mtpt, rootlbl=rootlbl, bootlbl=bootlbl, rootdev=rootdev)])
    if retcode != 0:
        raise FilesystemFormattingError("Unable to format&mount our working copy\n" + stderr_txt)


'''
from my.globals import call_binary, generate_random_string
import os
from my.exceptions import BlankFileCreationError, DestinationPaddingWriteError, \
            DestinationDeviceTooSmallError, DestinationImageWriteError, MBRCopyError, \
            FilesystemCopyError, FilesystemFormattingError

from my.disktools.disks import is_this_a_disk, Disk
from my.fructify.mine import execute_most_of_the_original_script
source='/root/Armbian_21.08.1_Nanopineo3_focal_current_5.10.60.img'
destination='/dev/sda'
fstype='ext4'
'''



# def fructify_me(source, destination, fstype, phase):
#     poolname = 'rpool'
#     source_img_fname=source
#     rootfs_format=fstype
#     output_image_fname=destination
#     retcode, stdout_txt, stderr_txt = call_binary(['bash','-c',"""printf "%08x" 0x$(dd if=/dev/urandom bs=1 count=100 2>/dev/null | tr -dc 'a-f0-9' | cut -c-8)"""])
#     if retcode != 0:
#         raise SystemError("Failed to generate a random serial number for disk %s" % destination)
#
#     imgserno = '0x' + stdout_txt
#     frucuuid = 'u' + generate_random_string(5).lower()
#     bootlbl= frucuuid + 'Boot'
#     rootlbl =  frucuuid + 'Root'
#     bootdev = '/devloop3'
#     rootdev = '/dev/loop4'
#     old_dev = '/dev/loop5'
#     mtpt = '/tmp/fructify_mtpt' #/tmp/my_mtpt_"$FRUCUUID"
#     os.system('mkdir "{mtpt}"'.format(mtpt=mtpt))
#     os.system("cd /")
#         # if is_this_a_disk(source) or not os.path.exists(source) or os.path.isdir(source):
#         #     raise ValueError("Please specify a source disk image, e.g. /root/somethingsomething.img.gz or /root/blah.img")
#         # if is_this_a_disk(destination) or os.path.isdir(source):
#         #     raise ValueError("Please specify an output file, e.g. /root/output.img or /root/op.img.xz")
#     generate_blank_output_image(source, destination) 
#     d = Disk(destination)
#     d.myid = imgserno    # set_the_new_serialno_of_our_disk_image $output_image_fname $IMGSERNO
#     repartition_and_losetup_our_working_copy(source, destination, fstype, bootdev, rootdev, old_dev, poolname)
#     execute_most_of_the_original_script(source, destination, fstype, bootdev, rootdev, old_dev)
#
#     # format_and_mount_root(destination, fstype)
#     # format_and_mount_our_wkg_copy_boot_partition(destination, fstype)
#     # populate_working_copy(source, destination)
#     # modify_diskresizer_script(destination)
#     # adjust_bootup_configuration(destination)
#     # [ -e "$mtpt/boot/uInitrd.new" ] || die "$mtpt/boot/uInitrd.new is missing --- weird"
#     # if fstype == 'zfs':
#     #     os.system("systemctl stop zed")
#     #     do_the_legwork()
#     #     losetup -D
#     # else
#     #     echo -en "succeeded.\nUnmounting everything..."
#     #     unmount_disk_image_and_loopdevs
#     # fi
#     # cd "$pwd"
#     # echo "succeeded.
#     # Please examine $output_image_fname and see if it is kosher.
#     #
#     # To write this to /dev/sda, do this:-
#     # # pv -B 1M $output_image_fname | dd of=/dev/sda bs=1024k
#     # "
#     # exit 0
#
#     return 0






# def main(arguments):
#     print("FOFTA --- OS backup and migration tool")
#     if len(arguments) not in (4, 5):
#         print("fofta <input> <output> <ext4|btrfs|xfs|zfs> (<phase>)")
#         sys.exit(254)
#     else:
#         res = fructify_me(source=sys.argv[1], destination=sys.argv[2], fstype=sys.argv[3], \
#                     phase=None if len(arguments) == 4 else sys.argv[4])
#         return res


# if __name__ == "__main__":
#     sys.exit(main(sys.argv))
