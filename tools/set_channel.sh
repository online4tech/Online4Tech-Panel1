#!/bin/bash
# usage: tools/set_channel.sh stable|dev   - points the files of this tree at one channel (branch)
set -e
cd "$(dirname "$0")/.."
CH="$1"
case "$CH" in stable|dev) ;; *) echo "usage: $0 stable|dev"; exit 1;; esac
echo "$CH" > plugin/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel/channel.txt
sed -i "s|^BRANCH=.*|BRANCH=\"$CH\"|" install.sh
sed -i "s|Online4Tech-Panel1/[a-z0-9-]*/install.sh|Online4Tech-Panel1/$CH/install.sh|g" README.md
echo "channel set to $CH"
