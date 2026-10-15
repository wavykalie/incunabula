#!/usr/bin/env bash
# preflight — the make-ready verifier stack, run before a session starts.
#
# Measures the TOOL and the STATE, never the prose. Not a gate, and deliberately not a
# row in GATE_FREEZE.md: it answers "will the instruments I am about to use be the ones
# the results will be attributed to", which is the question sync-skills.py --check
# already asks. Same exemption class, one layer up.
#
# Every past failure class this project recorded is one of its rows: a stale installed
# skill copy (meaningless measurements), a broken freeze (unattributable results), a
# state file that would not parse (KF-004), a stray CR that hid from grep (KF-005),
# and a book carrying its own stale copy of the instruments (a verdict nobody can
# attribute - a quarantined copy under a book's `_archive/tools/` failed U1 at 30%
# where the frozen instrument fails at 22%).#   A check that has never been seen to fail is not yet known to work — so every row here
#   names its own state, including the states where it could not look.
#   Row 7 (record hygiene) is the self-prune in its check role: the record files'
#   standing claims measured against the live program. The repair half is
#   `python tools/prune-stale.py --apply`, also run by run-gates.sh after each run.
#
# USAGE
#   bash tools/preflight.sh [project-root ...]
#
#   With no project root, the state-hygiene rows are reported SKIPPED, not passed.
#   With one or more roots (a book directory or a books root), every canonical state
#   file found there is checked. The embedded-instrument row always scans the whole
#   workspace (test-books/) plus any given roots - that failure class lives wherever
#   the books live, whether or not a session passed a root.
#
# EXIT
#   0  every row PASS or SKIPPED (skips are named in the output)
#   1  at least one FAIL
#   2  could not run at all (missing tool)

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

fails=0
skips=0

row() {   # row NAME STATUS DETAIL
  printf "  %-22s %-6s %s\n" "$1" "$2" "$3"
  [ "$2" = "FAIL" ] && fails=$((fails + 1))
  [ "$2" = "SKIP" ] && skips=$((skips + 1))
}

echo "preflight — the make-ready verifier stack"
echo

# 1. Freeze attribution ------------------------------------------------------------
echo "1. freeze attribution"
if [ -f "$ROOT/tools/prose/verify-freeze.sh" ]; then
  out=$(bash "$ROOT/tools/prose/verify-freeze.sh" 2>&1)
  rc=$?
  if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q "FREEZE HOLDS"; then
    row "verify-freeze" PASS "$(printf '%s' "$out" | tail -1)"
  else
    row "verify-freeze" FAIL "exit $rc — results would not be attributable. Do not draft against this instrument."
  fi
else
  row "verify-freeze" FAIL "verify-freeze.sh not found at tools/prose/"
fi

# 2. Installed skill copy ---------------------------------------------------------
echo "2. installed skill copy"
if command -v python >/dev/null 2>&1; then
  out=$(python "$ROOT/tools/sync-skills.py" --check 2>&1)
  rc=$?
  if [ $rc -eq 0 ]; then
    row "sync-skills --check" PASS "installed copies match the authoritative skills/"
  else
    row "sync-skills --check" FAIL "drift or pending quarantine (exit $rc). Run: python tools/sync-skills.py"
  fi
else
  row "sync-skills --check" FAIL "python not found; the skill copies cannot be checked"
fi

# 3. State hygiene ----------------------------------------------------------------
# The KF-005 lesson, encoded: stray CR is counted with tr, never grep — on this
# platform grep cannot see the character the defect is about.
echo "3. state hygiene"
if [ $# -eq 0 ]; then
  row "state files" SKIP "no project root given — passing a root checks PROJECT_STATE/STATE/ENTITY_STATE/CANON_LEDGER"
else
  for dir in "$@"; do
    found=0
    for f in "$dir"/PROJECT_STATE.yaml "$dir"/STATE.yaml "$dir"/ENTITY_STATE.yaml "$dir"/CANON_LEDGER.yaml; do
      [ -f "$f" ] || continue
      found=1
      name="$(basename "$dir")/$(basename "$f")"
      cr=$(tr -cd '\r' < "$f" | wc -c)
      if [ "$cr" -gt 0 ]; then
        row "$name" FAIL "$cr stray CR byte(s) — the KF-005 defect class; sentence-level rows will under-count"
        continue
      fi
      out=$(python - "$f" <<'PYEOF' 2>&1
import sys
p = sys.argv[1]
try:
    open(p, encoding="utf-8").read()
except UnicodeDecodeError as e:
    print(f"NOT UTF-8: {e}")
    sys.exit(1)
try:
    import yaml
except ImportError:
    sys.exit(3)
try:
    yaml.safe_load(open(p, encoding="utf-8"))
except Exception as e:
    print(f"DOES NOT PARSE: {e}")
    sys.exit(1)
sys.exit(0)
PYEOF
)
      rc=$?
      if [ $rc -eq 0 ]; then
        row "$name" PASS "clean, parses"
      elif [ $rc -eq 3 ]; then
        row "$name" SKIP "no YAML parser on this machine — readability checked, parse NOT CHECKED (and not passed)"
      else
        row "$name" FAIL "$out"
      fi
    done
    [ $found -eq 0 ] && row "$(basename "$dir")" SKIP "no canonical state file at this root — a gate reading it would report UNGOVERNED"
  done
fi

# 4. The dice, the scaffold and the integrity check -----------------------------------
# roll-brief.py and niche-grow.py decide what a run is about, and a run against a
# broken dice produces a book plus a RUN_REPORT nobody can re-derive.
# check-manuscript-integrity.py is here for a different reason: it is a check that
# has never been seen to fail, which is the state this project keeps getting bitten
# by. Twelve contaminated lines sat inside one chapter of La merienda in sentences
# that read correctly on both sides, and no prose gate could see them.
# init-book.py is here because a book was being born failing row 3 above: on Windows
# Python's text mode wrote every state file CRLF, so seven books on disk carried a
# CR that grep cannot see and row 3 calls a defect (2026-10-15). The scaffold's own
# self-test reads its bytes back and refuses to pass if the CR has returned.
# errata-store.py is the record layer's other half (row 7 runs prune-stale, which
# repairs the records; this one indexes and compacts them). Its self-test is what
# proves an append does not rewrite the records already in the store - so it runs
# here rather than when someone remembers.
# outcome-ledger.py is here for the same reason: it is the only channel that can tell
# the loop it is wrong about the world, and a channel that runs when someone
# remembers is the 2026-09-30 Hollow Bridge entry over again.
# ductus.py is the same class again: a voice whose ledger path has rotted would have a
# run writing taste into another voice's book, and isolation is structural or it is
# decoration.
echo "4. the harness self-tests"
if command -v python >/dev/null 2>&1; then
  for t in roll-brief niche-grow init-book errata-store outcome-ledger swarm-route ductus check-manuscript-integrity; do
    if [ -f "$ROOT/tools/$t.py" ]; then
      out=$(python "$ROOT/tools/$t.py" --self-test 2>&1)
      rc=$?
      if [ $rc -eq 0 ]; then
        row "$t --self-test" PASS "$(printf '%s' "$out" | tail -1)"
      else
        case "$t" in
          check-manuscript-integrity) why="a check nobody has seen fail is not a check" ;;
          init-book)                  why="a book scaffolded here would be born failing its own state row" ;;
          errata-store)               why="the store cannot be trusted to keep what it was given" ;;
          outcome-ledger)             why="the loop has no working way to hear that it was wrong" ;;
          swarm-route)                why="a swarm run would route findings nobody can check" ;;
          ductus)                     why="a run would draft under the wrong voice's taste" ;;
          *)                          why="the dice cannot be trusted to reproduce a roll" ;;
        esac
        row "$t --self-test" FAIL "exit $rc - $why"
      fi
    else
      row "$t --self-test" SKIP "$t.py not found at tools/ - nothing to test"
    fi
  done
else
  row "roll-brief --self-test" FAIL "python not found; the dice cannot be checked"
fi

# 5. Improvement mode -------------------------------------------------------------
echo "5. improvement mode"
if [ -f "$ROOT/SELF_IMPROVEMENT.md" ]; then
  mode=$(grep -m1 -E "^\s+mode:" "$ROOT/SELF_IMPROVEMENT.md" | sed -E "s/.*mode:\s*([a-z]+).*/\1/")
  case "$mode" in
    hand|supervised|auto) row "improvement.mode" PASS "$mode" ;;
    *) row "improvement.mode" FAIL "unreadable in SELF_IMPROVEMENT.md — a mode that cannot be read is a mode nobody chose" ;;
  esac
else
  row "improvement.mode" FAIL "SELF_IMPROVEMENT.md not found"
fi

# 6. Embedded instruments --------------------------------------------------------
# A book that carries its own copy of the gates can be measured by a stale one:
# a quarantined copy of check-uniformity.py under a book's `_archive/tools/`
# (quarantined 2026-10-13) fails U1 at 30% while the frozen copy fails at 22% (recorded in
# tools/run-gates.sh). run-gates.sh never runs
# a book-embedded copy, but a human with a shell might, and a result must be
# attributable to one known instrument. The scan matches by instrument NAME: a
# book's own tool (track_words.py, build-epub.py) is its apparatus and is left
# alone; a copy of THE instruments is the trap. Quarantining (_archive/) or
# deleting the copy is the author's call - this row deletes nothing.
echo "6. embedded instruments"
inst_names=$(find "$ROOT/tools" -maxdepth 3 -type f \( -name '*.py' -o -name '*.sh' -o -name '*.tsv' \) 2>/dev/null | sed 's#.*/##' | sort -u)
hits=$(for base in "$ROOT/test-books" "$@"; do
  [ -d "$base" ] || continue
  find "$base" \( -name _archive -o -name archive -o -name dist -o -name __pycache__ -o -name .git -o -name .agents \) -prune -o -type f \( -name '*.py' -o -name '*.sh' -o -name '*.tsv' \) -print 2>/dev/null
done | sort -u)
found_inst=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in "$ROOT/tools/"*) continue ;; esac   # the instruments themselves
  n=$(basename "$f")
  if printf '%s\n' "$inst_names" | grep -qxF "$n"; then
    row "$(dirname "${f#$ROOT/}")" FAIL "$n is a book-carried copy of the instrument - a stale copy mis-measures, run-gates never runs it but a shell might. Quarantine under _archive/ or delete."
    found_inst=1
  fi
done <<< "$hits"
[ $found_inst -eq 0 ] && row "embedded instruments" PASS "no book carries a copy of the instruments"

# 7. Record hygiene -----------------------------------------------------------
# The self-prune's check half. The record files (ERRATA.md, GATE_FREEZE.md,
# KNOWN_FINDINGS.md) carry standing claims about the program - counts, tallies,
# statuses - and the program moves while the claims stand still. That drift is the
# failure class the author hit: ERRATA.md opened with "the ten controls" against a
# suite that runs nineteen. prune-stale.py measures the live program and reports the
# disagreement; --apply repairs what is provable in place (old wording preserved in
# maintenance/PRUNING_LOG.md) and reports the rest for a ruling. This row CHECKS;
# it never writes. A dated entry is never edited by either mode.
echo "7. record hygiene"
if command -v python >/dev/null 2>&1; then
  if [ -f "$ROOT/tools/prune-stale.py" ]; then
    out=$(python "$ROOT/tools/prune-stale.py" --check 2>&1)
    rc=$?
    if [ $rc -eq 0 ]; then
      row "prune-stale --check" PASS "records agree with the live program"
    else
      row "prune-stale --check" FAIL "stale record claim(s) - run: python tools/prune-stale.py --apply (old wording goes to maintenance/PRUNING_LOG.md; dated history is reported, never edited)"
    fi
  else
    row "prune-stale --check" FAIL "tools/prune-stale.py not found - record drift would go unnoticed"
  fi
else
  row "prune-stale --check" FAIL "python not found; the records cannot be checked against the program"
fi

echo
if [ $fails -gt 0 ]; then
  echo "PREFLIGHT FAIL - $fails row(s) failed, $skips skipped. The failing rows name their fix."
  exit 1
fi
if [ $skips -gt 0 ]; then
  echo "PREFLIGHT PASS - with $skips row(s) SKIPPED. A skip is named, not passed."
  exit 0
fi
echo "PREFLIGHT PASS - instrument, copies, and state are known."
exit 0
