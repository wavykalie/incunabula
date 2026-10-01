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
# state file that would not parse (KF-004), and a stray CR that hid from grep (KF-005).
# A check that has never been seen to fail is not yet known to work — so every row here
# names its own state, including the states where it could not look.
#
# USAGE
#   bash tools/preflight.sh [project-root ...]
#
#   With no project root, the state-hygiene rows are reported SKIPPED, not passed.
#   With one or more roots (a book directory or a books root), every canonical state
#   file found there is checked.
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

# 4. Improvement mode -------------------------------------------------------------
echo "4. improvement mode"
if [ -f "$ROOT/SELF_IMPROVEMENT.md" ]; then
  mode=$(grep -m1 -E "^\s+mode:" "$ROOT/SELF_IMPROVEMENT.md" | sed -E "s/.*mode:\s*([a-z]+).*/\1/")
  case "$mode" in
    hand|supervised|auto) row "improvement.mode" PASS "$mode" ;;
    *) row "improvement.mode" FAIL "unreadable in SELF_IMPROVEMENT.md — a mode that cannot be read is a mode nobody chose" ;;
  esac
else
  row "improvement.mode" FAIL "SELF_IMPROVEMENT.md not found"
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
