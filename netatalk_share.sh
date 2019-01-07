#!/bin/bash

# Netatalk Freigabe hinzufügen
answer='j';
if [ $answer == 'j' ]; then
  # Letzte Zeile in der Netatalk-Config liegt
  sudo sed -ie '$d' /etc/netatalk/afpd.conf
  sudo sed -i '$a'"- -tcp -noddp -uamlist uams_dhx.so,uams_dhx2_passwd.so -nosavepassword" /etc/netatalk/afpd.conf
  # Das Ende der Datei (#EOF) löschen
  sudo sed -ie '$d' /etc/netatalk/AppleVolumes.default

  while [ $answer == 'j' ]; do
    echo Bitte geben Sie den Namen der Ordnerfreigabe ein:
    read networkname
    echo

    echo Bitte geben Sie den Pfad zum Ordner ein:
    read path
    echo

    echo Bitte geben Sie die freigegeben Nutzer ein '(User1,User2,... oder @users)':
    read users
    echo

    sudo sed -i '$a'"$path $networkname allow:$users options:upriv perm:0776" /etc/netatalk/AppleVolumes.default
    echo

    echo Wollen Sie eine weitere Freigabe hinzufügen '( j | n )' ?
    read answer
    echo
  done
  # Das Ende der Datei wieder kennzeichnen
  sudo sed -i '$a'"#EOF" /etc/netatalk/AppleVolumes.default
  # Kopieren der Konfigurationsdatei um Daten verlust zu verhindern
  sudo cp /etc/netatalk/AppleVolumes.default /etc/netatalk/AppleVolumes.default.orig
fi
