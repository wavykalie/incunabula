#!/usr/bin/env bash
# run-checks.sh - the combined documentation gate.
#
# Runs every documentation-integrity check and reports one combined status. This is
# what a phase gate and a run close invoke; see DOC_POLICY.md for the workflow the
# checks serve and for how a finding is reconciled.
#
#   usage:  tools/run-checks.sh
#   exit 0 = every check passed   exit 1 = at least one failed
#
# Each check prints its own detail. A REVIEW-only note never fails this gate.
#
# The prose checks are separate and per-target, and all three are required:
#   tools/deslop-check.sh      one chapter at a time, against per-1k caps
#   tools/check-uniformity.py  a whole manuscript, comparing chapters to each other
#   tools/check-drift.py       a whole manuscript, comparing the first half to the last
#   tools/validate-controls.sh the calibration controls for all of the above
#
# They answer different questions and none of them subsumes another. deslop-check
# cannot see uniformity at all - it never holds two chapters at once. Neither
# cross-chapter gate can see a bad sentence. And uniformity and drift are opposites:
# one fails a book whose chapters are too alike, the other fails a book that stops
# being like itself. A book passes the prose gate only when all three are green.

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON="${PYTHON:-python}"

fail=0

step() {
  local name="$1"
  shift
  echo "==================================================================="
  echo "## $name"
  echo "==================================================================="
  if "$@"; then
    echo "-- PASS  $name"
  else
    echo "-- FAIL  $name"
    fail=1
  fi
  echo
}

# The ledger check defaults to */book-*/, which is right for a project holding several
# books and wrong for a single-book project, where the book IS the project directory.
# Called bare it found nothing, reported "no book directory", and exited 1 - so this
# gate failed unconditionally on every single-book project regardless of the ledgers.
# Pass the project root so the check looks at this project's own two files.
step "structural-ledger drift (foundation.md vs outline.md)" bash "$HERE/check-structure-drift.sh" "$HERE/.."
step "stale status assertions (state and planning files)"     bash "$HERE/check-stale-status.sh"
step "document registry integrity (coverage, refs, archive)"  "$PYTHON" "$HERE/check-docs.py"

# Uniformity is a prose check but it is cross-chapter, so it belongs here rather than
# in the per-chapter scanner: this is the gate that runs at a phase boundary, and a
# manuscript whose chapters are all the same length should not pass one.
if [ -f "$HERE/check-uniformity.py" ]; then
  step "cross-chapter uniformity (length, rhythm, coda, frames, paragraph layout)" "$PYTHON" "$HERE/check-uniformity.py"
fi

# Drift is the mirror of uniformity: it fails a book whose voice changes between the
# first chapter and the last. Same reason for being here - it needs the whole book.
if [ -f "$HERE/check-drift.py" ]; then
  step "cross-chapter voice drift (stylometric, first half vs second)" "$PYTHON" "$HERE/check-drift.py"
fi

echo "==================================================================="
if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASS - the documents and the ledgers agree."
  exit 0
fi
echo "CHECK FAILURE - reconcile before calling the gate passed. See DOC_POLICY.md."
exit 1
