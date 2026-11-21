#!/bin/sh
# Online4Tech item-specific installer for Klll-Pro-FHD.
# Original skin/payload credit: Biko-73.
# The payload remains hosted by its original author; Online4Tech maintains
# this safe wrapper. Existing skin files are updated in place, never pre-deleted.
set -eu

PAYLOAD_URL="https://raw.githubusercontent.com/biko-73/zelda77/main/klll-pro-v.3.3.tar.gz"
TMP_ARCHIVE="/tmp/o4t-klll-pro-v3.3.tar.gz"

cleanup() {
    rm -f "$TMP_ARCHIVE"
}
trap cleanup 0 HUP INT TERM

echo "[Online4Tech] Downloading Klll-Pro-FHD (original payload by Biko-73)..."

if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_ARCHIVE" "$PAYLOAD_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$PAYLOAD_URL" -o "$TMP_ARCHIVE"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_ARCHIVE" ]; then
    echo "[ERROR] Klll-Pro payload download failed."
    exit 1
fi

if ! tar -tzf "$TMP_ARCHIVE" >/dev/null 2>&1; then
    echo "[ERROR] The downloaded Klll-Pro archive is invalid."
    exit 1
fi

echo "[Online4Tech] Installing skin files without deleting the existing skin first..."
tar -xzf "$TMP_ARCHIVE" -C /

sync
echo "[Online4Tech] Klll-Pro-FHD files installed. Restarting Enigma2 GUI..."

if command -v systemctl >/dev/null 2>&1; then
    if systemctl restart enigma2.service 2>/dev/null || systemctl restart enigma2 2>/dev/null; then
        exit 0
    fi
fi

if command -v init >/dev/null 2>&1; then
    init 4
    sleep 3
    init 3
else
    echo "[INFO] Please restart the Enigma2 GUI manually."
fi

exit 0
