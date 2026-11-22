#!/bin/bash
# usage: tools/bump.sh 1.9.1   - sets the panel version everywhere
set -e
cd "$(dirname "$0")/.."
[[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "usage: $0 X.Y.Z"; exit 1; }
sed -i "s|^BASE_VERSION = .*|BASE_VERSION = \"$1\"|" plugin/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel/version.py
echo "$1" > version.txt
echo "version $1"
