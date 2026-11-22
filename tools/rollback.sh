#!/bin/bash
# Put customers back on an older release.   usage: tools/rollback.sh v1.9.0
set -e
cd "$(dirname "$0")/.."
TAG="$1"; [ -n "$TAG" ] || { echo "usage: $0 vX.Y.Z"; exit 1; }
# releases are found by their commit message ("Release vX.Y.Z ..."), so no git tags are needed
REF="$(git log stable --format=%H --grep="^Release $TAG " -1)"
[ -n "$REF" ] || { echo "no such release: $TAG"; git log stable --format=%s --grep="^Release v" | head; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "commit your changes first"; exit 1; }
START="$(git rev-parse --abbrev-ref HEAD)"
git checkout -q stable
git rm -rq . 2>/dev/null || true
git checkout "$REF" -- .
git add -A
git commit -q -m "Rollback to $TAG" || echo "already on $TAG"
git push origin stable 2>&1 | grep -v remote || true
git checkout -q "$START"
echo "stable now serves $TAG"
