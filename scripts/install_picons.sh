#!/bin/sh
echo "Preparing standard Picon directories..."
mkdir -p /usr/share/enigma2/picon
wget -q --no-check-certificate -O /usr/share/enigma2/picon_default.png "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/assets/picon_default.png"
echo "Online4Tech Default Picon installed!"
