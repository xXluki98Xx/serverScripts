#!/bin/bash

# Änderung des Server Namens
echo '| !!! | Bitte wenn möglich nur direkt angemeldet | !!! |'
echo
echo '   'Wollen Sie den Namen des Servers ändern '( j | n )' ?
echo
echo '| !!! | Bitte wenn möglich nur direkt angemeldet | !!! |'
echo
read answer
echo

if [ $answer == 'j' ]; then
  echo Wie soll der Server heißen?
  read newName
  echo

  oldName=$(cat /etc/hostname)
  echo Alter Name: $oldName
  echo Neuer Name: $newName

  # Ersetzt den alten Namen durch den Neuen
  sudo sed -i s/"$oldName"/"$newName"/g /etc/hosts
  # überschreibt die Datei mit dem neuem Hostname
  sudo sed -i s/"$oldName"/"$newName"/g /etc/hostname
  # übernimmt den neuen Hostname der Maschine
  sudo hostname -F /etc/hostname
  echo
fi
