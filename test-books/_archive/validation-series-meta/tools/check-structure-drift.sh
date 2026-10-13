#!/usr/bin/env bash
# check-structure-drift.sh - flags drift between a book's structural ledgers.
#
# WHY THIS EXISTS
#   foundation.md and outline.md each carry the book's structural spine (the
#   per-chapter ledger, e.g. chronological · catalogue · chorus · ...). Both are
#   LIVING documents, so the two copies can drift apart silently. Book 2's pair did:
#   foundation.md called ch.4 "spiral" while outline.md called it "fragmented", and
#   the Phase 2.8 outline audit - a human read of 22 findings - missed it. A later
#   read caught it. This makes that check mechanical and re-runnable with the gates.
#
# WHAT IT CHECKS
#   The ledger line in each file: the first non-blank line after a line containing
#   "Structural ledger". Backticks and outer whitespace are stripped and internal
#   whitespace is collapsed before comparing. The separator is NOT normalised - if
#   the two files use different separators, that is itself worth seeing.
#
# WHAT IT DOES NOT DO
#   It does not decide WHICH file is right. It does not fail a book that carries the
#   ledger in only one file (Book 1's foundation.md never had one); it reports that
#   case and moves on. It only fails where BOTH files carry a ledger and they differ.
#
#   usage:  tools/check-structure-drift.sh [BOOK_DIR ...]
#           (no argument = every book-*/ containing foundation.md and outline.md)
#   exit 0 = no drift   exit 1 = a drift, or nothing to check

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)

# Print the normalised ledger from one file, or nothing if the file has none.
read_ledger() {
  [ -f "$1" ] || return 0
  awk '
    found && NF { print; exit }
    /Structural ledger/ { found = 1 }
  ' "$1" \
    | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
          -e 's/^`//' -e 's/`$//' \
          -e 's/[[:space:]][[:space:]]*/ /g'
}

books=()
if [ "$#" -gt 0 ]; then
  books=("$@")
else
  for d in "$ROOT"/book-*/; do
    d="${d%/}"
    [ -f "$d/foundation.md" ] && [ -f "$d/outline.md" ] && books+=("$d")
  done
fi

if [ "${#books[@]}" -eq 0 ]; then
  echo "check-structure-drift: no book directory with both foundation.md and outline.md"
  exit 1
fi

drift=0

for b in "${books[@]}"; do
  b="${b%/}"
  name=$(basename "$b")
  f="$b/foundation.md"
  o="$b/outline.md"

  lf=$(read_ledger "$f")
  lo=$(read_ledger "$o")

  if [ -z "$lf" ] && [ -z "$lo" ]; then
    echo "$name: no structural ledger in either file - skipped"
    continue
  fi

  if [ -z "$lf" ] || [ -z "$lo" ]; then
    echo "$name: ledger in only one file - not compared"
    [ -n "$lf" ] && echo "    foundation.md: $lf"
    [ -n "$lo" ] && echo "    outline.md:    $lo"
    continue
  fi

  if [ "$lf" = "$lo" ]; then
    echo "$name: OK - both files carry the same structural ledger"
    echo "    $lo"
  else
    echo "$name: DRIFT - foundation.md and outline.md disagree"
    echo "    foundation.md: $lf"
    echo "    outline.md:    $lo"
    drift=1
  fi
done

echo
if [ "$drift" -eq 0 ]; then
  echo "NO STRUCTURAL DRIFT - the ledgers agree where both files carry one."
  exit 0
fi

echo "STRUCTURAL DRIFT - pick the current ledger, then update the stale copy."
exit 1
