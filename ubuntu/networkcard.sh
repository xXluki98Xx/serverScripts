#!/bin/bash

# Anzeige der Netzwerkkarten
ifconfig -a
echo
echo Wie lautet die Netzwerkschnittstelle '(eth0/ enp2s0/ ..)' ?
read newNetcard

# da standart mäßig enp oder eth bezeichnungen gewählt werden/ wurden, nimmt man diese alte Bezeichnung und tauscht Sie mit der neuen
oldNetcard=$(cat /etc/network/interfaces | grep -Eo -m 1 "enp.{3}")
if [ "$oldNetcard" == "" ]; then
  oldNetcard=$(cat /etc/network/interfaces | grep -Eo -m 1 "eth.{1}")
fi

# Tausche die alte Schnittstelle mit der neuen aus
sudo sed -i s/"$oldNetcard"/"$newNetcard"/g /etc/network/interfaces
# Startet die Netzwerkschnittstelle neu
sudo /etc/init.d/networking stop && sudo ifdown $newNetcard && sudo ifup $newNetcard && sudo /etc/init.d/networking start
