#!/bin/sh
# Online4Tech Panel - Telnet / SSH installer
#
#   wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/panel-v2/install.sh | sh
#
REPO="online4tech/Online4Tech-Panel1"
BRANCH="panel-v2"
RAW="https://raw.githubusercontent.com/$REPO/$BRANCH"
IPK_URL="$RAW/release/enigma2-plugin-extensions-online4techpanel_all.ipk"
IPK="/tmp/o4t_panel.ipk"
WORK="/tmp/o4t_panel_x"

say() { echo "[Online4Tech] $*"; }
cleanup() { rm -rf "$IPK" "$WORK"; }
fail() { say "ERROR: $*"; cleanup; exit 1; }

[ "$(id -u)" = "0" ] || fail "run as root"
[ -d /usr/lib/enigma2/python/Plugins/Extensions ] || fail "this does not look like an Enigma2 receiver"

cleanup
say "Downloading Online4Tech Panel..."
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O "$IPK" "$IPK_URL" || fail "download failed (check the internet connection)"
elif command -v curl >/dev/null 2>&1; then
    curl -fsSLk -o "$IPK" "$IPK_URL" || fail "download failed (check the internet connection)"
else
    fail "wget/curl not found"
fi
[ -s "$IPK" ] || fail "downloaded file is empty"

say "Installing..."
if command -v opkg >/dev/null 2>&1 && opkg install --force-reinstall --force-overwrite "$IPK" >/tmp/o4t_opkg.log 2>&1; then
    :
else
    say "opkg failed, extracting manually"
    mkdir -p "$WORK" && cd "$WORK" || fail "cannot create $WORK"
    ar x "$IPK" 2>/dev/null || tar -xf "$IPK" 2>/dev/null || fail "invalid package"
    [ -f data.tar.gz ] || fail "invalid package (no data.tar.gz)"
    tar -xzf data.tar.gz -C / || fail "extract failed"
    cd /
fi
DEST="/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel"
[ -f "$DEST/plugin.py" ] || fail "installation failed (see /tmp/o4t_opkg.log)"
chmod -R 755 "$DEST"
find "$DEST" \( -name '*.pyc' -o -name '__pycache__' \) -prune -exec rm -rf {} + 2>/dev/null
cleanup
sync
say "Online4Tech Panel installed OK."

if [ "$O4T_NO_RESTART" = "1" ]; then
    exit 0
fi
say "Restarting Enigma2 in 3 seconds..."
sleep 3
if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service 2>/dev/null | grep -q enigma2; then
    systemctl restart enigma2
else
    killall -9 enigma2
fi
exit 0
