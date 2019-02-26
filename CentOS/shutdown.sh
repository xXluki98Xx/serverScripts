#!/bin/bash

# festplatten in /home/Server/ auslesen, ohne swap, nur die /dev/sd verweise raussuchen
anzDisks=$(df -h | grep /home/Server/ | grep -v /home/Server/swap | grep -Eoc "/dev/sd.{2}")
disks=$(df -Th | grep /home/Server/ | grep -v /home/Server/swap | grep ext4 | grep -Eo "/dev/sd.{2}")

i=0;
while [ "$i" != "$anzDisks" ]; do
  # löscht das erste auftreten von /dev/ von vorn
  disks="${disks#*/dev/}"
  # löscht alle auftreten von /dev/ von hinten
  disk="${disks%%/dev/*}"

  # gemounteten Ordner zur Festplatte herrausfinden
  folder=$(df -h /dev/$disk)
  folder="${folder#*/home/Server/}"

  # # Laufwerk aushängen
  # sudo umount /dev/$disk
  #
  # # das problem ist, das fsck ein terminal dialog braucht
  # sudo fsck -f /dev/$disk
  #
  # # Laufwerk eingängen
  # sudo mount /home/Server/$folder

  # testet das Laufwerk auf benötigung von defragmentierung
  defrag=$(sudo e4defrag -c /dev/$disk)
  defrag=$(echo "$defrag" | grep -o "does not need")

  sudo e4defrag -c /dev/$disk
  # Überprüft die Festplatte / den Pfad ob eine Defragmentierung notwendig/ sinnvoll ist
  if [ "$defrag" != "does not need" ]; then
    # Wenn es notwendig/ sinnvoll ist, führt es die defragmentierung aus
    sudo e4defrag -v /dev/$disk
  else
    echo
    echo Disk /dev/$disk braucht keine Defragmentierung
    echo ;
  fi

  i=$[$i +1]
done

# Ende
sudo shutdown -h now
