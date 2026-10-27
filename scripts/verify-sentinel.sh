#!/usr/bin/env bash
# Record the working tree `make verify` just passed on, as the short git tree id
# ~/.claude/hooks/review-gate.sh compares against before allowing a commit.
# Must compute the same value as that hook's compute_diff_hash.
set -euo pipefail
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT
git read-tree --index-output="$dir/index" HEAD
GIT_INDEX_FILE="$dir/index" git add -A
mkdir -p .claude
GIT_INDEX_FILE="$dir/index" git write-tree | cut -c1-16 > .claude/.last-verify-passed
