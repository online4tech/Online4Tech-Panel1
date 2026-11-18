#!/bin/bash
mac=$(ifconfig eth0 | awk '/HWaddr/ {print $5}')
macUrl="https://api.qrserver.com/v1/create-qr-code/?size=512x512&data=https://e2.gosatplus.com/V3?id=${mac}"
wget --no-check-certificate "$macUrl" -O /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/qr.png
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/plugin.py
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/__init__.py
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/plugin_v3.zip
wget --no-check-certificate "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/plugin_v3.zip" -O /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/plugin_v3.zip
unzip -o /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/plugin_v3.zip -d /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/
rm -f /usr/lib/enigma2/python/Plugins/Extensions/GosatPlus/plugin_v3.zip
reboot
