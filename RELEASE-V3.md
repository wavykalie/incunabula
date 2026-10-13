# Incunabula v3 — release record

**Released:** 2026-10-05 · **Origin:** an external review of the pipeline, run against
`kagiroi-drift` (Short Novel Edition) after its delivery pass.

## What this file is, and what it is not

The repository carries **no version field** — not in `skills/incunabula/SKILL.md`, not in
`skills/incunabula-codex/SKILL.md`, not in the README, not anywhere. The installed skill
copies in `~/.agents/skills` say "V4" and are stale relative to the repo they came from,
so they cannot be used to name a release either. So: this record stamps v3, and
`GATE_FREEZE.md` remains the authoritative change log. There is no v1 or v2 record in
this repository to diff against; the freeze history is the history, and this file is the
summary of what the last five freezes did and why.

**v3 in one sentence:** the pipeline learns to record what a character looks like, what
mechanism resolved a chapter, and when a wound had to fire — and gains a way to see, at
drafting time, where in the file a rule actually bites.

## What changed

Five changes, all of them from the same review, all adopted on author direction rather
than on a measured comparison. None of them can fail a book.

| # | change | where | freeze |
|---|---|---|---|
| 1 | Resolution mechanisms. N2 compared declared arc *strings*, so eight distinct arcs could hide one circuit resolving four chapters running. Beats now carry `mechanism` — free text, deliberately not a closed vocabulary — and N2 reports a mechanism succeeding more than twice consecutively. | `check-narrative.py`, `narrative-ledger-schema.md`, `proof-panel` | 14 |
| 2 | Wound timing. `debt.fire_by` gives a core wound the chapter by which it must re-stage; N1 reports an OPEN wound past its milestone, and reports a non-integer `fire_by` rather than ignoring it. | `check-narrative.py`, schema, both narrative fixtures | 15 |
| 3 | Register range. V2's book-level breath-share cannot tell a reader *which scenes* to check, so V2 gained a per-chapter breath map, and the `proof-panel` Hostile gained the working-register question with the map named as its evidence. | `check-dialogue-tags.py`, `proof-panel` | 16 |
| 4 | A drafting surface. `tools/lint-chapter.py` renders `deslop-check.sh`'s 36 rules as `line:col` spans, reading the rule table live out of the scanner and holding none of its own. | new tool, `README.md`, `setting` | 17 |
| 5 | A place to write the result down. `NARRATIVE_LEDGER.yaml` gained `lint_run` and `lint`, so a lint run survives the terminal — and `lint.state: instrument` distinguishes a finding about the book from a finding about the gate. | ledger schema, `check-narrative.py` untouched | 18 |

Plus the pipeline's other half of the review, which is not an instrument change at all:
an intake **Round 4 — What people look like** (frame, muscle, beauty register, movement,
anti-tropes, sensory signature), mirrored into `ENTITY_STATE.yaml` so `case-keeper`
carries it and `collator` can audit against it. That one has no freeze number because
`intake-schema.md` and `case-keeper/SKILL.md` are skill files whose changes are named in
the freeze record rather than hashed; it is recorded in `ERRATA.md` 2026-10-05.

Four `ERRATA.md` entries were appended under **2026-10-05 — Kagiroi Drift production
review** — the resolution-circuit gap, the intake/physique gap, the un-fired foundation
trauma, and the dialogue register collapse. All four are `state: observed` with `n: 1`,
and all four write their motive as the author's account rather than as a measurement.

## What did not change

- **No gate can fail differently.** Every row added in v3 is a report. N1's delivery gate
  already forbade shipping OPEN debt, so `fire_by` is a timing signal; N2's repetition
  rows were already report-only; V2 was already report-only; `lint-chapter.py` gates
  nothing. The rate limit in `SELF_IMPROVEMENT.md` — one promotion per channel per book —
  is respected: craft moved on author direction (round 4, the register question, the
  ledger's `mechanism` declaration), measurement did not.
- **`tools/prose/` is untouched at every hash.** `deslop-check.sh` still reads
  `20e1976d20312974`, the hash it has carried since Freeze 12. The v3 linter reads that
  file rather than copying it, which is the only reason a drafting aid could be added
  without touching a gate.
- **No book was re-run.** `kagiroi-drift` was linted, not revised; nothing in the
  manuscript changed.

## The instrument defect v3 found

Running the new linter over all 8 chapters disagreed with `deslop-check.sh` on exactly one
rule, across three chapters — and the scanner was wrong.

`A23` (parenthetical dash) is written `—[^—\n]{1,70}—`. In POSIX ERE a backslash inside a
bracket expression is a literal backslash, not an escape, so the class is *em-dash,
backslash, or the letter n*. The rule can only fire on a parenthetical dash containing
neither. Measured read-only over the installed calibration corpus — 449 chapter files,
2,562,491 words — the frozen regex matches **561 of the 1,159** occurrences the rule was
written to match: it cannot see 51.6% of them. Fiction alone, 421 of 855.

It is not a one-character fix, and that is the interesting part. `deslop-check.sh` states
its own rule — cap ≈ 1.5× the worst calibration document. Under the reading A23 was
*meant* to have, the worst fiction chapter on the corpus reads **6.03/1k**, which puts the
cap near 9/1000 rather than the present 3/1000. So fixing the regex while keeping the cap
would fail published Hardy and Eliot, and fixing it while keeping the *recorded* worst
would be a silent loosening dressed as a bug fix. Separately, `CALIBRATION.md` records
A23 as "85 occurrences, 1.79/1k" from "the 48 narrative documents" with no path, and that
figure is not reproducible from any subset installed here — so the provenance of the
number that makes the cap trustworthy cannot currently be checked by anyone.

Author ruling: **record as proposed, leave the frozen scanner untouched.**
`deslop-check.sh` is unmodified. The entry is `ERRATA.md` 2026-10-05, `state: proposed`,
with the order of operations written down: identify the derivation corpus, re-measure
under the corrected regex, set the cap from that, then re-key and re-run the controls.
`kagiroi-drift` is unaffected either way — its worst true reading is 0.80/1k against a
3/1000 cap.

It is not in `KNOWN_FINDINGS.md`, and that is deliberate: that file is for findings the
author has seen and declined to fix. This one has been reported and is awaiting a ruling.

## Verification

| check | result |
|---|---|
| `verify-freeze.sh` | **FREEZE HOLDS** — 19/19 rows ok, no row re-keyed since Freeze 16 |
| `validate-controls.sh` | **PARTIAL (exit 2), by design** — 19 shipped-fixture assertions ok, 0 unexpected failures; 5 controls did not run because no corpus is installed at the default path. Exit 2 never means fully validated |
| `check-errata.py` | **OK** — 49 entries, all seven fields, valid motives and states, Rejected registry at its floor of 30 |
| `check-narrative.py` (kagiroi-drift) | **exit 0** — N1 clean, N4 conformant with the new `lint_run`/`lint` sections parsed and ignored |
| `deslop-check.sh` (kagiroi-drift) | **exit 0** — 8 chapters, 0 hard slop; this is the run that surfaced the A23 defect |
| `lint-chapter.py` (kagiroi-drift) | **exit 0** on all 8 chapters, 0 chapters over cap across 36 rules |
| `sync-skills.py` | **no drift** — 29 skills match `~/.claude/skills` and `~/.agents/skills` byte-for-byte |
| `preflight.sh` | **PASS** with 1 row SKIPPED (state hygiene, no project root given — a skip is named, not passed) |

The preflight earned its place during this release. After the Freeze 18 schema edit,
`sync-skills.py --check` failed and preflight reported `PREFLIGHT FAIL - 1 row(s) failed`
— the installed copies of `incunabula-codex` were stale, which would have made every
measurement in this document meaningless, exactly as KF-004 describes. `sync-skills.py` is
the named fix, it is idempotent, and the re-run is green above. A row that fails loudly
during a release is the freeze working, not the release being broken.

Two refusals worth recording, because the tools were right and the change was wrong:
a single `lint:` section holding both scalars and a findings list **fails** N4 at the
parse ("list item under non-list section"), because the parser only promotes a section to
a list while it is still empty; and A23's proposed fix fails for the same reason its
blind spot is dangerous — the number that would authorise it is not attributable.

## Still open

1. **A23** — awaiting an author ruling on the re-derivation. Nothing moves until then.
2. **Controls 4–7** — a corpus *is* installed at
   `tools/prose/calibration/corpus/{multivolume,nonfiction,montgomery}` (303 / 143 / 3
   files), just not at the default path `HUMAN_CORPUS` looks for. Running the full suite
   is an environment variable, not an acquisition.
3. **`CALIBRATION.md` provenance** — "the 48 narrative documents" names no path. Every
   figure in that table inherits the problem A23 makes visible.
4. **Pre-existing file damage**, untouched and unrelated to v3: `ERRATA.md` and
   `GATE_FREEZE.md` each carry a corrupted first line (a stray table fragment before the
   H1). Noted here rather than fixed, because a silent repair of a frozen-adjacent file
   is the thing this directory is against.

## Attribution

Author direction throughout. Nothing in v3 was adopted on a held-out comparison, and
nothing in v3 is labelled as if it were: the craft moves are the author's rulings and the
measurement moves are the author's calibrations, in that order, which is the firewall the
three-channel rule exists to keep.
