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
# The prose checks are separate and per-target: tools/deslop-check.sh on a chapter,
# and tools/validate-controls.sh for the scanner's calibration.

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

step "structural-ledger drift (foundation.md vs outline.md)" bash "$HERE/check-structure-drift.sh"
step "stale status assertions (state and planning files)"     bash "$HERE/check-stale-status.sh"
step "document registry integrity (coverage, refs, archive)"  "$PYTHON" "$HERE/check-docs.py"

echo "==================================================================="
if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASS - the documents and the ledgers agree."
  exit 0
fi
echo "CHECK FAILURE - reconcile before calling the gate passed. See DOC_POLICY.md."
exit 1
