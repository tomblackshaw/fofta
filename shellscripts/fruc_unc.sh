#!/bin/bash
#
# /usr/local/bin/fructify_an_armbian_distro_image.sh
#
# > /usr/local/bin/fructify_an_armbian_distro_image.sh; nano /usr/local/bin/fructify_an_armbian_distro_image.sh; chmod +x /usr/local/bin/fructify_an_armbian_distro_image.sh
#
# Example:
#     t=zfs; if=/root/bu*/sou*/Arm*_Nanopineo3*f*curr*5.10.60.img; of=/root/out.$t.img; fructify_an_armbian_distro_image.sh $if $t $of && pv -B 1M $of | dd bs=1024k of=/dev/sd_
#
# 2021/09/18
#     first proper iteration
# ...
#
# 2021/10/08
#     zfs works
#
#####################################################################################
#
# To install ZFS, try:-
#     apt -y install zfsutils-linux zfs-initramfs zfs-auto-snapshot zfs-zed \
#                    busybox-static busybox dkms zfs-dkms dkms fakeroot \
#                    linux-libc-dev menu debhelper
#     for i in $(dpkg -S /lib/modules/* | cut -d':' -f1); do apt -y install $(echo "$i" | sed s/image/headers/); done
#     apt -y remove  zfs-dkms zfs-zed zfs-auto-snapshot
#     apt -y install zfs-dkms zfs-zed
#
#####################################################################################




if [ "$#" -ne "3" ]; then
    die "
     $0 <incoming image filename> <btrfs|zfs|xfs|ext4> <output image filename>

e.g. $0 /root/armbian.img btrfs /root/out.img

"
fi




DESIRED_IMAGE_SIZE_IN_MB=2700












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



