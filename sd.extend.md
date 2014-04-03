#turn off swap
sudo apt-get remove dphys-swapfile

#move home and /var/log to external usb
#make 2 new partitions, then
sudo mkfs.ext4 /dev/sda1
sudo mkfs.ext4 /dev/sda2

and add to /etc/fstab

/dev/sda1	/var/log	ext4	defaults,noatime	0	1
/dev/sda2	/home		ext4	defaults,noatime	0	1

#mv /tmp to ram
sudo vi /etc/default/tmpfs
RAMTMP=yes

#turn off journalling (had to do on another computer)
sudo tune2fs -O ^has_journal /dev/sdb6
sudo tune2fs -O ^has_journal /dev/sdb3
