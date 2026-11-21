#!/bin/sh
# Online4Tech safe installer for Ciefp community plugins.
# Original plugin code remains hosted by its author, ciefp.
# This wrapper validates the archive and updates files in place without
# pre-deleting the installed plugin directory or force-restarting Enigma2.
set -eu

if [ "$#" -lt 2 ]; then
    echo "[ERROR] Usage: install_ciefp_plugin.sh REPOSITORY PLUGIN_PATH [auto|py2|py3] [none|pillow] [any|openpli]"
    exit 1
fi

REPO="$1"
PLUGIN_PATH="$2"
if [ "$#" -ge 3 ]; then PYTHON_MODE="$3"; else PYTHON_MODE="auto"; fi
if [ "$#" -ge 4 ]; then EXTRA_DEP="$4"; else EXTRA_DEP="none"; fi
if [ "$#" -ge 5 ]; then IMAGE_MODE="$5"; else IMAGE_MODE="any"; fi

case "$REPO" in
    ""|*[!A-Za-z0-9_-]*)
        echo "[ERROR] Invalid repository name."
        exit 1
        ;;
esac

case "$PLUGIN_PATH" in
    /usr/lib/enigma2/python/Plugins/Extensions/*|/usr/lib64/enigma2/python/Plugins/Extensions/*)
        ;;
    *)
        echo "[ERROR] Refusing an unexpected plugin path."
        exit 1
        ;;
esac

case "$PYTHON_MODE" in auto|py2|py3) ;; *) echo "[ERROR] Invalid Python mode."; exit 1 ;; esac
case "$EXTRA_DEP" in none|pillow) ;; *) echo "[ERROR] Invalid dependency option."; exit 1 ;; esac
case "$IMAGE_MODE" in any|openpli) ;; *) echo "[ERROR] Invalid image requirement."; exit 1 ;; esac

PLUGIN_NAME="$(basename "$PLUGIN_PATH")"
ARCHIVE_ROOT="$REPO-main"
ARCHIVE_URL="https://github.com/ciefp/$REPO/archive/refs/heads/main.tar.gz"
TMP_ARCHIVE="/tmp/o4t-$REPO-main.tar.gz"
STAGE="/tmp/o4t-$REPO-stage-$$"

cleanup() {
    rm -f "$TMP_ARCHIVE"
    rm -rf "$STAGE"
}
trap cleanup 0 HUP INT TERM

if [ "$IMAGE_MODE" = "openpli" ]; then
    if ! grep -qi "openpli" /etc/issue /etc/image-version /etc/oe-release 2>/dev/null; then
        echo "[ERROR] This plugin variant is marked for OpenPLi images only."
        exit 1
    fi
fi

if [ "$PYTHON_MODE" = "auto" ]; then
    if command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "^Python 3"; then
        PYTHON_MODE="py3"
    elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "^Python 2"; then
        PYTHON_MODE="py2"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_MODE="py3"
    elif command -v python2 >/dev/null 2>&1; then
        PYTHON_MODE="py2"
    else
        echo "[ERROR] No Python interpreter was found."
        exit 1
    fi
fi

if [ "$PYTHON_MODE" = "py3" ]; then
    if ! command -v python3 >/dev/null 2>&1 && ! (command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "^Python 3"); then
        echo "[ERROR] This plugin variant requires Python 3."
        exit 1
    fi
    PACKAGES="python3-requests python3-six"
    if [ "$EXTRA_DEP" = "pillow" ]; then PACKAGES="$PACKAGES python3-pillow"; fi
else
    if ! command -v python2 >/dev/null 2>&1 && ! (command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "^Python 2"); then
        echo "[ERROR] This plugin variant requires Python 2."
        exit 1
    fi
    PACKAGES="python-requests"
    if [ "$EXTRA_DEP" = "pillow" ]; then PACKAGES="$PACKAGES python-imaging"; fi
fi

echo "[Online4Tech] Downloading $REPO from the original ciefp repository..."
if command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_ARCHIVE" "$ARCHIVE_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -fLsS "$ARCHIVE_URL" -o "$TMP_ARCHIVE"
else
    echo "[ERROR] Neither wget nor curl is available."
    exit 1
fi

if [ ! -s "$TMP_ARCHIVE" ] || ! tar -tzf "$TMP_ARCHIVE" >/dev/null 2>&1; then
    echo "[ERROR] The $REPO source archive is missing or invalid."
    exit 1
fi

if ! tar -tzf "$TMP_ARCHIVE" | awk '
    /^\// { bad = 1 }
    /(^|\/)\.\.(\/|$)/ { bad = 1 }
    END { exit bad }
'; then
    echo "[ERROR] The source archive contains an unsafe absolute or parent path."
    exit 1
fi

if ! tar -tzf "$TMP_ARCHIVE" | grep -Fq "$ARCHIVE_ROOT/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME/"; then
    if ! tar -tzf "$TMP_ARCHIVE" | grep -Fq "$ARCHIVE_ROOT/usr/lib64/enigma2/python/Plugins/Extensions/$PLUGIN_NAME/"; then
        echo "[ERROR] The expected plugin folder was not found in the source archive."
        exit 1
    fi
fi

mkdir -p "$STAGE"
tar -xzf "$TMP_ARCHIVE" -C "$STAGE"
SOURCE_USR="$STAGE/$ARCHIVE_ROOT/usr"
if [ ! -d "$SOURCE_USR" ]; then
    echo "[ERROR] The extracted usr directory is missing."
    exit 1
fi

echo "[Online4Tech] Preparing Python dependencies: $PACKAGES"
if [ -f /var/lib/dpkg/status ] && command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y $PACKAGES
elif command -v opkg >/dev/null 2>&1; then
    opkg update
    opkg install $PACKAGES
else
    echo "[ERROR] No supported package manager was found."
    exit 1
fi

# Preserve common user-managed data files before updating plugin code.
PRESERVE_DIR="$STAGE/o4t-preserved-user-data"
EXISTING_PLUGIN_PATH=""
if [ -d "/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME" ]; then
    EXISTING_PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
elif [ -d "/usr/lib64/enigma2/python/Plugins/Extensions/$PLUGIN_NAME" ]; then
    EXISTING_PLUGIN_PATH="/usr/lib64/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
fi

if [ -n "$EXISTING_PLUGIN_PATH" ]; then
    mkdir -p "$PRESERVE_DIR"
    find "$EXISTING_PLUGIN_PATH" -type f \(
        -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.json" \
        -o -name "*.db" -o -name "*.sqlite" -o -name "*.key" -o -name "SoftCam.Key" \
        -o -name "*.m3u" -o -name "*.m3u8" -o -name "*.txt" -o -name "*.list" \
        -o -name "*.dat" -o -name "*.xml" -o -name "*.yaml" -o -name "*.yml" \
    \) -print | while IFS= read -r USER_FILE; do
        RELATIVE_FILE="$(printf '%s\n' "$USER_FILE" | sed "s#^$EXISTING_PLUGIN_PATH/##")"
        DEST_FILE="$PRESERVE_DIR/$RELATIVE_FILE"
        mkdir -p "$(dirname "$DEST_FILE")"
        cp -p "$USER_FILE" "$DEST_FILE"
    done
fi

# Resolve the exact plugin folder in the downloaded source tree. The 39
# maintained Ciefp repositories were checked individually: their usr/ payloads
# are contained in their own Enigma2 Extensions plugin directory.
INSTALL_PLUGIN_PATH="$PLUGIN_PATH"
SOURCE_PLUGIN="$STAGE/$ARCHIVE_ROOT$PLUGIN_PATH"

if [ ! -d "$SOURCE_PLUGIN" ]; then
    case "$PLUGIN_PATH" in
        /usr/lib/enigma2/*)
            INSTALL_PLUGIN_PATH="$(printf '%s\n' "$PLUGIN_PATH" | sed 's#^/usr/lib/#/usr/lib64/#')"
            ;;
        /usr/lib64/enigma2/*)
            INSTALL_PLUGIN_PATH="$(printf '%s\n' "$PLUGIN_PATH" | sed 's#^/usr/lib64/#/usr/lib/#')"
            ;;
    esac
    SOURCE_PLUGIN="$STAGE/$ARCHIVE_ROOT$INSTALL_PLUGIN_PATH"
fi

if [ ! -d "$SOURCE_PLUGIN" ]; then
    echo "[ERROR] The exact plugin directory was not found in the source archive."
    exit 1
fi

echo "[Online4Tech] Updating only $PLUGIN_NAME; preserving all existing plugin files..."
mkdir -p "$INSTALL_PLUGIN_PATH"
cp -a "$SOURCE_PLUGIN/." "$INSTALL_PLUGIN_PATH/"

# Restore user-managed files over packaged defaults, when they existed before.
if [ -n "$EXISTING_PLUGIN_PATH" ] && [ -d "$PRESERVE_DIR" ]; then
    cp -a "$PRESERVE_DIR/." "$EXISTING_PLUGIN_PATH/"
fi
sync

if [ ! -d "$INSTALL_PLUGIN_PATH" ]; then
    echo "[ERROR] Plugin files were copied, but the expected plugin directory is not present."
    exit 1
fi

echo "[Online4Tech] $REPO installed. Restarting Enigma2 GUI gracefully..."
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
