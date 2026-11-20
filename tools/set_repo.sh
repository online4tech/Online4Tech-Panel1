#!/bin/sh
# Usage: tools/set_repo.sh YourUser/YourRepo
# Replaces the YOUR_GITHUB_USER/Online4Tech-Panel placeholder everywhere.
[ -n "$1" ] || { echo "usage: $0 user/repo"; exit 1; }
cd "$(dirname "$0")/.." || exit 1
grep -rl --exclude-dir=.git 'YOUR_GITHUB_USER/Online4Tech-Panel' . | while read -r f; do
    sed -i "s#YOUR_GITHUB_USER/Online4Tech-Panel#$1#g" "$f"
done
echo "repo set to $1"
