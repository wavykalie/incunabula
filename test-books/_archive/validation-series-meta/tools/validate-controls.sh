#!/usr/bin/env bash
# validate-controls.sh - the Prose Gate's own check.
#
# The caps in tools/deslop-check.sh are only meaningful if the scanner still
# discriminates. This re-runs the controls the caps were derived from and refuses
# to report success unless all of them behave the way the calibration predicts.
#
#   usage:  tools/validate-controls.sh
#   exit 0 = all controls behaved as predicted   exit 1 = a control misbehaved
#
#   HUMAN_CORPUS / SLOP_FIXTURE / AI_CONTROL override the three control paths.
#   The AI control is skipped with a note when its path is absent, so this runs
#   in a project that has no such control.
#
# | # | Control                          | Kind            | Must be          |
# |---|----------------------------------|-----------------|------------------|
# | 1 | Elaina, 48 narrative docs        | human           | 0 failing rows   |
# | 2 | calibration/slop-fixture.md      | synthetic slop  | FAIL             |
# | 3 | Coldbrook, 11 final chapters     | AI-written      | some fail, some pass |
#
# A control that scans zero files is a FAILURE, not a pass. That is not
# hypothetical: directory mode used to glob only *.md, so the corpus control
# matched nothing and reported PASS without running a single check.
#
# See calibration/CALIBRATION.md for the caps, the method, and the raw numbers.

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
SCANNER="$HERE/deslop-check.sh"
HUMAN_CORPUS="${HUMAN_CORPUS:-$HERE/calibration/corpus/elaina}"
SLOP_FIXTURE="${SLOP_FIXTURE:-$HERE/calibration/slop-fixture.md}"
AI_CONTROL="${AI_CONTROL:-$HERE/../../Coldbrook Junction/manuscript/chapters}"

[ -f "$SCANNER" ] || { echo "missing scanner: $SCANNER"; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Emit "<path> <verdict>" for one scanner run. A file counts as failed if any FAIL
# row appears under its "== path" header. The path is taken whole, not as $2: these
# project paths contain spaces, and splitting on whitespace silently truncated them.
tally() {
  awk '
    /^== /   {
               if (seen) print path " " (bad ? "FAIL" : "pass")
               path = $0
               sub(/^== /, "", path)
               sub(/ +\\([0-9]+ words\\)$/, "", path)
               bad = 0; seen = 1; next
             }
    /   FAIL/ { bad = 1 }
    END      { if (seen) print path " " (bad ? "FAIL" : "pass") }
  ' "$1"
}

verdicts=0

echo "=== Control 1/3: human prose must all pass (negative control)"
echo "    $HUMAN_CORPUS"
if [ ! -d "$HUMAN_CORPUS" ]; then
  echo "    FAIL  control corpus not found; cannot validate the caps"
  verdicts=1
else
  bash "$SCANNER" "$HUMAN_CORPUS" >"$TMP/human.txt" 2>&1
  tally "$TMP/human.txt" >"$TMP/human.tally"
  h_n=$(wc -l <"$TMP/human.tally" | tr -d ' ')
  h_f=$(grep -c " FAIL$" "$TMP/human.tally" || true)
  echo "    scanned $h_n documents, $h_f failing"
  if [ "$h_n" -eq 0 ]; then
    echo "    FAIL  empty scan - a control that reads zero files proves nothing"
    verdicts=1
  elif [ "$h_f" -gt 0 ]; then
    echo "    FAIL  published human prose is failing the scanner. The caps are too tight."
    grep " FAIL$" "$TMP/human.tally" | head -10 | sed 's/^/          /'
    verdicts=1
  else
    echo "    ok    every document inside the caps"
  fi
fi

echo
echo "=== Control 2/3: synthetic slop must fail (positive control)"
echo "    $SLOP_FIXTURE"
if [ ! -f "$SLOP_FIXTURE" ]; then
  echo "    FAIL  fixture not found; the scanner could be blind"
  verdicts=1
else
  bash "$SCANNER" "$SLOP_FIXTURE" >"$TMP/slop.txt" 2>&1
  s_status=$?
  s_rows=$(grep -c "   FAIL" "$TMP/slop.txt" || true)
  if [ "$s_status" -eq 0 ]; then
    echo "    FAIL  the fixture passed. The scanner is not detecting slop."
    verdicts=1
  elif [ "$s_rows" -eq 0 ]; then
    echo "    FAIL  fixture failed but reported no failing rows (exit $s_status)"
    verdicts=1
  else
    echo "    ok    FAIL with $s_rows failing rows"
  fi
fi

echo
echo "=== Control 3/3: AI-written prose must not all pass (discrimination control)"
echo "    $AI_CONTROL"
if [ ! -d "$AI_CONTROL" ]; then
  echo "    skip  no AI-written control at that path (set AI_CONTROL= to point at one)"
else
  # Final chapters only. -report and -pre-disruption files are working drafts,
  # not published prose, and would skew the pass rate.
  mkdir -p "$TMP/ai"
  cp "$AI_CONTROL"/chapter-*.md "$TMP/ai/" 2>/dev/null
  for f in "$TMP/ai"/*-report.md "$TMP/ai"/*-pre-disruption.md; do
    [ -f "$f" ] && rm -f "$f"
  done
  bash "$SCANNER" "$TMP/ai" >"$TMP/ai.txt" 2>&1
  tally "$TMP/ai.txt" >"$TMP/ai.tally"
  a_n=$(wc -l <"$TMP/ai.tally" | tr -d ' ')
  a_f=$(grep -c " FAIL$" "$TMP/ai.tally" || true)
  echo "    scanned $a_n chapters, $a_f failing, $(( a_n - a_f )) passing"
  if [ "$a_n" -eq 0 ]; then
    echo "    skip  no final chapters matched chapter-*.md"
  elif [ "$a_f" -eq 0 ]; then
    echo "    FAIL  every AI-written chapter passed - the scanner is not discriminating"
    verdicts=1
  elif [ "$a_f" -eq "$a_n" ]; then
    echo "    FAIL  every chapter failed - that is a blanket rule, not a threshold"
    verdicts=1
  else
    echo "    ok    the scanner separates this control instead of blanket-failing it"
  fi
fi

echo
if [ "$verdicts" -eq 0 ]; then
  echo "ALL CONTROLS PASS - the caps in tools/deslop-check.sh are still calibrated."
  echo "Caps changed? Re-measure with calibration/measure.py before trusting this run."
  exit 0
fi
echo "CONTROL FAILURE - do not use this scanner as a gate until this is resolved."
exit 1
