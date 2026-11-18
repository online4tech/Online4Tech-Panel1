#!/bin/bash

# Force remove existing version
echo "Removing current xDreamy..."
rm -rf /usr/share/enigma2/xDreamy
opkg remove --force-depends enigma2-plugin-skins-xDreamy

# Download fresh copy
echo "Downloading xDreamy..."
wget -q --no-check-certificate "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/xDreamy.ipk" -O /tmp/xDreamy_new.ipk

# Force install (ignore version checks)
echo "Installing..."
opkg install --force-reinstall --force-overwrite /tmp/xDreamy_new.ipk

# Cleanup
rm -f /tmp/xDreamy_new.ipk
echo "Please Restart GUI..."
exit
