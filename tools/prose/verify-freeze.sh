#!/usr/bin/env bash
# Check the live tools against GATE_FREEZE.md. Exit 0 = the freeze holds, 1 = it moved.
# A gate that changed after a book was generated makes that book a test against an
# instrument nobody can name, so this is worth running before trusting any old result.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# tools/prose -> tools -> incunabula. GATE_FREEZE.md sits at the project root, which is
# the parent of `tools`, NOT the parent of `prose`. Getting this wrong pointed the check
# at tools/GATE_FREEZE.md and reported "no freeze" on a freeze that exists.
ROOT="$(cd "$HERE/../.." && pwd)"
FREEZE="$ROOT/GATE_FREEZE.md"
[ -f "$FREEZE" ] || { echo "no GATE_FREEZE.md at $FREEZE"; exit 1; }
rc=0
# Only the MANIFEST region is scanned - the lines above the first `## Freeze` heading.
# The history below it is full of `file` | `old-hash` cells ("what this was at Freeze
# N"), and the naive grep this replaced read those as live claims: it reported CHANGED
# against hashes that were stale by design and could never pass again, so every freeze
# entry permanently broke the guard. A guard crying wolf is worse than no guard. Found
# 2026-10-08 while verifying Freeze 21; see that entry in GATE_FREEZE.md.
rows=$(awk '/^## Freeze/{exit} {print}' "$FREEZE" \
       | grep -oE '`tools/prose/[a-zA-Z0-9_/-]+\.(sh|py|tsv|md)` \| `[0-9a-f]{16}`' \
       | sed 's#`tools/prose/##; s/` | `/ /; s/`//g')
# Zero rows scanned is a FAILURE, not a pass - the same rule the controls suite uses
# against a scanner that globs no files.
[ -n "$rows" ] || { echo "no manifest rows found in $FREEZE - refusing to call this a hold"; exit 1; }
# Completeness guard (2026-10-13): the scan above only reads the manifest region,
# which is right - the history below is full of old-hash cells. But a frozen row
# RECORDED outside that region is then frozen in fact and unchecked in fact, which
# is how Freeze 5's and Freeze 13's seven rows went unchecked for five and nine
# days. So: every manifest-shaped row anywhere in the file (a tools/prose path, one
# hash, and a role cell that is NOT another hash - the history tables carry
# old|new hash PAIRS and are excluded by that shape) must name a file the scan
# above actually checked. A row the glob cannot parse trips this the same way.
frozen_rows=$(awk -F'|' '{
  for (i = 2; i <= 4; i++) gsub(/^[ \t\r]+|[ \t\r]+$/, "", $i)
  if ($2 ~ /^`tools\/prose\/.+`$/ && $3 ~ /^`[0-9a-f]{16}`$/ && $4 !~ /^`[0-9a-f]{16}`$/) {
    gsub(/`/, "", $2); print $2
  }
}' "$FREEZE" | sort -u)
checked_rows=$(printf '%s\n' "$rows" | awk '{print "tools/prose/" $1}' | sort -u)
unchecked=$(comm -23 <(printf '%s\n' "$frozen_rows") <(printf '%s\n' "$checked_rows"))
if [ -n "$unchecked" ]; then
  echo "frozen rows this verifier cannot see - recorded outside the manifest region,"
  echo "or in a shape the scanner does not read. Frozen in fact, unchecked in fact:"
  printf '%s\n' "$unchecked" | sed 's/^/  /'
  echo "Move the row into the manifest region (above the first '## Freeze' heading)."
  rc=1
fi
while read -r name want; do
  f="$HERE/$name"
  [ -f "$f" ] || { printf '%-24s MISSING\n' "$name"; rc=1; continue; }
  got=$(sha256sum "$f" | cut -c1-16)
  if [ "$got" = "$want" ]; then
    printf '%-24s %s  ok\n' "$name" "$got"
  else
    printf '%-24s %s  CHANGED (frozen %s)\n' "$name" "$got" "$want"
    rc=1
  fi
done <<< "$rows"
[ $rc -eq 0 ] && echo "FREEZE HOLDS - results from these tools are attributable to a known instrument."
exit $rc
