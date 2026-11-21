#!/bin/sh
# Online4Tech safe installer for Abertis Auto Switcher PRO.
# Original package and plugin are maintained by prof-abdo.
# Pinned to release v1.9.24 and verified with the published SHA-256 digests.
# This wrapper never removes an existing plugin directory and never force-overwrites packages.
set -eu

PACKAGE="enigma2-plugin-extensions-abertisautoswitcher"
VERSION="1.9.24"
BASE_URL="https://github.com/prof-abdo/Abertis-Auto-Switcher-PRO/releases/download/v1.9.24"
TMP_FILE="/tmp/o4t-abertis-$$"

cleanup() {
    rm -f "$TMP_FILE"
}
trap cleanup EXIT HUP INT TERM

die() {
    echo "[Online4Tech] ERROR: $*" >&2
    exit 1
}

if [ "$(id -u)" != "0" ]; then
    die "Run this installer as root."
fi

if [ ! -d /usr/lib/enigma2/python/Plugins/Extensions ]; then
    die "Enigma2 plugin directory was not found."
fi

if [ "${1:-}" = "--remove" ]; then
    if command -v dpkg >/dev/null 2>&1; then
        if dpkg-query -W -f='${Status}' "$PACKAGE" 2>/dev/null | grep -q "install ok installed"; then
            dpkg -r "$PACKAGE"
        else
            echo "[Online4Tech] Package is not installed."
        fi
    elif command -v opkg >/dev/null 2>&1; then
        if opkg status "$PACKAGE" 2>/dev/null | grep -q "Status:.*installed"; then
            opkg remove "$PACKAGE"
        else
            echo "[Online4Tech] Package is not installed."
        fi
    else
        die "Neither dpkg nor opkg is available."
    fi
    exit 0
fi

if [ "$#" -ne 0 ]; then
    die "Usage: install_abertis_auto_switcher.sh [--remove]"
fi

if command -v dpkg >/dev/null 2>&1; then
    FILE="${PACKAGE}_${VERSION}_all.deb"
    URL="$BASE_URL/$FILE"
    EXPECTED="2fdf10d5c86886a66a526852077d2c79172a3c5d56e095a7a7e157d8abd9c8e1"
    MANAGER="dpkg"
elif command -v opkg >/dev/null 2>&1; then
    FILE="${PACKAGE}_${VERSION}_all.ipk"
    URL="$BASE_URL/$FILE"
    EXPECTED="24d19a93808e958bbe5efc8e17e86e8af7643cdc1e2ebe5c1ceb2006698667c5"
    MANAGER="opkg"
else
    die "Neither dpkg nor opkg is available."
fi

if command -v wget >/dev/null 2>&1; then
    wget -q -O "$TMP_FILE" "$URL" || die "Package download failed."
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS --connect-timeout 20 --max-time 300 "$URL" -o "$TMP_FILE" || die "Package download failed."
else
    die "Neither wget nor curl is available."
fi

[ -s "$TMP_FILE" ] || die "Downloaded package is empty."
command -v sha256sum >/dev/null 2>&1 || die "sha256sum is required to verify the package."
ACTUAL="$(sha256sum "$TMP_FILE" | awk '{print $1}')"
[ "$ACTUAL" = "$EXPECTED" ] || die "SHA-256 verification failed; package was not installed."

if command -v ar >/dev/null 2>&1; then
    ar t "$TMP_FILE" >/dev/null 2>&1 || die "Downloaded file is not a valid Debian archive."
fi

echo "[Online4Tech] Installing verified Abertis Auto Switcher PRO v$VERSION using $MANAGER..."
if [ "$MANAGER" = "dpkg" ]; then
    dpkg -i "$TMP_FILE"
else
    opkg install "$TMP_FILE"
fi

echo "[Online4Tech] Installation command completed."
echo "[Online4Tech] No plugin directory was pre-deleted and no forced overwrite was used."
echo "[Online4Tech] Restart the Enigma2 GUI manually when convenient."
