#!/bin/sh
# Safe Online4Tech package wrapper for the Levi45 Emulator.
# Original package distribution: Emil Nabil / download-plugins.
# Existing package files are not pre-deleted and force-overwrite is not used.
set -eu

BASE_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/levi45emulator"
TMP_PKG="/tmp/o4t-levi45emulator.$$"

cleanup() {
    rm -f "$TMP_PKG"
}
trap cleanup 0 HUP INT TERM

if command -v dpkg >/dev/null 2>&1 && [ -f /var/lib/dpkg/status ]; then
    PKG_NAME="enigma2-plugin-extensions-levi45emulator_all.deb"
    PKG_TYPE="dpkg"
elif command -v opkg >/dev/null 2>&1; then
    PKG_NAME="enigma2-plugin-extensions-levi45emulator_all.ipk"
    PKG_TYPE="opkg"
else
    echo "[ERROR] No supported package manager found (dpkg/opkg)."
    exit 1
fi

PKG_URL="$BASE_URL/$PKG_NAME"
echo "[Online4Tech] Downloading Levi45 Emulator package from Emil Nabil..."
if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_PKG" "$PKG_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$PKG_URL" -o "$TMP_PKG"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_PKG" ]; then
    echo "[ERROR] Levi45 package download failed."
    exit 1
fi

ARCHIVE_MAGIC="$(dd if="$TMP_PKG" bs=8 count=1 2>/dev/null || true)"
if [ "$ARCHIVE_MAGIC" != "!<arch>" ]; then
    echo "[ERROR] Downloaded Levi45 package is not a valid IPK/DEB archive."
    exit 1
fi

echo "[Online4Tech] Installing package without removing the existing plugin first..."
if [ "$PKG_TYPE" = "dpkg" ]; then
    dpkg -i "$TMP_PKG"
else
    opkg install --force-reinstall "$TMP_PKG"
fi

sync
echo "[Online4Tech] Levi45 Emulator package installed. Restarting Enigma2 GUI..."
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
