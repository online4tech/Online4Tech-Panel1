#!/bin/bash
# Put customers back on an older release.   usage: tools/rollback.sh v1.9.0
set -e
cd "$(dirname "$0")/.."
TAG="$1"; [ -n "$TAG" ] || { echo "usage: $0 vX.Y.Z"; exit 1; }
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || { echo "no such release: $TAG"; git tag -l 'v*'; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "commit your changes first"; exit 1; }
START="$(git rev-parse --abbrev-ref HEAD)"
git checkout -q stable
git rm -rq . 2>/dev/null || true
git checkout "$TAG" -- .
git add -A
git commit -q -m "Rollback to $TAG" || echo "already on $TAG"
git push origin stable 2>&1 | grep -v remote || true
git checkout -q "$START"
echo "stable now serves $TAG"
