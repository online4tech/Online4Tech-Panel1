#!/bin/sh
# Online4Tech Panel - Telnet / SSH installer
#
#   wget -q --no-check-certificate -O - https://raw.githubusercontent.com/YOUR_GITHUB_USER/Online4Tech-Panel/main/install.sh | sh
#
REPO="YOUR_GITHUB_USER/Online4Tech-Panel"
BRANCH="main"
NAME="Online4TechPanel"
DEST="/usr/lib/enigma2/python/Plugins/Extensions/$NAME"
TMP="/tmp/o4t_install"
URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"

say() { echo "[Online4Tech] $*"; }
fail() { say "ERROR: $*"; rm -rf "$TMP" /tmp/o4t_install.tar.gz; exit 1; }

[ "$(id -u)" = "0" ] || fail "run as root"
[ -d /usr/lib/enigma2/python/Plugins/Extensions ] || fail "this does not look like an Enigma2 receiver"

say "Downloading..."
rm -rf "$TMP" /tmp/o4t_install.tar.gz
mkdir -p "$TMP" || fail "cannot create $TMP"
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O /tmp/o4t_install.tar.gz "$URL" || fail "download failed (check internet)"
elif command -v curl >/dev/null 2>&1; then
    curl -fsSLk -o /tmp/o4t_install.tar.gz "$URL" || fail "download failed (check internet)"
else
    fail "wget/curl not found"
fi

say "Extracting..."
tar -xzf /tmp/o4t_install.tar.gz -C "$TMP" || fail "archive is corrupt"
SRC=$(ls -d "$TMP"/*/plugin/usr/lib/enigma2/python/Plugins/Extensions/$NAME 2>/dev/null | head -n 1)
[ -n "$SRC" ] && [ -f "$SRC/plugin.py" ] || fail "plugin files not found in archive"

say "Installing to $DEST"
rm -rf "$DEST"
cp -r "$SRC" "$DEST" || fail "copy failed"
chmod -R 755 "$DEST"
find "$DEST" -name '*.pyc' -delete 2>/dev/null
find "$DEST" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null

rm -rf "$TMP" /tmp/o4t_install.tar.gz
sync
say "Installed Online4Tech Panel OK"
say "Restarting Enigma2 in 3 seconds..."
sleep 3
if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service 2>/dev/null | grep -q enigma2; then
    systemctl restart enigma2
else
    killall -9 enigma2
fi
exit 0
