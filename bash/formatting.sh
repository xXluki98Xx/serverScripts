#!/bin/bash

echo "Hier können Sie Festplatte schnell und effizient löschen und in ext4 formatieren lassen"
echo
echo "Festplatte formatieren"

# Auslesen der richtigen Festplatte
fdisk -l | grep -e 'Festplatte /dev/' -e 'Disk /dev/'
echo

echo "Bitte geben Sie den gewünschten Laufwerkbezeichner '(sda1)' ein:"
read disk
echo

partition=$disk
disk=$disk | sed 's/[0-9]*//g'

echo "Löschung:"
# löscht die Filesystem Tabelle, aktualisiert den Kernel und startet fdisk
wipefs -a /dev/$disk && sudo partprobe /dev/$disk && sudo fdisk /dev/$disk
echo

echo "Formatierung:"
# Formatiert zu ext4, überprüft die Festplatte und setzt den reservierten Speicher auf 0%
mkfs.ext4 /dev/$partition && sudo fsck -fy /dev/$partition && sudo tune2fs -m 0 /dev/$partition
echo

echo "Herzlichen Glückwunsch"