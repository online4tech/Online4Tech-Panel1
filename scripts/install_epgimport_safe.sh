#!/bin/sh
# Safe Online4Tech wrapper for EPGImport-99.
# Original IPK distribution: Emil Nabil / download-plugins.
# This package is IPK/opkg-only in the referenced upstream repository.
# Existing plugin files are not manually removed before package installation.
set -eu

PACKAGE_NAME="enigma2-plugin-extensions-epgimport"
PACKAGE_FILE="${PACKAGE_NAME}_1.0.ipk"
PACKAGE_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/${PACKAGE_FILE}"
TMP_PACKAGE="/tmp/o4t-${PACKAGE_FILE}"

cleanup() {
    rm -f "$TMP_PACKAGE"
}
trap cleanup 0 HUP INT TERM

if ! command -v opkg >/dev/null 2>&1; then
    echo "[ERROR] The verified upstream package is IPK/opkg-only; this receiver does not provide opkg."
    exit 1
fi

echo "[Online4Tech] Downloading EPGImport package from Emil Nabil..."
if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_PACKAGE" "$PACKAGE_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$PACKAGE_URL" -o "$TMP_PACKAGE"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_PACKAGE" ]; then
    echo "[ERROR] EPGImport package download failed."
    exit 1
fi

ARCHIVE_MAGIC="$(dd if="$TMP_PACKAGE" bs=8 count=1 2>/dev/null || true)"
if [ "$ARCHIVE_MAGIC" != "!<arch>" ]; then
    echo "[ERROR] Downloaded EPGImport file is not a valid IPK archive."
    exit 1
fi

echo "[Online4Tech] Installing without manually removing the existing EPGImport directory..."
opkg install --force-reinstall "$TMP_PACKAGE"
sync

echo "[Online4Tech] EPGImport package installed. Restart Enigma2 GUI to apply changes."
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
