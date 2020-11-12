#!/bin/sh
# By Lukas Ramm

echo Wie heißt lautet ihr username?
read username
echo

echo Wie soll ihr Passwort lauten?
read password
echo

docker run --entrypoint htpasswd registry:2 -Bbn $username "$password" > auth/htpasswd