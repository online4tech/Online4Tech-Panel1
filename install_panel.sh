#!/bin/sh
# Compatibility entry point. The canonical installer handles package detection,
# archive validation, safe installation, and a graceful Enigma2 restart.
set -eu

INSTALLER_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/install.sh"
TMP_INSTALLER="/tmp/o4t-panel-installer.$$"

cleanup() {
    rm -f "$TMP_INSTALLER"
}
trap cleanup 0 HUP INT TERM

echo "[Online4Tech] Starting the official 7.5 package installer..."

if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_INSTALLER" "$INSTALLER_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$INSTALLER_URL" -o "$TMP_INSTALLER"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_INSTALLER" ]; then
    echo "[ERROR] Could not download the official installer."
    exit 1
fi

/bin/sh "$TMP_INSTALLER"
