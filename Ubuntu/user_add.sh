#!/bin/bash

# Nutzer hinzufügen
answer='j';
while [ $answer == 'j' ]; do
  echo Bitte geben Sie den Benutzernamen ein:
  read name
  echo

  sudo  adduser $name --ingroup users --no-create-home --disabled-login --gecos "" --shell /bin/false
  echo

  echo Wollen Sie einen weiteren Benutzer hinzufügen '( j | n )' ?
  read answer
  echo
done
