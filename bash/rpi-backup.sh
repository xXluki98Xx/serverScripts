#!/bin/bash

# Auslesen der richtigen Festplatte
fdisk -l | grep -e 'Festplatte /dev/' -e 'Disk /dev/'

echo ''
echo 'which disk? (just sdX)'
read disk

# Auslesen des Rechner Namens
echo ''
echo 'please enter the title for the backup image:'
read title

echo ''

targetPath="$PWD/$title"_"$(date +'%Y-%m-%d').img"
echo "target file: $targetPath"
# dd if=/dev/$disk of=$targetPath status=progress

dd bs=4M if=/dev/$disk status=progress | gzip > "$targetPath.gz"