#!/bin/sh
# Safe Online4Tech installer wrapper for KeyAdder.
# Original plugin author: RAED (fairbird). Project license: GPL-3.0.
# The upstream archive is fetched directly; no third-party source is mirrored.
set -eu

SOURCE_URL="https://github.com/fairbird/KeyAdder/archive/refs/heads/main.tar.gz"
TMP_ARCHIVE="/tmp/o4t-keyadder-main.tar.gz"
STAGE="/tmp/o4t-keyadder-stage.$$"
SOURCE_SUBDIR="KeyAdder-main/usr"

cleanup() {
    rm -f "$TMP_ARCHIVE"
    rm -rf "$STAGE"
}
trap cleanup 0 HUP INT TERM

echo "[Online4Tech] Downloading KeyAdder by RAED (fairbird)..."
if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_ARCHIVE" "$SOURCE_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$SOURCE_URL" -o "$TMP_ARCHIVE"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_ARCHIVE" ] || ! tar -tzf "$TMP_ARCHIVE" >/dev/null 2>&1; then
    echo "[ERROR] KeyAdder source archive is missing or invalid."
    exit 1
fi

if ! tar -tzf "$TMP_ARCHIVE" | awk '
    /^\// { bad = 1 }
    /(^|\/)\.\.(\/|$)/ { bad = 1 }
    END { exit bad }
'; then
    echo "[ERROR] The KeyAdder archive contains an unsafe path."
    exit 1
fi

if ! tar -tzf "$TMP_ARCHIVE" | grep -q "KeyAdder-main/usr/lib/enigma2/python/Plugins/Extensions/KeyAdder/"; then
    echo "[ERROR] Expected KeyAdder plugin files were not found in the archive."
    exit 1
fi

mkdir -p "$STAGE"
tar -xzf "$TMP_ARCHIVE" -C "$STAGE"
SOURCE="$STAGE/$SOURCE_SUBDIR"
if [ ! -d "$SOURCE/lib/enigma2/python/Plugins/Extensions/KeyAdder" ]; then
    echo "[ERROR] Extracted KeyAdder plugin directory is missing."
    exit 1
fi

echo "[Online4Tech] Updating KeyAdder files without deleting the existing plugin first..."
mkdir -p /usr
cp -a "$SOURCE/." /usr/
sync

echo "[Online4Tech] KeyAdder installed. Restarting Enigma2 GUI..."
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
