#!/bin/bash
# Publish the current dev tree to customers (the stable channel).
# usage: tools/promote.sh            (run from a clean checkout of dev)
set -e
cd "$(dirname "$0")/.."
[ "$(git rev-parse --abbrev-ref HEAD)" = "dev" ] || { echo "switch to the dev branch first"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "commit your changes on dev first"; exit 1; }
VER="$(tr -d ' \n' < version.txt)"
SHA="$(git rev-parse --short HEAD)"
git fetch -q origin || true
if git show-ref --verify -q refs/heads/stable; then git checkout -q stable; else git checkout -q -b stable; fi
git rm -rq . 2>/dev/null || true
git checkout dev -- .
tools/set_channel.sh stable
bash build_ipk.sh | tail -1
git add -A
git commit -q -m "Release v$VER (promoted from dev $SHA)" || echo "nothing new to release"
git tag "v$VER" >/dev/null
git push origin stable 2>&1 | grep -v remote || true
git push origin "v$VER" 2>&1 | grep -v remote || true
git checkout -q dev
echo "stable is now v$VER"
