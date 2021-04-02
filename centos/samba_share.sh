#!/bin/bash

# Samba Freigaben hinzufügen
answer='j';
while [ $answer == 'j' ]; do
  echo Bitte geben Sie den Namen der Ordnerfreigabe ein:
  read networkname
  echo

  echo Bitte geben Sie einen Kommentar ein:
  read comment
  echo

  echo Bitte geben Sie den Pfad zum Ordner ein:
  read path
  echo

  echo Bitte geben Sie die freigegeben Nutzer ein '(User1,User2,... oder @users)':
  read users
  echo

  echo Ist der Ordner read-only '( yes | no )' ?
  read readonly
  echo

  sudo sed -i '$a\ ' /etc/samba/smb.conf
  sudo sed -i '$a'"[$networkname]" /etc/samba/smb.conf
  sudo sed -i '$a'"  comment = $comment" /etc/samba/smb.conf
  sudo sed -i '$a'"  path = $path" /etc/samba/smb.conf
  sudo sed -i '$a'"  valid user = $users" /etc/samba/smb.conf
  sudo sed -i '$a'"  read only = $readonly" /etc/samba/smb.conf

  echo Soll der Ordner von allen genutzt werden '( j | n )' ?
  read answer
  echo

  if [ $answer == 'j' ]; then
    sudo sed -i '$a'"  force gruop = users" /etc/samba/smb.conf
    sudo sed -i '$a'"  force create mode = 2660" /etc/samba/smb.conf
    sudo sed -i '$a'"  force directory mode = 2770" /etc/samba/smb.conf
  else
    sudo chown $users $path
    sudo chmod 700 -R $path
  fi

  # fügt eine Leerzeile ein
  sudo sed -i '$a\ ' /etc/samba/smb.conf
  # Kopieren der Konfigurationsdatei um Daten verlust zu verhindern
  sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.orig

  echo Wollen Sie eine weitere Freigabe hinzufügen '( j | n )' ?
  read answer
  echo
done
