#!/usr/bin/env bash
# run-phases — the phase runner. Control, not content.
#
# WHY THIS EXISTS
#   Every phase transition used to be an agent choosing to comply: the engine
#   "does not invoke skills; it tells the user which one to run", and the only
#   proof a gate ran was the agent's own report. Books skipped gates that way.
#   This runner makes the existing gates unavoidable. It reads the phase chain
#   from tools/phase-map.yaml (the single source of truth), runs each phase's
#   gate TOOLS itself, parses their EXIT CODES — never a report — and refuses to
#   advance on anything but 0. On any failure it hard-stops: the project state
#   file is marked HALTED with a resume pointer naming the phase, the gate, and
#   the exit code.
#
# WHAT IT IS NOT
#   It is not a gate and deliberately not a row in GATE_FREEZE.md. It writes no
#   prose and scores nothing; it sequences, invokes, and refuses. It adds no
#   gate (GATE_FREEZE.md; the rewrite skill's rule) — every command it runs is a
#   tool that already existed, with its own exit contract and its own freeze
#   attribution. Same exemption class as preflight.sh and run-gates.sh.
#
#   It enforces the mechanical half only. The map's `human` field (user
#   approvals, judgments, the skill layer's content work) is printed beside each
#   phase and enforced by nothing here. A CLEAR from this runner covers the
#   gates it ran. It never covers the human column, and it never means the book
#   is good.
#
# USAGE
#   bash tools/run-phases.sh <book-root> [--from <id>] [--to <id>]
#   bash tools/run-phases.sh <book-root> --tick proof-pull|revision [--chapter <n>]
#   bash tools/run-phases.sh <book-root> --waive <rule> --chapter <n|book> --reason <text>
#   bash tools/run-phases.sh --list
#
#   <book-root> is the project directory holding PROJECT_STATE.yaml and
#   manuscript/chapters/. Without --from, the walk starts at the phase recorded
#   in the state's runner block (the resume pointer), or at phase 1.
#
#   --tick records one more iteration of a capped loop - proof-pull's three per
#   chapter, or the revision 5->4 loop's three per book - in PROJECT_STATE.yaml.
#   The refusal is in code: a fourth request exits 1 and marks the loop
#   ESCALATED, and a later walk into an ESCALATED loop refuses to dispatch at
#   all. "Do not run a fourth" used to be a sentence; now it is the state file.
#   --chapter resets a proof-pull counter when the chapter changes (the
#   proof-pull counter is per chapter; revision_cycles is per book).
#
#   --waive records a waiver in maintenance/WAIVERS.md - the "waived in
#   writing" of the composing review gate, in one ledger the runner appends to
#   and tools/prose/check-waivers.py audits across chapters. It records the
#   declaration; it clears no gate. A waived gate still halts the walk: fix the
#   row, or declare the waiver and resume past that phase explicitly with
#   --from, on the record.
#
# EXIT
#   0  every requested phase's gates were CLEAR; the state advanced. For --tick,
#      the iteration was recorded; for --waive, the declaration was appended.
#   1  HALTED: a gate or artifact failed, a capped loop refused another
#      iteration, or an ESCALATED loop refused dispatch. The state file says
#      where to resume and why.
#   2  refused to start: bad invocation, unknown phase id, or no state file
#   3  could not run: no python, or the phase map is missing or unparsable

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
STATE_TOOL="$HERE/phase-state.py"

if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "run-phases: no python on PATH - the runner cannot read its map. Exit 3."
  exit 3
fi

usage() {
  awk 'NR>1 && !/^#/{exit} NR>1{sub(/^# ?/,""); print}' "${BASH_SOURCE[0]}"
}

if [ "${1:-}" = "--list" ]; then
  rows="$("$PY" "$STATE_TOOL" phases)" || exit 3
  echo "phase map: tools/phase-map.yaml (single source of truth)"
  echo
  printf '%-5s %-22s %-14s %s\n' "id" "phase" "skill" "gates at the exit"
  while IFS=$'\x1f' read -r id name skill artifacts gates human; do
    printf '%-5s %-22s %-14s %s\n' "$id" "$name" "$skill" "${gates:--}"
  done <<< "$rows"
  exit 0
fi

if [ $# -lt 1 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  usage
  [ $# -ge 1 ] && exit 0
  exit 2
fi

BOOK_IN="$1"; shift
FROM=""; TO=""; TICK=""; CHAPTER=""; WAIVE_RULE=""; REASON=""
while [ $# -gt 0 ]; do
  case "$1" in
    --from) FROM="${2:-}"; shift 2 ;;
    --to)   TO="${2:-}"; shift 2 ;;
    --tick) TICK="${2:-}"; shift 2 ;;
    --chapter) CHAPTER="${2:-}"; shift 2 ;;
    --waive) WAIVE_RULE="${2:-}"; shift 2 ;;
    --reason) REASON="${2:-}"; shift 2 ;;
    *) echo "run-phases: unknown argument $1"; usage; exit 2 ;;
  esac
done

if [ ! -d "$BOOK_IN" ]; then
  echo "run-phases: no such book directory: $BOOK_IN"
  exit 2
fi
BOOK="$(cd "$BOOK_IN" && pwd)"
CHAPTERS="$BOOK/manuscript/chapters"
cd "$ROOT" || exit 3

# The waiver ledger the runner appends to and check-waivers.py audits (B4).
# Created empty on first use: a book that has never waived anything is the
# healthy state, not a missing file, and the audit row must be able to say so.
ensure_waivers_ledger() {
  local f="$BOOK/maintenance/WAIVERS.md"
  [ -f "$f" ] && return 0
  mkdir -p "$BOOK/maintenance"
  cat > "$f" <<'EOF'
# Waiver ledger

Declared waivers for this book, one entry per waiver, appended by
`bash tools/run-phases.sh BOOK --waive RULE --chapter N --reason TEXT`.
Audited by `tools/prose/check-waivers.py`, which holds the entry format and
fails when the same rule is waived in more than three consecutive chapters.
This is the "waived in writing" the composing review gate requires. The
long-term catch for a recurring waiver is the press-ledger errata path - a rule
waived by a second book is an ERRATA.md entry; this ledger is per-book.
EOF
}

# --- --tick: one more iteration of a capped loop (B3) --------------------------
if [ -n "$TICK" ]; then
  tick_args=(state tick --root "$BOOK" --loop "$TICK")
  [ -n "$CHAPTER" ] && tick_args+=(--chapter "$CHAPTER")
  "$PY" "$STATE_TOOL" "${tick_args[@]}"
  exit $?
fi

# --- --waive: declare a waiver into the one ledger (B4) -----------------------
if [ -n "$WAIVE_RULE" ]; then
  if [ -z "$CHAPTER" ]; then
    echo "run-phases: --waive needs --chapter N (or 'book' for a book-scoped row)."
    exit 2
  fi
  if [ -z "$REASON" ]; then
    echo "run-phases: --waive needs --reason TEXT - a waiver without a reason is"
    echo "            a skip wearing a waiver's clothes, and the auditor refuses it."
    exit 2
  fi
  ensure_waivers_ledger
  WAIVERS="$BOOK/maintenance/WAIVERS.md"
  n=1
  while grep -q "^## W-$(printf '%03d' "$n") " "$WAIVERS"; do n=$((n + 1)); done
  wid="$(printf 'W-%03d' "$n")"
  {
    printf '\n'
    printf '## %s — %s — chapter %s — %s\n' "$wid" "$(date +%Y-%m-%d)" "$CHAPTER" "$WAIVE_RULE"
    printf -- '- reason: %s\n' "$REASON"
  } >> "$WAIVERS"
  echo "run-phases: waiver $wid recorded in maintenance/WAIVERS.md"
  echo "            chapter $CHAPTER, rule $WAIVE_RULE."
  echo "            This is the declaration, not a pass: the gate it excuses still"
  echo "            exits nonzero. To advance, fix the row, or resume past the phase"
  echo "            explicitly (bash tools/run-phases.sh $BOOK_IN --from <id>) - on"
  echo "            the record. Recurring waivers are counted:"
  echo "            python tools/prose/check-waivers.py $BOOK_IN"
  exit 0
fi

# --- the map, into two tables -------------------------------------------------
PHASES="$("$PY" "$STATE_TOOL" phases)" || exit 3
declare -A GATE_CMD
while IFS=$'\t' read -r gid gcmd; do
  [ -n "$gid" ] && GATE_CMD[$gid]="$gcmd"
done < <("$PY" "$STATE_TOOL" gates) || exit 3

phase_exists() {
  printf '%s\n' "$PHASES" | cut -d$'\x1f' -f1 | grep -qx "$1"
}

if [ -n "$FROM" ] && ! phase_exists "$FROM"; then
  echo "run-phases: --from $FROM is not a phase in tools/phase-map.yaml"
  exit 2
fi
if [ -n "$TO" ] && ! phase_exists "$TO"; then
  echo "run-phases: --to $TO is not a phase in tools/phase-map.yaml"
  exit 2
fi

# A state file is where the halt and the resume pointer live. No state, no run.
if ! "$PY" "$STATE_TOOL" state show --root "$BOOK" >/dev/null; then
  echo "run-phases: refusing to run without a project state file."
  exit 2
fi

if [ -z "$FROM" ]; then
  saved="$("$PY" "$STATE_TOOL" state show --root "$BOOK" \
           | sed -n 's/^  current_phase: "\(.*\)"/\1/p' | head -1)"
  if [ -n "$saved" ] && phase_exists "$saved"; then
    FROM="$saved"
    echo "run-phases: resuming at phase $FROM (the state's resume pointer)."
  else
    FROM="$(printf '%s\n' "$PHASES" | head -1 | cut -d$'\x1f' -f1)"
  fi
fi

halt() {  # halt PHASE GATE RC REASON
  "$PY" "$STATE_TOOL" state halt --root "$BOOK" --phase "$1" --gate "$2" \
      --exit "$3" --reason "$4" >&2
  echo
  echo "run-phases: HALTED at phase $1 ($2, exit $3)."
  echo "            $4"
  echo "            The state file is marked HALTED with a resume pointer:"
  echo "            re-run 'bash tools/run-phases.sh $BOOK_IN' to resume here,"
  echo "            or --from <id> to restart the walk at a named phase."
  exit 1
}

run_gate() {  # run_gate PHASE GATE_ID -> returns the tool's exit code
  local phase="$1" gid="$2" tpl cmd out rc
  tpl="${GATE_CMD[$gid]:-}"
  if [ -z "$tpl" ]; then
    echo "run-phases: the map names gate '$gid' but declares no command."
    halt "$phase" "$gid" 3 "the phase map is incomplete for gate $gid"
  fi
  cmd="${tpl//\{book\}/$(printf '%q' "$BOOK")}"
  cmd="${cmd//\{chapters\}/$(printf '%q' "$CHAPTERS")}"
  echo "---- $gid"
  echo "     command: $cmd"
  out=$(bash -c "$cmd" 2>&1)
  rc=$?
  printf '%s\n' "$out"
  if [ "$rc" -eq 0 ]; then
    echo "     => CLEAR (exit 0)"
  else
    echo "     => NOT CLEAR (exit $rc)"
  fi
  echo
  return $rc
}

echo "================================================================="
echo "run-phases - the 17-phase chain against one book"
echo "book:    $BOOK"
echo "map:     tools/phase-map.yaml (single source of truth)"
echo "control: this runner enforces gate exit codes only. It writes no prose"
echo "         and scores nothing. The 'human' line under each phase is the"
echo "         skill layer's work and is enforced by nothing here."
echo "================================================================="
echo

# --- pre-run: the pattern preflight.sh started — refuse before the run --------
for gid in preflight registry; do
  echo "==== pre-run: $gid =============================================="
  run_gate "(pre-run)" "$gid" \
    || halt "(pre-run)" "$gid" "$?" "pre-run gate $gid refused the run - fix it before any phase"
done

walking=0
last="$(printf '%s\n' "$PHASES" | tail -1 | cut -d$'\x1f' -f1)"
while IFS=$'\x1f' read -r id name skill artifacts gates human; do
  if [ "$id" = "$FROM" ]; then walking=1; fi
  [ "$walking" -eq 1 ] || continue

  echo "==== phase $id — $name ($skill) ================================="
  echo "     human (recorded, NOT enforced here): $human"
  echo

  # loop caps (B3): an ESCALATED loop refuses dispatch - in code, not prose
  loop=""
  case "$id" in
    4.5) loop="proof_pull" ;;
    5)   loop="revision_cycles" ;;
  esac
  if [ -n "$loop" ]; then
    loop_state="$("$PY" "$STATE_TOOL" state loop --root "$BOOK" --loop "$loop")"
    lcount="$(printf '%s' "$loop_state" | cut -f1)"
    lstatus="$(printf '%s' "$loop_state" | cut -f2)"
    lcap="$(printf '%s' "$loop_state" | cut -f3)"
    if [ "$lstatus" = "ESCALATED" ]; then
      echo "---- loop:$loop"
      echo "     $lcount of $lcap iterations used - status ESCALATED. The runner"
      echo "     refuses to dispatch another: the cap is enforced in code."
      echo
      halt "$id" "loop:$loop" 1 "the $loop loop is at its cap ($lcount of $lcap) and ESCALATED - the next move is a human decision (fix, accept, or escalate as structural), not another iteration"
    fi
  fi

  # artifacts: an absent artifact is a failure, never a pass
  IFS=',' read -r -a arts <<< "$artifacts"
  for a in "${arts[@]}"; do
    [ -n "$a" ] || continue
    if ! compgen -G "$BOOK/$a" >/dev/null; then
      echo "---- artifact"
      echo "     $a — MISSING under the book root"
      echo
      halt "$id" "artifact:$a" 1 "required artifact $a does not exist - the phase's content work is not done"
    fi
    echo "---- artifact"
    echo "     $a — present"
    echo
  done

  # gates: exit 0 from every one, or the run stops here
  IFS=',' read -r -a gl <<< "$gates"
  for g in "${gl[@]}"; do
    [ -n "$g" ] || continue
    [ "$g" = "waivers" ] && ensure_waivers_ledger
    rc=0
    run_gate "$id" "$g" || rc=$?
    if [ "$rc" -ne 0 ]; then
      if [ "$g" = "uniformity" ]; then
        echo "     composing's review gate: a uniformity row is fixed, or waived in"
        echo "     writing. Put the writing on the one ledger, then fix the row or"
        echo "     resume past this phase explicitly - both are on the record:"
        echo "       bash tools/run-phases.sh $BOOK_IN --waive U<n> --chapter book --reason <why>"
        echo "       bash tools/run-phases.sh $BOOK_IN --from <next phase id>"
        echo "     A waived gate still halted this run: the waiver is a record, not a"
        echo "     pass. Recurring waivers are counted by tools/prose/check-waivers.py."
      fi
      halt "$id" "$g" "$rc" "gate $g did not return CLEAR - not-run is never a pass"
    fi
  done

  nxt=""
  after="$(printf '%s\n' "$PHASES" | awk -F'\x1f' -v p="$id" 'f{print $1; exit} $1==p{f=1}')"
  [ -n "$after" ] && nxt="$after"
  "$PY" "$STATE_TOOL" state advance --root "$BOOK" --phase "$id" --next "$nxt" >&2
  echo "     phase $id CLEAR — advanced to ${nxt:-COMPLETE}."
  echo

  if [ "$id" = "$TO" ]; then
    echo "run-phases: stopped after --to $id as asked. State advanced."
    exit 0
  fi
  if [ "$id" = "$last" ]; then
    echo "run-phases: the whole chain is CLEAR. The human column above is still"
    echo "            unenforced: gates passing is not the book being good."
    exit 0
  fi
done <<< "$PHASES"

if [ "$walking" -eq 0 ]; then
  echo "run-phases: start phase $FROM was never reached in the map."
  exit 2
fi
