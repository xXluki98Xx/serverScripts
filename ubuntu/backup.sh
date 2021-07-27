#!/bin/bash

# Auslesen der richtigen Festplatte
disk=$(df /home/ | grep -Eo "/dev/.{3}")

# Auslesen des Rechner Namens
title=$(cat /etc/hosts | grep 127.0.1.1)
title="${title##*1}"

sudo dd if=/dev/$disk of=/path/to/folder/$title_$(date +'%Y-%m-%d').img status=progress
