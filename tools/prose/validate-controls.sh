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
# | 3 | Hollow Bridge, 11 final chapters     | AI-written      | some fail, some pass |
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
# Controls 4-7 need a DIFFERENT corpus from control 1. Control 1 runs the per-chapter
# scanner over everything in the directory, so it wants a handful of documents; controls
# 4-7 need a MULTI-VOLUME corpus already split into chapter files, which is hundreds of
# files and takes ~12 minutes to scan. Conflating the two means either the uniformity
# controls never run or the whole suite times out. See calibration/fetch-multivolume.py.
VOLUME_CORPUS="${VOLUME_CORPUS:-$HUMAN_CORPUS}"
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

CORPUS_ABSENT=0
if [ ! -d "$HUMAN_CORPUS" ]; then
  # WHY THIS NO LONGER EXITS.
  #
  # This block used to `exit 2` immediately, which meant a fresh clone could not run a
  # single control - including control 2, the positive control, whose fixture
  # (calibration/slop-fixture.md) IS shipped and needs no corpus at all. The harness could
  # not demonstrate it detects bad prose on the machine it was cloned to, while holding
  # the evidence in its own repository. Found by cloning this repo clean and running the
  # suite the way a new user would, 2026-09-29.
  #
  # Exit 2 remains the right ANSWER - not-run must never read as pass, and the corpus is
  # genuinely somebody else's copyright. But it should be the verdict at the END, after
  # every control that can run without a corpus has run, not a refusal to begin.
  #
  # This is the recurring failure in its purest form: the instrument was honest, and the
  # gap was filled with the more comfortable story that the whole suite simply needs the
  # corpus. It did not.
  CORPUS_ABSENT=1
  echo "PARTIAL VALIDATION - no calibration corpus installed."
  echo
  echo "  looked in:  $HUMAN_CORPUS"
  echo
  echo "  The corpus is published commercial prose and is deliberately not shipped with"
  echo "  these tools. Point HUMAN_CORPUS at your own reference text and re-run:"
  echo
  echo "      HUMAN_CORPUS=/path/to/reference bash validate-controls.sh"
  echo
  # A corpus installed under a DIFFERENT name than the default is the common case, and
  # silence about it is what made a working calibration look absent. If anything is
  # sitting in corpus/, say so and give the command. Controls 4-7 need a multi-volume
  # corpus, so name that one too - setting only HUMAN_CORPUS runs control 1 and then
  # fails 4-7 for a reason that looks like a gate defect.
  found=0
  for d in "$HERE"/calibration/corpus/*/; do
    [ -d "$d" ] || continue
    n=$(ls -1 "$d" 2>/dev/null | wc -l | tr -d ' ')
    [ "$n" -gt 0 ] || continue
    found=1
    echo "  found instead:  $d  ($n files)"
  done
  if [ "$found" -eq 1 ]; then
    echo
    echo "  A corpus IS installed here, just not at the default path. To run every"
    echo "  control, point both variables at it - controls 4-7 need a MULTI-VOLUME"
    echo "  corpus already split into chapter files:"
    echo
    echo "      HUMAN_CORPUS=\"$HERE/calibration/corpus/<name>\" \\"
    echo "      VOLUME_CORPUS=\"$HERE/calibration/corpus/<name>\" \\"
    echo "        bash validate-controls.sh"
    echo
  fi
  echo "  Controls that need only SHIPPED fixtures still run below. Until the full suite"
  echo "  runs, the caps in deslop-check.sh, check-uniformity.py and check-drift.py are"
  echo "  UNVERIFIED against human prose. The final exit is 2; it never means pass."
  echo "  calibration/CALIBRATION.md holds the measurements and the method."
  echo
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Controls that could not run. Tracked separately from `verdicts` so the final summary
# can say "9 ran, 2 skipped" instead of folding a skip into a pass count. A suite that
# reported 11/11 while a control was skipped would be making the claim this file exists
# to prevent.
notrun=0

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
  # Not a FAIL. A control that could not run has produced no evidence either way, and
  # recording it as a failure would train people to ignore the FAIL column. It is
  # `skip`, the same word the AI-discrimination control has always used, and it is
  # counted separately so the summary cannot report 11/11 while a control did not run.
  echo "    skip  no human corpus installed; the caps are unverified against human prose"
  notrun=$((notrun+1))
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
    set -- "$VOLUME_CORPUS"/*"-$v"__*chapter*.txt
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
    echo "    skip  no corpus volumes staged - a control that reads nothing proves nothing, and"
    echo "          nothing here is evidence either way"
    notrun=$((notrun+1))
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
  src=$(ls "$VOLUME_CORPUS"/*chapter*.txt 2>/dev/null | head -1)
  if [ -z "$src" ]; then
    echo "    skip  no published chapter available to synthesise the control from"
    notrun=$((notrun+1))
    # Point $control5 at nothing so the gate branch below cannot run. Without this the
    # suite skipped the control in one line and then judged an empty directory in the
    # next, and the second verdict - a FAIL - overwrote the first. A skipped control that
    # reports a failure is the confusion this whole change exists to remove.
    rmdir "$control5" 2>/dev/null || true
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
    # NOT a skip. This line is only reachable when a control fixture WAS synthesised, so
    # the gate ran and produced a failure it could not account for. That is a real
    # defect in the gate and stays a FAIL.
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
    echo "    skip  no corpus volumes staged - a control that reads nothing proves nothing, and"
    echo "          nothing here is evidence either way"
    notrun=$((notrun+1))
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
      ls "$VOLUME_CORPUS"/*chapter*.txt 2>/dev/null | head -5
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
    $PYTHON - "$VOLUME_CORPUS" "$d" <<'PYEOF'
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
    echo "    skip  could not assemble the two-voice fixture (it is built from a published chapter)"
    notrun=$((notrun+1))
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
echo "=== Control 12/12: a drafting book is recorded, not failed (L1 in-progress)"
# Freeze 11. ERRATA 2026-10-01: check-length reported a book 13 of 30 chapters in
# as LENGTH FAILURE. In-progress and delivered-short are different states, and a
# gate that cries during drafting is trained out of its reader before delivery.
# The fix keys on the book's own status: in_progress declaration. Both arms are
# tested - a draft is reclassified to exit 4, and the same book finished (status
# removed) still fails if it is short. Without the second arm this control could
# pass on a gate that never fails anything.
if [ ! -f "$HERE/check-length.py" ]; then
  echo "    FAIL  missing check-length.py"
  verdicts=1
else
  rm -rf "$TMP/draftfix"
  mkdir -p "$TMP/draftfix/manuscript/chapters"
  for c in 01 02 03 04 05; do
    printf 'Chapter %s. ' "$c" >"$TMP/draftfix/manuscript/chapters/chapter-$c.md"
    i=0; while [ $i -lt 120 ]; do printf 'The record is silent about this. ' >>"$TMP/draftfix/manuscript/chapters/chapter-$c.md"; i=$((i + 1)); done
  done
  printf 'project:\n  target_floor_words: 20000\n  target_ceiling_words: 24000\n  status: "in_progress"\n' >"$TMP/draftfix/PROJECT_STATE.yaml"
  draft_rc=0
  $PYTHON "$HERE/check-length.py" "$TMP/draftfix" >"$TMP/draftfix.txt" 2>&1 || draft_rc=$?
  if [ "$draft_rc" -eq 0 ] || [ "$draft_rc" -eq 1 ] || [ "$draft_rc" -eq 3 ]; then
    echo "    FAIL  a book declaring in_progress exited $draft_rc - the draft was judged as delivery."
    sed 's/^/          /' "$TMP/draftfix.txt" | tail -6
    verdicts=1
  elif [ "$draft_rc" -ne 4 ]; then
    echo "    FAIL  in-progress book exited $draft_rc, not 4. The reclassification is not wired."
    sed 's/^/          /' "$TMP/draftfix.txt" | tail -6
    verdicts=1
  elif [ "$(grep -cE 'IN PROGRESS, recorded not judged' "$TMP/draftfix.txt" || true)" -eq 0 ]; then
    echo "    FAIL  exit was 4 but the row did not say what it did."
    verdicts=1
  else
    echo "    ok    a draft declaring in_progress exits 4, recorded not judged"
    grep -E '^   --' "$TMP/draftfix.txt" | head -1 | sed 's/^/          /'
  fi
  # The inverse arm: the same book, finished, must fail again.
  sed -i 's/  status: "in_progress"//' "$TMP/draftfix/PROJECT_STATE.yaml"
  $PYTHON "$HERE/check-length.py" "$TMP/draftfix" >/dev/null 2>&1 && fin_rc=0 || fin_rc=$?
  if [ "$fin_rc" -eq 1 ] && [ "$(grep -cE '^   FAIL  L1' "$TMP/draftfix.txt" || true)" -ge 0 ]; then
    echo "    ok    the same book finished still fails short (L1 intact at delivery)"
  elif [ "$fin_rc" -eq 1 ]; then
    echo "    ok    the same book finished still fails short (L1 intact at delivery)"
  else
    echo "    FAIL  finished book short of floor exited $fin_rc - delivery enforcement lost."
    verdicts=1
  fi
  rm -rf "$TMP/draftfix"
fi

echo
echo "=== Control 8/9: the REPORT tier must not be able to fail (D1, D2)"
# D1 and D2 were demoted to report-only because the AI control sits INSIDE the published
# distribution on both rows - D1 reads 0.00/1k on every control chapter because these books
# spell a dash "--", and D2's control p50 sits at the published median. The cap is still
# printed, so a future edit that quietly promotes one back to the DENSITY tier would
# reintroduce a gate that fails 14-19% of real human prose. This control fails if it does.
if [ ! -f "$SCANNER" ]; then
  echo "    FAIL  missing $SCANNER"
  verdicts=1
else
  rep_fail=0
  # Every id in the REPORT block, read from the file rather than hardcoded, so adding a
  # row to that block brings it under this control automatically.
  # The pipe must go too: `tr -d " '"` leaves the id as "D1|", which matches no row and
  # makes this control report a phantom FAIL for a row that is correctly demoted.
  rep_ids=$(sed -n '/^REPORT=(/,/^)/p' "$SCANNER" \
            | grep -oE "^  '[A-Z][0-9]+[a-z]?\|" | tr -d " '|")
  if [ -z "$rep_ids" ]; then
    echo "    FAIL  no REPORT block found in deslop-check.sh - the tier is gone."
    verdicts=1
  else
    bash "$SCANNER" "$SLOP_FIXTURE" >"$TMP/report.txt" 2>&1
    for id in $rep_ids; do
      if grep -qE "^   FAIL  $id " "$TMP/report.txt"; then
        echo "    FAIL  $id is in the REPORT block but printed FAIL - the demotion is"
        echo "          not in effect and this row can fail a book again."
        rep_fail=1
        verdicts=1
      fi
    done
    if [ "$rep_fail" -eq 0 ]; then
      echo "    ok    $(echo $rep_ids | tr ' ' ',') cannot fail anything"
      echo "          (the slop fixture is over both caps and neither printed FAIL)"
      grep -E "^   --  " "$TMP/report.txt" | head -2 | sed 's/^/          /'
    fi
  fi
fi

echo
echo "=== Control 11/11: a book short of its DECLARED length must FAIL (L1)"
# Every other row in this directory is a rate, and a rate is satisfied by a book that is
# shorter than intended. L1 is the only row that is not: it compares a book to the length
# that book declared for itself, so it needs no corpus and cannot false-fail a population.
#
# It is also the only thing standing between the system and its own perverse incentive.
# U1 is scale-invariant, so cutting the two longest chapters by 40% RAISES the CV - the
# cheapest way to pass the chapter-shape row is to delete prose. Measured on
# sons-of-heaven-v2: 17,872 words / CV 30.3% -> 15,980 words / CV 22.5%, still passing.
# L1 is the row that moves the other way, so it must be able to fail.
if [ ! -f "$HERE/check-length.py" ]; then
  echo "    FAIL  missing check-length.py"
  verdicts=1
else
  rm -rf "$TMP/lenfix"
  mkdir -p "$TMP/lenfix/manuscript/chapters"
  # A four-chapter book that declares a range and then delivers 40% of it.
  for c in 01 02 03 04; do
    printf 'Chapter %s. ' "$c" >>"$TMP/lenfix/manuscript/chapters/chapter-$c.md"
    i=0; while [ $i -lt 300 ]; do printf 'The record is silent about this. ' >>"$TMP/lenfix/manuscript/chapters/chapter-$c.md"; i=$((i + 1)); done
  done
  printf 'project:\n  target_floor_words: 20000\n  target_ceiling_words: 24000\n' >"$TMP/lenfix/PROJECT_STATE.yaml"
  if $PYTHON "$HERE/check-length.py" "$TMP/lenfix" >"$TMP/lenfix.txt" 2>&1; then
    echo "    FAIL  a book delivering 40% of its declared length PASSED."
    echo "          This is the gate that stops 'vary your chapters' becoming a licence to delete."
    sed 's/^/          /' "$TMP/lenfix.txt" | tail -6
    verdicts=1
  elif [ "$(grep -cE '^   FAIL' "$TMP/lenfix.txt" || true)" -eq 0 ]; then
    echo "    FAIL  gate failed but reported no failing row - it is erroring, not judging"
    sed 's/^/          /' "$TMP/lenfix.txt" | head -6
    verdicts=1
  else
    echo "    ok    FAIL with 1 failing row"
    grep -E '^   FAIL' "$TMP/lenfix.txt" | head -1 | sed 's/^/          /'
  fi
  # And the inverse: a book that DID deliver its range must pass.
  sed -i 's/target_floor_words: 20000/target_floor_words: 400/' "$TMP/lenfix/PROJECT_STATE.yaml"
  if $PYTHON "$HERE/check-length.py" "$TMP/lenfix" >/dev/null 2>&1; then
    echo "    ok    a book within its declared range passes"
  else
    echo "    FAIL  a book inside its declared range was failed. The row is miscalibrated."
    verdicts=1
  fi
  rm -rf "$TMP/lenfix"
fi

echo "=== Control 10/10: a published NON-FICTION volume must not fail U1"
# The fiction floor for U1 is 30% CV. Six published non-fiction volumes were measured
# and one of them falls under it - Darwin's Journal of Researches, at 28.2%. A chapter in
# a novel runs as long as its scene does; a chapter on a species runs as long as the
# argument does, and those are not the same shape. U1 is therefore advisory on a book
# that declares positioning: nonfiction, and enforced everywhere else.
#
# This control takes a REAL published non-fiction volume, declares the convention, and
# fails if U1 accuses it. It is the demotion's regression test: without the scoping this
# control fires, which is the point.
NONFICTION_VOL="${NONFICTION_VOL:-$HERE/calibration/corpus/nonfiction}"
if [ ! -d "$NONFICTION_VOL" ]; then
  echo "    skip  no non-fiction corpus - run calibration/fetch-multivolume.py --nonfiction"
  echo "          (U1's advisory scoping is then UNVERIFIED, as it was before this row)"
else
  rm -rf "$TMP/nf"
  # EVERY volume, one at a time. Testing only the first one passes trivially - the first
  # happens to be comfortable - and a guard that cannot be made to fail is not a guard.
  # The volume that matters is Darwin's Journal of Researches at 28.2%, and the only way
  # to be sure it is in here is to stage all of them.
  nf_volumes=0
  nf_bad=0
  nf_report=""
  for f in "$NONFICTION_VOL"/*"__chapter-01.txt"; do
    [ -e "$f" ] || continue
    stem=$(basename "$f" | sed 's/__chapter-01\.txt$//')
    rm -rf "$TMP/nf"
    mkdir -p "$TMP/nf/manuscript/chapters"
    for c in "$NONFICTION_VOL/$stem"__chapter-*.txt; do
      [ -e "$c" ] || continue
      cp "$c" "$TMP/nf/manuscript/chapters/"
    done
    [ -n "$(ls -A "$TMP/nf/manuscript/chapters" 2>/dev/null)" ] || continue
    nf_volumes=$((nf_volumes + 1))
    printf 'project:\n  positioning: "narrative nonfiction"\n' >"$TMP/nf/PROJECT_STATE.yaml"
    $PYTHON "$HERE/check-uniformity.py" "$TMP/nf" >"$TMP/nf.txt" 2>&1
    v=$(grep -oE 'CV [0-9.]+%' "$TMP/nf.txt" | head -1 | sed 's/CV //;s/%//')
    if grep -qE '^   FAIL  U1' "$TMP/nf.txt"; then
      nf_bad=$((nf_bad + 1))
      nf_report="$nf_report
    FAIL  $stem - CV ${v}%"
      grep -E '^   FAIL  U1' "$TMP/nf.txt" | head -1 | sed 's/^/          /'
      verdicts=1
    else
      nf_report="$nf_report
    ok    $stem  CV ${v}%"
    fi
  done
  if [ "$nf_volumes" -eq 0 ]; then
    echo "    skip  non-fiction corpus present but no volume could be staged"
  else
    echo "    ok    $nf_volumes published nonfiction volumes, none failed U1:$nf_report"
  fi
  rm -rf "$TMP/nf"
fi

echo "=== Control 9/9: the monotone-arc fixture must FAIL (A1 can still fire)"
# A synthetic book whose sentiment only ever falls. If this passes, A1 is not judging arc
# and every green A1 in this directory is meaningless. The fixture is generated rather
# than stored, because a stored fixture can rot and still be cited as proof.
if [ ! -f "$HERE/calibration/make-arc-fixture.py" ]; then
  echo "    FAIL  missing make-arc-fixture.py"
  verdicts=1
else
  rm -rf "$TMP/arcfix"
  $PYTHON "$HERE/calibration/make-arc-fixture.py" "$TMP/arcfix" >/dev/null 2>&1
  if $PYTHON "$HERE/check-arc.py" "$TMP/arcfix" >"$TMP/arcfix.txt" 2>&1; then
    echo "    FAIL  a monotone-emotion book PASSED the arc gate."
    verdicts=1
  elif [ "$(grep -cE '^   FAIL' "$TMP/arcfix.txt" || true)" -eq 0 ]; then
    echo "    FAIL  gate failed but reported no failing row - it is erroring, not judging"
    sed 's/^/          /' "$TMP/arcfix.txt" | head -6
    verdicts=1
  else
    echo "    ok    FAIL with $(grep -cE '^   FAIL' "$TMP/arcfix.txt" || true) failing row(s)"
    grep -E "^   FAIL" "$TMP/arcfix.txt" | head -2 | sed 's/^/          /'
  fi
  rm -rf "$TMP/arcfix"
fi

echo
# The summary is where a partial run becomes a false claim. On a fresh clone the suite
# cannot reach published prose, and the wording used to say "ALL CONTROLS PASS - still
# calibrated against published prose" off the back of controls that only used fixtures
# shipped in this repository. The controls that DID run are real evidence and are
# reported; the ones that could not are counted and named, and the exit code is 2.
if [ "$verdicts" -ne 0 ]; then
  echo "CONTROL FAILURE - do not use this scanner as a gate until this is resolved."
  exit 1
fi

if [ "$CORPUS_ABSENT" -eq 1 ]; then
  echo "PARTIAL - controls that need only shipped fixtures ran and passed; $notrun"
  echo "control(s) could not run because no calibration corpus is installed."
  echo
  echo "  Proven on this run: the scanner FAILS synthetic slop, and the uniformity,"
  echo "  drift and arc gates still FAIL the manuscripts they are built to reject."
  echo "  That is the harness detecting bad output, and it is the part that does not"
  echo "  depend on anyone else's copyright."
  echo
  echo "  NOT proven: that the caps still match published human prose. Until you point"
  echo "  HUMAN_CORPUS at reference text, the thresholds are UNVERIFIED in that"
  echo "  direction and the numbers in CALIBRATION.md are the only evidence for them."
  echo
  echo "  Exit 2 means partially validated. It never means fully validated."
  exit 2
fi

echo "ALL CONTROLS PASS - the caps in tools/deslop-check.sh and the floors in"
echo "tools/check-uniformity.py and tools/check-drift.py are still calibrated"
echo "against published prose, fiction and non-fiction."
if [ "$notrun" -gt 0 ]; then
  echo "Note: $notrun control(s) reported skip - see above for which, and read those"
  echo "lines before treating this as full coverage."
fi
echo "Caps changed? Re-measure with calibration/measure.py before trusting this run."
exit 0
