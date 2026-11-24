#!/usr/bin/env bash
# run-gates — the whole gate suite against one book, in one command.
#
# WHY THIS EXISTS
#   The gates in tools/prose/ are a dozen separate commands a run had to remember
#   at seventeen phase boundaries, and nothing enforced the remembering: books
#   reached `status: complete` with zero gated words and no pass files at all.
#   Two such books were found by tools/check-pass-evidence.py. "The prose gate"
#   was prose: a checklist an
#   agent could skip and still declare victory. This runner is the enforcement
#   point. One command, every gate, and the project's standing rule applied to
#   the suite as a whole: NOT-RUN IS NEVER PASS. It exits nonzero when a gate
#   fails the book AND when a gate could not run.
#
# WHAT IT IS NOT
#   It is not a gate and deliberately not a row in GATE_FREEZE.md. It measures
#   nothing new: it runs the frozen instruments and reports their exit codes,
#   then gets out of the way. Same exemption class as preflight.sh - process
#   tooling around the instrument. Every gate it runs keeps its own hash and its
#   own freeze attribution; this file changes none of them.
#
#   It always runs the tools in THIS tree ($ROOT/tools/prose), never a copy
#   embedded in a book directory. A book carrying its own tools/ snapshot can
#   carry a stale instrument - a quarantined copy of check-uniformity.py under a
#   book's own `_archive/tools/` fails U1 at 30% while the frozen copy fails at 22% -
#   and a result must be attributable to one known instrument.
#
#   Two steps run after the gates and are not gates. tools/prune-stale.py --apply is
#   the self-prune: it keeps the record files' standing claims true to the program
#   (old wording preserved in maintenance/PRUNING_LOG.md), quarantines book-carried
#   instrument copies, and never edits dated history. tools/errata-store.py automerge
#   --apply is the craft store's unattended compaction, rate-limited by
#   record/errata-policy.yaml and never allowed to touch a pinned measurement record.
#   Housekeeping, both of them - neither can change the verdict. See their docstrings
#   for the full contracts.
#
# USAGE
#   bash tools/run-gates.sh <book-root> [--ledger <premise-ledger.tsv>]
#
#   <book-root> is the project directory holding manuscript/chapters/.
#
#   --ledger points check-premise-distinct.py at a premise ledger other than the frozen
#   one in this tree. The public tree's PREMISE_LEDGER.tsv holds no rows by design - the
#   de-identification pass removed them (GATE_FREEZE, 2026-10-15) - so the premise row
#   reads NOT RUN in every checkout, and correctly so: an empty ledger makes that gate
#   pass everything. The real rows live in .private/record/PREMISE_LEDGER.seed.tsv, which
#   is gitignored and absent from a clone. This flag lets a local run measure the row
#   against them without seeding the frozen file, which would publish them and break the
#   freeze. WITHOUT THE FLAG NOTHING CHANGES: the row still reads NOT RUN, and not-run is
#   never a pass.
#
# EXIT
#   0  CLEAR - every gate ran and passed (report-only rows gate nothing)
#   1  FAIL - at least one gate failed the book
#   2  NOT CLEAR - nothing failed, but at least one gate row did not run or
#      declined to judge ("recorded, not judged"). Never read this as a pass.
#   3  could not run at all: bad invocation, no python, or no
#      manuscript/chapters under the book root
#
# ROW CLASSES (how each tool's exit code is read)
#   prose     deslop-check.sh, check-uniformity.py, check-monotony.py, check-drift.py,
#             check-arc.py: 0 pass, else fail - except an output saying
#             "nothing checkable" / "no chapters found", which is NOT RUN.
#             An empty scan is a FAIL by the scanner's own design.
#   contract  check-length.py, check-narrative.py, check-progress.py:
#             0 pass, 1 fail, 2 not declared / 3 ungoverned -> NOT RUN,
#             4 -> RECORDED ("in_progress" - recorded, not judged; the row
#             re-enforces the moment the book stops declaring status:
#             in_progress. check-progress.py C1 deliberately never defers:
#             the contract and the plan are declarations, not deliveries.)
#   hygiene   check-comps.py, check-premise-distinct.py, check-names.py,
#             check-manuscript-integrity.py, check-pass-evidence.py:
#             0 pass, 2 could-not-read / not-applicable -> NOT RUN, else fail.
#   report    check-surplus.py, check-recoverable.py, check-figurative.py,
#             check-quantities.py, check-agency.py: 0 REPORTED,
#             findings never fail anything; a report that could not run is
#             NOTED and gates nothing, because these rows cannot gate.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PROSE="$ROOT/tools/prose"

if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "run-gates: no python on PATH - the suite cannot run at all. Exit 3."
  exit 3
fi

usage() {
  cat <<'EOF'
usage: bash tools/run-gates.sh <book-root> [--ledger <premise-ledger.tsv>]

Runs the full gate suite against one book and prints every tool's own output,
followed by a summary table. Exit 0 = clear, 1 = a gate failed the book,
2 = not clear (a gate did not run or declined to judge - never a pass),
3 = could not run at all.

Not-run is never a pass. That is the whole contract of this file.
EOF
}

LEDGER=""
BOOK=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage; exit 0 ;;
    --ledger)
      shift
      LEDGER="${1:-}"
      if [ -z "$LEDGER" ]; then
        echo "run-gates: --ledger needs a path to a premise ledger."
        exit 3
      fi ;;
    --ledger=*)
      LEDGER="${1#*=}" ;;
    -*)
      echo "run-gates: unknown option: $1"
      usage
      exit 3 ;;
    *)
      if [ -n "$BOOK" ]; then
        echo "run-gates: one book per run (got '$BOOK' and '$1')."
        exit 3
      fi
      BOOK="$1" ;;
  esac
  shift
done

if [ -z "$BOOK" ]; then
  usage
  exit 3
fi
if [ -n "$LEDGER" ] && [ ! -f "$LEDGER" ]; then
  echo "run-gates: no premise ledger at $LEDGER"
  echo "          (the private seed is .private/record/PREMISE_LEDGER.seed.tsv"
  echo "           and is not present in a public clone)"
  exit 3
fi
if [ ! -d "$BOOK" ]; then
  echo "run-gates: no such book directory: $BOOK"
  exit 3
fi
CHAPTERS="$BOOK/manuscript/chapters"
if [ ! -d "$CHAPTERS" ]; then
  echo "run-gates: no manuscript/chapters under $BOOK - nothing to gate."
  echo "          (A book root is the directory holding manuscript/chapters/.)"
  exit 3
fi
chapter_files=$(find "$CHAPTERS" -maxdepth 1 \( -name '*.md' -o -name '*.txt' \) | wc -l)
if [ "$chapter_files" -eq 0 ]; then
  echo "run-gates: $CHAPTERS holds no .md or .txt files - nothing can be gated."
  echo "          Not-run is never a pass; this book is NOT CLEAR."
  exit 2
fi

# ------------------------------------------------------------------------------

R_NAME=(); R_STATUS=(); R_EXIT=(); R_DETAIL=()
fails=0
unclear=0

contains() { case "$2" in *"$1"*) return 0 ;; *) return 1 ;; esac; }

classify() {  # classify KIND RC OUT -> echoes status
  local kind="$1" rc="$2" out="$3"
  case "$kind" in
    prose)
      # A row can decline to judge one file and still exit 0: deslop-check.sh reports
      # P1 and A25 as UNMEASURED below 667 words, the measured document-size floor
      # (2026-11-07; 45 of 281 published documents under 667 failed P1 at the old
      # 167-word floor). That is not a pass and not a failure, so it gets its own
      # status and counts toward `unclear` like NOT RUN does.
      if [ "$rc" -eq 0 ] && contains "RESULT: UNMEASURED" "$out"; then
        echo UNMEASURED
      elif [ "$rc" -eq 0 ]; then
        echo PASS
      elif contains "nothing checkable" "$out" || contains "no chapters found" "$out"; then
        echo "NOT RUN"
      else
        echo FAIL
      fi ;;
    contract)
      case "$rc" in
        0)  echo PASS ;;
        4)  echo RECORDED ;;
        2|3) echo "NOT RUN" ;;
        *)  echo FAIL ;;
      esac ;;
    hygiene)
      case "$rc" in
        0)  echo PASS ;;
        2)  echo "NOT RUN" ;;
        *)  echo FAIL ;;
      esac ;;
    report)
      if [ "$rc" -eq 0 ]; then echo REPORTED; else echo "NOT RUN"; fi ;;
  esac
}

run_row() {  # run_row NAME KIND SCRIPT [ARGS...]
  local name="$1" kind="$2" script="$3"; shift 3
  local out rc status detail interp
  if [ ! -f "$script" ]; then
    out="run-gates: tool missing at $script - the suite cannot run this row."
    rc="-"
    status="NOT RUN"
  else
    case "$script" in
      *.sh) interp=bash ;;
      *)    interp="$PY" ;;
    esac
    out=$("$interp" "$script" "$@" 2>&1)
    rc=$?
    status=$(classify "$kind" "$rc" "$out")
  fi

  echo "---- $name"
  echo "     command: $interp ${script#$ROOT/} $*"
  printf '%s\n' "$out"
  echo "     => $status (exit $rc)"
  echo

  detail=$(printf '%s\n' "$out" | tail -n 1)
  R_NAME+=("$name"); R_STATUS+=("$status"); R_EXIT+=("$rc"); R_DETAIL+=("$detail")

  case "$status" in
    FAIL)      fails=$((fails + 1)) ;;
    "NOT RUN") if [ "$kind" != report ]; then unclear=$((unclear + 1)); fi ;;
    UNMEASURED) unclear=$((unclear + 1)) ;;
    RECORDED)  unclear=$((unclear + 1)) ;;
  esac
}

echo "================================================================="
echo "run-gates - the full suite against one book"
echo "book:  $BOOK   ($chapter_files chapter files)"
if [ -n "$LEDGER" ]; then
  echo "ledger: $LEDGER  (premise row only; the frozen ledger is untouched)"
fi
echo "tools: ${PROSE#$ROOT/}  (the frozen instrument; book-embedded"
echo "       copies are never used, so every result is attributable)"
echo "================================================================="
echo

echo "== research gates (P1, C1) ====================================="
run_row "check-comps.py" hygiene "$PROSE/check-comps.py" "$BOOK"
if [ -n "$LEDGER" ]; then
  run_row "check-premise-distinct.py" hygiene "$PROSE/check-premise-distinct.py" "$BOOK" --ledger "$LEDGER"
else
  run_row "check-premise-distinct.py" hygiene "$PROSE/check-premise-distinct.py" "$BOOK"
fi

echo "== cross-book and integrity ===================================="
run_row "check-names.py" hygiene "$PROSE/check-names.py" "$BOOK"
run_row "check-manuscript-integrity.py" hygiene "$ROOT/tools/check-manuscript-integrity.py" "$BOOK"
run_row "check-ductus.py" hygiene "$ROOT/tools/check-ductus.py" "$BOOK"
# The contract's own numbers, measured. check-monotony.py prints its rates against the
# published band and enforces only M1; this row reads the limits the assigned ductus
# DECLARES (negation, subject openings, texture) and fails the book where it leaves one.
# A book with no `ductus:` reads NOT RUN, the same as any other undeclared contract.
run_row "ductus.py calibrate" contract "$ROOT/tools/ductus.py" "calibrate" "$BOOK"

echo "== world gate (Phase 2; only where a world is declared) ========"
# A book's world is fixed before it has chapters, so this row cannot exist for most books
# and must not read as NOT RUN for them: an absent world.md means the book has not reached
# Phase 2, not that a gate declined to judge. A book that does carry world.md is judged by
# the same audit the Phase 2 gate names (blind-packet.py --gate, rules W1-W4): three
# candidate engines, one chosen, a chosen engine that is not administration in costume,
# and the administrative attractor named among the discards.
if [ -f "$BOOK/world.md" ]; then
  run_row "blind-packet.py --gate" hygiene "$ROOT/tools/blind-packet.py" "$BOOK" --gate
else
  echo "     no world.md under this book - the Phase 2 world gate does not apply."
  echo "     (A book that reaches Phase 2 acquires one; run the row then.)"
  echo
fi

echo "== discard record (Phase 0-2; only where a premise is declared) ======"
# The refusal intake runs by hand: a premise that rebuilds an engine this project
# scrapped (root COMMONPLACE.md, "Do not rebuild") has no engine yet, whatever its
# nouns. Absent premise.md means the book predates the record, not that it passed.
if [ -f "$BOOK/premise.md" ]; then
  run_row "blind-packet.py --discards" hygiene "$ROOT/tools/blind-packet.py" "$BOOK" --discards
else
  echo "     no premise.md under this book - the discard refusal does not apply."
  echo
fi

echo "== prose gate =================================================="
run_row "deslop-check.sh" prose "$PROSE/deslop-check.sh" "$CHAPTERS"
run_row "check-uniformity.py" prose "$PROSE/check-uniformity.py" "$BOOK"
run_row "check-monotony.py" prose "$PROSE/check-monotony.py" "$BOOK"
run_row "check-drift.py" prose "$PROSE/check-drift.py" "$BOOK"
run_row "check-arc.py" prose "$PROSE/check-arc.py" "$BOOK"
# check-world.py forbids objects; this row reads <book>/DICTION_RULES.txt, which both
# forbids words that date the page and REQUIRES the vocabulary the book must keep. The
# failure it was built for was a world that subtracted every modern noun and never put
# one back - prose that passed all eight caps and still sounded like 1880. A book with no
# rules file reads NOT RUN, the same stance every other undeclared contract takes.
run_row "check-diction.py" prose "$PROSE/check-diction.py" "$BOOK"
# V3 is the one measured row in the tag tool; V1/V2 above it still report only. A book
# under 40 tagged spans reads UNMEASURED and exits 0 (see the tool's MIN_TAGGED_FOR_V3),
# so a dialogue-sparse book is not failed for a rate it cannot support.
run_row "check-dialogue-tags.py" prose "$PROSE/check-dialogue-tags.py" "$BOOK"

echo "== report-only companions (never gate) ========================="
run_row "check-surplus.py" report "$PROSE/check-surplus.py" "$BOOK"
run_row "check-recoverable.py" report "$PROSE/check-recoverable.py" "$BOOK"
run_row "check-figurative.py" report "$PROSE/check-figurative.py" "$BOOK"
run_row "check-quantities.py" report "$PROSE/check-quantities.py" "$BOOK"
# Place agency ("The hall knows") and object agency ("the car waited"), counted apart, plus
# motive by absence ("because it didn't need to"). Report-only for a measured reason, not
# for want of one: 6 hits in 4,531,815 words of published prose, and the ones that occur
# are deliberate. Published prose runs 3 place to 3 object; this tree runs 15 to 0.
# A 1.5x cap from the worst published document (0.21/1k) would land at ~0.32/1k and fail
# the project book's own deliberate chapter 14 (0.74/1k) - the D1/D2 document-vs-chapter
# mismatch, never tested on chapters. The stronger signal is the second row: 2 hits in
# 4.5M published words against 0.014/1k in this tree, and two hits is a hypothesis. So
# this row lists per chapter and a reader rules; promoting either row is a freeze event,
# and the tool's docstring carries the numbers that decide it.
run_row "check-agency.py" report "$PROSE/check-agency.py" "$BOOK"

echo "== narrative gate (Freeze 13) =================================="
run_row "check-narrative.py" contract "$PROSE/check-narrative.py" "$BOOK"

echo "== length, progress, and pass evidence ========================="
run_row "check-length.py" contract "$PROSE/check-length.py" "$BOOK"
run_row "check-progress.py" contract "$ROOT/tools/check-progress.py" "$BOOK"
run_row "check-pass-evidence.py" hygiene "$ROOT/tools/check-pass-evidence.py" "$BOOK"

echo "== post-run self-prune (housekeeping; gates nothing) ==================="
# The repair half of the self-prune. After the book has been measured, the RECORDS
# are measured against the program that just ran: standing claims (counts, tallies,
# statuses) that the live program contradicts are corrected in place, with the old
# wording preserved verbatim in maintenance/PRUNING_LOG.md (maintenance-protocol §7).
# Book-carried instrument copies are quarantined under _archive/, never deleted.
# DATED HISTORY IS NEVER EDITED - a dated entry that disagrees with the program is
# reported for the author to rule on. This is housekeeping around the run and cannot
# change the verdict below; it is deliberately not a row in GATE_FREEZE.md, same
# exemption class as preflight.sh.
if [ -f "$ROOT/tools/prune-stale.py" ]; then
  "$PY" "$ROOT/tools/prune-stale.py" --apply
  echo
else
  echo "     prune-stale.py not found at tools/ - record drift is not repaired."
  echo
fi

# And the second housekeeping step, for the same reason and with the same status:
# tools/errata-store.py automerge --apply, the craft store's unattended compaction.
# It is rate-limited by record/errata-policy.yaml (one change per pass, per
# SELF_IMPROVEMENT §5) and it never touches a pinned measurement record. It cannot
# change the verdict either; it is reported so a run's record state is visible.
if [ -f "$ROOT/tools/errata-store.py" ]; then
  "$PY" "$ROOT/tools/errata-store.py" automerge --apply
  echo
else
  echo "     errata-store.py not found at tools/ - the craft store is not compacted."
  echo
fi

echo "================================================================="
echo "run-gates summary"
for i in "${!R_NAME[@]}"; do
  printf '  %-28s %-8s exit %-3s %s\n' "${R_NAME[$i]}" "${R_STATUS[$i]}" "${R_EXIT[$i]}" "${R_DETAIL[$i]}"
done
echo
if [ "$fails" -gt 0 ]; then
  echo "VERDICT: FAIL - $fails gate row(s) failed the book. The failing rows name their fix."
  echo "A gate that cannot see a weakness is not a gate that passed it."
  exit 1
fi
if [ "$unclear" -gt 0 ]; then
  echo "VERDICT: NOT CLEAR - nothing failed, but $unclear gate row(s) did not run or declined to judge."
  echo "Not-run is never a pass. Run the named rows before claiming a phase."
  exit 2
fi
echo "VERDICT: CLEAR - every gate ran and passed. Report-only rows never gate."
exit 0
