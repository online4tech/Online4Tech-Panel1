#!/bin/sh
echo "===================================================="
echo "   Installing Online4Tech Panel v7.5 Gold Edition   "
echo "===================================================="

IPK_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/enigma2-plugin-extensions-online4tech_7.5_all.ipk"
TMP_IPK="/tmp/enigma2-plugin-extensions-online4tech_7.5_all.ipk"

rm -f "$TMP_IPK" /tmp/o4t_database.json

if command -v wget >/dev/null 2>&1; then
    wget --no-check-certificate -qO "$TMP_IPK" "$IPK_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -kLs "$IPK_URL" -o "$TMP_IPK"
fi

if [ ! -s "$TMP_IPK" ]; then
    echo "[!] Download failed! Please check your internet connection."
    exit 1
fi

if command -v opkg >/dev/null 2>&1; then
    opkg install --force-reinstall --force-overwrite "$TMP_IPK"
else
    cd /tmp && ar -x "$TMP_IPK" && tar -xzf /tmp/data.tar.gz -C /
    rm -f /tmp/debian-binary /tmp/control.tar.gz /tmp/data.tar.gz
fi

rm -f "$TMP_IPK"
chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Online4Tech
sync

echo "===================================================="
echo "   Installation Complete! Restarting Enigma2 GUI... "
echo "===================================================="
sleep 2
killall -9 enigma2 2>/dev/null || init 4 && sleep 2 && init 3
exit 0