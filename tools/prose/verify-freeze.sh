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
done < <(grep -oE '`tools/prose/[a-zA-Z0-9_/-]+\.(sh|py|tsv|md)` \| `[0-9a-f]{16}`' "$FREEZE" \
         | sed 's#`tools/prose/##; s/` | `/ /; s/`//g')
[ $rc -eq 0 ] && echo "FREEZE HOLDS - results from these tools are attributable to a known instrument."
exit $rc
