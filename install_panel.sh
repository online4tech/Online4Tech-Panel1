#!/bin/sh
# Online4Tech Panel Direct Installer from GitHub Source
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"
BASE_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"

echo "[Online4Tech] Installing / Updating Online4Tech Panel..."
mkdir -p "$PLUGIN_DIR"

for FILE in __init__.py plugin.py o4t_store.py; do
    wget --no-check-certificate -qO "$PLUGIN_DIR/$FILE" "$BASE_URL/$FILE"
done

chmod -R 755 "$PLUGIN_DIR"
echo "[SUCCESS] Online4Tech Panel Installed! Restarting Enigma2 GUI..."
sleep 2
killall -9 enigma2