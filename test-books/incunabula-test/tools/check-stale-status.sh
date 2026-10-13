#!/usr/bin/env bash
# check-stale-status.sh - flags documents that assert a book is both finished and
# unfinished, and reports the ones that only might be.
#
# WHY THIS EXISTS
#   The layer's whole claim is that a later session can trust it without re-deriving
#   anything. Stale status prose breaks that claim directly: a state file whose own
#   fields say the book is delivered, still opening with "STILL NOT DRAFTED", or a
#   ledger whose meta says BOOK 2 DELIVERED still saying "no prose exists". Two such
#   sentences survived the entire Book 2 run. Both were caught by a human read, by no
#   gate. This makes that class mechanical so it is caught by the process instead.
#
# WHAT IT CHECKS
#   Two tiers, because the documents are not the same kind of thing.
#
#   ENFORCED - state and planning documents, the files a later session trusts first:
#     CANON_LEDGER.yaml        */PROJECT_STATE.yaml   */CANON_LEDGER.yaml
#     */ENTITY_STATE.yaml      */foundation.md        */outline.md
#   A hit here is STALE when the file ALSO asserts completion (a status field of
#   complete/completed, a positive drafted_total or manuscript_words, or DELIVERED).
#   A hit with no completion signal is REVIEW. STALE fails.
#
#   ADVISORY - living summaries that narrate history, so a past-tense sentence is
#   normal and must never fail the gate:
#     README.md                */continuity/*.md
#   Every hit here is REVIEW by definition - reported for a human to rule on, never a
#   failure. A check that failed a report for describing what happened would be noise.
#
#   STILL EXCLUDED: maintenance/SESSION_LOG.md, maintenance/PRUNING_LOG.md and
#   artifacts/*. They are pure append-only records; scanning them would flag every
#   honest past-tense sentence. If you want them, pass them explicitly as arguments.
#
#   usage:  tools/check-stale-status.sh [FILE ...]     (default: the files above)
#           --strict   treat REVIEW hits as failures too (including advisory files)
#   exit 0 = nothing stale   exit 1 = a STALE hit (or any hit under --strict)

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)

strict=0
args=()
for a in "$@"; do
  case "$a" in
    --strict) strict=1 ;;
    *) args+=("$a") ;;
  esac
done

# Files that are scanned but can never fail: living summaries and continuity reports.
is_advisory() {
  case "${1#"$ROOT"/}" in
    README.md|*/continuity/*.md) return 0 ;;
    *) return 1 ;;
  esac
}

files=()
if [ "${#args[@]}" -gt 0 ]; then
  files=("${args[@]}")
else
  for f in \
    "$ROOT"/CANON_LEDGER.yaml \
    "$ROOT"/README.md \
    "$ROOT"/book-*/PROJECT_STATE.yaml \
    "$ROOT"/book-*/CANON_LEDGER.yaml \
    "$ROOT"/book-*/ENTITY_STATE.yaml \
    "$ROOT"/book-*/foundation.md \
    "$ROOT"/book-*/outline.md \
    "$ROOT"/book-*/continuity/*.md; do
    [ -f "$f" ] && files+=("$f")
  done
fi

# Phrases that assert work is NOT done. Curated from the defects actually observed in
# this project (not guessed): a series ledger claiming "no prose exists" while its own
# meta says the book was delivered, and a state file opening "STILL NOT DRAFTED" while
# its own fields record seven drafted chapters.
STALE_PHRASES=(
  'no prose exists'
  'still not drafted'
  'not yet drafted'
  'not yet introduced'
  'zero chapters'
  'nothing past phase 0 has run'
  'no research has been run'
  'still not chosen'
)

# Signals that the SAME file claims the work is done. A STALE hit is one that appears
# in an ENFORCED file carrying one of these.
COMPLETION=(
  'status: "?(complete|completed)"?'
  'DELIVERED'
  '(drafted_total|manuscript_words): [1-9]'
  'prose_gate_all_chapters: "?[1-9]'
)

stale=0
review=0
scanned=0

for f in "${files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "missing: $f"
    stale=1
    continue
  fi
  scanned=$((scanned + 1))

  hits=""
  for p in "${STALE_PHRASES[@]}"; do
    m=$(grep -niE "$p" "$f" || true)
    [ -n "$m" ] && hits="${hits}${m}"$'\n'
  done
  [ -z "$hits" ] && continue

  rel=${f#"$ROOT"/}

  if is_advisory "$f"; then
    kind=REVIEW
    why="advisory file (summary/report) - reported, never fails"
  else
    complete=0
    for c in "${COMPLETION[@]}"; do
      grep -qE "$c" "$f" && { complete=1; break; }
    done
    if [ "$complete" -eq 1 ]; then
      kind=STALE
      why="file asserts completion; this prose says otherwise"
      stale=1
    else
      kind=REVIEW
      why="no completion signal in file - historical, or stale?"
      review=1
    fi
  fi

  echo "$kind $rel  ($why)"
  printf '%s' "$hits" | sed 's/^/         /'
done

echo
if [ "$scanned" -eq 0 ]; then
  echo "no documents found - nothing to check"
  exit 1
fi
if [ "$stale" -eq 1 ]; then
  echo "STALE STATUS FOUND - reconcile the file(s) above before trusting them."
  exit 1
fi
if [ "$review" -eq 1 ]; then
  if [ "$strict" -eq 1 ]; then
    echo "REVIEW hits present and --strict is set."
    exit 1
  fi
  echo "No stale status. REVIEW hits above need a human ruling (historical, or stale?)."
  echo "Advisory hits (README, continuity reports) are reported and never fail."
  exit 0
fi
echo "NO STALE STATUS - every checked document agrees with itself."
exit 0
