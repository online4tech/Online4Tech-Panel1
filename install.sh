#!/bin/sh
echo "===================================================="
echo "   Installing Online4Tech Panel v7.5 Gold Edition   "
echo "===================================================="

BASE_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main"
rm -f /tmp/o4t_database.json

if command -v dpkg >/dev/null 2>&1 && [ -f /var/lib/dpkg/status ]; then
    PKG_TYPE="deb"
    PKG_NAME="enigma2-plugin-extensions-online4tech_7.5_all.deb"
else
    PKG_TYPE="ipk"
    PKG_NAME="enigma2-plugin-extensions-online4tech_7.5_all.ipk"
fi

TMP_PKG="/tmp/$PKG_NAME"
PKG_URL="$BASE_URL/$PKG_NAME"
rm -f "$TMP_PKG"

echo "-> Detected System Package Format: [$PKG_TYPE]"
if command -v wget >/dev/null 2>&1; then
    wget --no-check-certificate -qO "$TMP_PKG" "$PKG_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -kLs "$PKG_URL" -o "$TMP_PKG"
fi

if [ ! -s "$TMP_PKG" ]; then
    echo "[!] Download failed! Please check your internet connection."
    exit 1
fi

if [ "$PKG_TYPE" = "deb" ]; then
    dpkg -i --force-overwrite "$TMP_PKG"
    apt-get -f -y install >/dev/null 2>&1
elif command -v opkg >/dev/null 2>&1; then
    opkg install --force-reinstall --force-overwrite "$TMP_PKG"
else
    cd /tmp && ar -x "$TMP_PKG" && tar -xzf /tmp/data.tar.gz -C /
    rm -f /tmp/debian-binary /tmp/control.tar.gz /tmp/data.tar.gz
fi

rm -f "$TMP_PKG"
chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Online4Tech
sync

echo "===================================================="
echo "   Installation Complete! Restarting Enigma2 GUI... "
echo "===================================================="
sleep 2
if command -v systemctl >/dev/null 2>&1 && systemctl list-units | grep -q enigma2; then
    systemctl restart enigma2
else
    killall -9 enigma2 2>/dev/null || (init 4 && sleep 2 && init 3)
fi
exit 0