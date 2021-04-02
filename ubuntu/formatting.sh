#!/bin/bash

echo Hier können Sie Festplatte schnell und effizient löschen und in ext4 formatieren lassen
echo
echo Festplatte formatieren

sudo fdisk -l
echo

echo Bitte geben Sie den gewünschten Laufwerkbezeichner '(sda1)' ein:
read disk
echo

echo Löschung:
# löscht die Filesystem Tabelle, aktualisiert den Kernel und startet fdisk
sudo wipefs -a /dev/${disk%?} && sudo partprobe /dev/${disk%?} && sudo fdisk /dev/${disk%?}
echo

echo Formatierung:
# Formatiert zu ext4, überprüft die Festplatte und setzt den reservierten Speicher auf 0%
sudo mkfs.ext4 /dev/$disk && sudo fsck -fy /dev/$disk && sudo tune2fs -m 0 /dev/$disk
echo

echo Herzlichen Glückwunsch
