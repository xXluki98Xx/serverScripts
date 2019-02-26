#!/bin/bash

# RSA-Anmeldung
echo "Hiermit wird die Anmeldung über RSA-Aktiviert, danach ist die Anmeldung mittels SSH nur noch mit dem Registrierten RSA-Key möglich."

# Aktiviert die Anmeldung mittels RSA
sudo sed -i s/'#AuthorizedKeysFile'/'AuthorizedKeysFile'/g /etc/ssh/sshd_config
# Schaltet die SSH-Kennwort Anmeldung aus
sudo sed -i s/'#PasswordAuthentication yes'/'PasswordAuthentication no'/g /etc/ssh/sshd_config
