#!/bin/bash

# get ip address
echo "please enter ip address"
read ipaddress
echo

# get subnet
echo "please enter subnet"
read subnet
echo

network="$ipaddress/$subnet"

# just current or all devices
echo "show all (a) or current active (c)"
read answer
echo

if [ $answer == 'a' ]; then
    nmap -sL -R $network | \grep --invert-match "Nmap scan report for ${ipaddress:0:3}"
fi

if [ $answer == 'c' ]; then
    nmap -sn $network | \grep --invert-match "Host is up"
fi