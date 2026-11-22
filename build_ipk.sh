#!/bin/bash
# Build release/enigma2-plugin-extensions-online4techpanel_all.ipk  (needs: ar, tar, gzip)
set -e
cd "$(dirname "$0")"
VER="$(tr -d ' \n' < version.txt)"
CH="$(tr -d ' \n' < plugin/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel/channel.txt)"
[ "$CH" = "dev" ] && VER="$VER-dev" || CH="stable"
PKG="enigma2-plugin-extensions-online4techpanel"
OUT="release"
W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT

mkdir -p "$W/data" "$W/control" "$OUT"
cp -r plugin/usr "$W/data/"
find "$W/data" \( -name '__pycache__' -o -name '*.pyc' \) -prune -exec rm -rf {} + 2>/dev/null || true

cat > "$W/control/control" <<CTL
Package: $PKG
Version: $VER
Architecture: all
Maintainer: Online4Tech
Section: extra
Priority: optional
Homepage: https://github.com/online4tech/Online4Tech-Panel1/tree/$CH
Description: Online4Tech Panel - latest plugins and skins panel for Enigma2 (Python 2/3)
CTL
cat > "$W/control/postinst" <<'SH'
#!/bin/sh
echo "Online4Tech Panel installed. Restart the GUI to use it."
exit 0
SH
cat > "$W/control/postrm" <<'SH'
#!/bin/sh
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel
exit 0
SH
chmod 755 "$W/control/postinst" "$W/control/postrm"

echo "2.0" > "$W/debian-binary"
(cd "$W/data" && tar --owner=0 --group=0 -czf "$W/data.tar.gz" .)
(cd "$W/control" && tar --owner=0 --group=0 -czf "$W/control.tar.gz" .)
(cd "$W" && ar -r "$OLDPWD/$OUT/${PKG}_all.ipk" debian-binary control.tar.gz data.tar.gz >/dev/null)
echo "built $OUT/${PKG}_all.ipk"
