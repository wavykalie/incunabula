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
# | 4 | Elaina, split back into volumes  | human           | uniformity PASS  |
# | 5 | one chapter cut into six equal parts | machine-uniform | uniformity FAIL |
# | 6 | Elaina, split back into volumes  | human           | drift PASS       |
# | 7 | two books cut in half and joined | voice shift     | drift FAIL       |
#
# Controls 4-7 belong to the cross-chapter gates (tools/check-uniformity.py and
# tools/check-drift.py). A scanner that only reads one chapter at a time can see
# neither, so both gates need their own controls and this is where they are re-run.
#
# Control 5 was the project's own manuscript until that manuscript was made to vary.
# A control whose subject is fixed stops being a control, so the uniform case is now
# SYNTHESISED: one published chapter sliced into six even pieces, which is uniform by
# construction and fails for the right reason at any future date.
#
# A control that scans zero files is a FAILURE, not a pass. That is not
# hypothetical: directory mode used to glob only *.md, so the corpus control
# matched nothing and reported PASS without running a single check.
#
# See calibration/CALIBRATION.md for the caps, the method, and the raw numbers.

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
SCANNER="$HERE/deslop-check.sh"
# THE CALIBRATION CORPUS IS NOT SHIPPED. It is published commercial prose, and it is
# somebody else's copyright. Every threshold in this directory was derived from it and
# the derivation is recorded in calibration/CALIBRATION.md, but re-running the controls
# needs a corpus you supply:
#
#     HUMAN_CORPUS="/path/to/your/reference/*.txt" bash validate-controls.sh
#
# One file per chapter, named so that check-drift.py can sort it. Exit 2 means the
# controls did not run - never that they passed.
HUMAN_CORPUS="${HUMAN_CORPUS:-$HERE/calibration/corpus/elaina}"
SLOP_FIXTURE="${SLOP_FIXTURE:-$HERE/calibration/slop-fixture.md}"
AI_CONTROL="${AI_CONTROL:-}"
# The uniformity gate's own positive control: a manuscript known to hold every
# chapter within a few percent of its neighbours. Defaults to this project's own
# manuscript, which is exactly that case.
UNIFORM_CONTROL="${UNIFORM_CONTROL:-}"
UNIFORMITY="$HERE/check-uniformity.py"
DRIFT="$HERE/check-drift.py"
PYTHON="${PYTHON:-python}"

[ -f "$SCANNER" ] || { echo "missing scanner: $SCANNER"; exit 1; }

if [ ! -d "$HUMAN_CORPUS" ]; then
  echo "NOT VALIDATED - no calibration corpus installed."
  echo
  echo "  looked in:  $HUMAN_CORPUS"
  echo
  echo "  The corpus is published commercial prose and is deliberately not shipped with"
  echo "  these tools. Point HUMAN_CORPUS at your own reference text and re-run:"
  echo
  echo "      HUMAN_CORPUS=/path/to/reference bash validate-controls.sh"
  echo
  echo "  Until it runs, the caps in deslop-check.sh, check-uniformity.py and"
  echo "  check-drift.py are UNVERIFIED. Exit 2 means not-run; it never means pass."
  echo "  calibration/CALIBRATION.md holds the measurements and the method."
  exit 2
fi

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

echo "=== Control 1/5: human prose must all pass (negative control)"
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
echo "=== Control 2/5: synthetic slop must fail (positive control)"
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
echo "=== Control 3/5: AI-written prose must not all pass (discrimination control)"
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
echo "=== Control 4/7: published prose must pass the uniformity gate (negative control)"
# check-uniformity.py compares chapters INSIDE one manuscript, so the corpus has to
# be split back into its volumes. A single pooled directory would measure variance
# across three books at once, which is not the unit the gate judges.
if [ ! -f "$UNIFORMITY" ]; then
  echo "    FAIL  missing $UNIFORMITY"
  verdicts=1
else
  staged=0
  for v in v01 v02 v05; do
    set -- "$HUMAN_CORPUS"/*"-$v"__*chapter*.txt
    [ -e "$1" ] || continue
    d="$TMP/uni-$v"; mkdir -p "$d"
    i=0
    for f in "$@"; do
      i=$((i+1))
      cp "$f" "$d/chapter-$i.txt"
    done
    echo "    $v: $i chapters"
    if ! $PYTHON "$UNIFORMITY" "$d" >"$TMP/uni-$v.txt" 2>&1; then
      echo "    FAIL  published volume $v is failing the uniformity gate. The floors are too tight."
      grep -E "^   FAIL" "$TMP/uni-$v.txt" | sed 's/^/          /'
      verdicts=1
    fi
    staged=1
  done
  if [ "$staged" -eq 0 ]; then
    echo "    FAIL  no corpus volumes staged - a control that reads nothing proves nothing"
    verdicts=1
  else
    echo "    ok    every published volume varies like human prose"
  fi
fi

echo
echo "=== Control 5/7: a uniform manuscript must fail (positive control)"
if [ ! -f "$UNIFORMITY" ]; then
  echo "    skip  no uniformity gate to test"
elif [ -n "$UNIFORM_CONTROL" ] && [ -d "$UNIFORM_CONTROL" ]; then
  echo "    $UNIFORM_CONTROL  (supplied)"
  control5="$UNIFORM_CONTROL"
else
  control5="$TMP/uni-uniform"
  mkdir -p "$control5"
  src=$(ls "$HUMAN_CORPUS"/*chapter*.txt 2>/dev/null | head -1)
  if [ -z "$src" ]; then
    echo "    FAIL  no published chapter available to synthesise the control from"
    verdicts=1
  else
    echo "    $control5  (one chapter sliced into six even parts)"
    $PYTHON - "$src" "$control5" <<'PYEOF'
import sys, os
words = open(sys.argv[1], encoding="utf-8", errors="ignore").read().split()
per = max(len(words) // 6, 1)
for i in range(6):
    chunk = words[i * per:(i + 1) * per] if i < 5 else words[i * per:]
    open(os.path.join(sys.argv[2], "chapter-%02d.txt" % (i + 1)), "w", encoding="utf-8").write(" ".join(chunk))
PYEOF
  fi
fi
if [ ! -f "$UNIFORMITY" ] || [ ! -d "$control5" ]; then
  :
elif $PYTHON "$UNIFORMITY" "$control5" >"$TMP/uni.txt" 2>&1; then
  echo "    FAIL  a manuscript with near-identical chapter lengths passed. The gate is blind."
  verdicts=1
else
  rows=$(grep -cE "^   FAIL" "$TMP/uni.txt" || true)
  if [ "$rows" -eq 0 ]; then
    echo "    FAIL  gate failed without reporting a failing row"
    verdicts=1
  else
    echo "    ok    FAIL with $rows failing rows"
    grep -E "^   FAIL" "$TMP/uni.txt" | sed 's/^/          /'
  fi
fi

echo
echo "=== Control 6/7: published prose must pass the drift gate (negative control)"
if [ ! -f "$DRIFT" ]; then
  echo "    FAIL  missing $DRIFT"
  verdicts=1
else
  staged=0
  for v in v01 v02 v05; do
    d="$TMP/uni-$v"          # staged by control 4; same volume split, reused here
    [ -d "$d" ] || continue
    if ! $PYTHON "$DRIFT" "$d" >"$TMP/drift-$v.txt" 2>&1; then
      echo "    FAIL  published volume $v is failing the drift gate. The cap is too tight."
      grep -E "^   FAIL" "$TMP/drift-$v.txt" | sed 's/^/          /'
      verdicts=1
    fi
    staged=1
  done
  if [ "$staged" -eq 0 ]; then
    echo "    FAIL  no corpus volumes staged - a control that reads nothing proves nothing"
    verdicts=1
  else
    echo "    ok    every published volume holds one voice"
  fi
fi

echo
echo "=== Control 7/7: a book that changes voice must fail (positive control)"
if [ ! -f "$DRIFT" ]; then
  echo "    skip  no drift gate to test"
else
  d="$TMP/drift-shift"
  mkdir -p "$d"
  # In a book project this resolves to the manuscript itself; in this shipped copy it
  # does not exist and the script falls back to the mechanical-rewrite fixture.
  PROJECT_CHAPS="${PROJECT_CHAPS:-$HERE/../manuscript/chapters}"
  if [ -d "$PROJECT_CHAPS" ] && [ "$(ls "$PROJECT_CHAPS"/chapter-*.md 2>/dev/null | grep -vc -- '-report')" -ge 5 ]; then
    # Two books joined at the spine. Read line by line, because these paths contain
    # spaces and a bare `for f in $(ls ...)` splits them into fragments.
    {
      ls "$PROJECT_CHAPS"/chapter-*.md 2>/dev/null | grep -v -- '-report' | head -5
      ls "$HUMAN_CORPUS"/*chapter*.txt 2>/dev/null | head -5
    } >"$TMP/shift.list"
    i=0
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      i=$((i+1))
      case "$f" in *.txt) ext=.txt ;; *) ext=.md ;; esac
      cp "$f" "$d/$(printf 'chapter-%02d' "$i")$ext"
    done <"$TMP/shift.list"
    echo "    $d  ($i chapters, two books joined)"
  else
    # No second book on hand. Build the shift into the corpus instead: first half
    # untouched, second half run through a mechanical rewriter that unpicks the
    # paragraphing, strips dialogue and pads the sentences. That is not a claim about
    # how the change is made in practice - it is a control that the gate can still
    # SEE a change of hand, and it is stronger than the joined-books version because
    # the vocabulary and subject matter stay identical across the seam.
    $PYTHON - "$HUMAN_CORPUS" "$d" <<'PYEOF'
import glob, os, re, sys
files = sorted(glob.glob(os.path.join(sys.argv[1], "*.txt")))[:10]
files = [f for f in files if "afterword" not in f and "appendix" not in f][:10]
half = len(files) // 2
for i, f in enumerate(files, 1):
    text = open(f, encoding="utf-8", errors="ignore").read()
    if i > half:
        text = re.sub(r"[\u201c\"][^\u201d\"]{0,400}[\u201d\"]", "", text)
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        text = " ".join(paras)
        text = re.sub(r"(?<=[.!?])\s+", " and then, in the manner of the place, ", text)
    open(os.path.join(sys.argv[2], "chapter-%02d.txt" % i), "w", encoding="utf-8").write(text)
print("    %s  (%d chapters, second half mechanically rewritten)" % (sys.argv[2], len(files)))
PYEOF
    i=$(ls "$d" | wc -l | tr -d ' ')
  fi
  if [ "$i" -lt 6 ]; then
    echo "    FAIL  could not assemble the two-voice fixture"
    verdicts=1
  elif $PYTHON "$DRIFT" "$d" >"$TMP/drift-shift.txt" 2>&1; then
    echo "    FAIL  a manuscript made of two different books passed the drift gate."
    verdicts=1
  elif [ "$(grep -cE '^   FAIL' "$TMP/drift-shift.txt" || true)" -eq 0 ]; then
    echo "    FAIL  gate failed but reported no failing row - it is erroring, not judging"
    sed 's/^/          /' "$TMP/drift-shift.txt" | head -6
    verdicts=1
  else
    echo "    ok    FAIL with $(grep -cE '^   FAIL' "$TMP/drift-shift.txt" || true) failing rows"
    grep -E "^   FAIL|voice-step" "$TMP/drift-shift.txt" | head -4 | sed 's/^/          /'
  fi
fi

echo
if [ "$verdicts" -eq 0 ]; then
  echo "ALL CONTROLS PASS - the caps in tools/deslop-check.sh and the floors in"
  echo "tools/check-uniformity.py and tools/check-drift.py are still calibrated"
  echo "against published prose."
  echo "Caps changed? Re-measure with calibration/measure.py before trusting this run."
  exit 0
fi
echo "CONTROL FAILURE - do not use this scanner as a gate until this is resolved."
exit 1
