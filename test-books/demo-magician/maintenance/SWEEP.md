# SWEEP — The Trick

**Run 2: 2026-10-01, at 34 of 34 chapters. 80,394 words. THE sweep.** Run per
`FULL_SWEEP.md`, once, at the end. This file replaces run 1's rather than appending
to it, as run 1's own closing line said it would.

Run 1 (2026-09-28, at 15 of 34 chapters) found two things worth keeping in one
paragraph: U6 read 80% antithesis — a tic no per-chapter check could see — and was
fixed to 20% with three chapters kept for declared reasons (ch 1 the L2 clue sentence,
ch 3 the demonstration, ch 6 Sigrid's method); and L1 had never run at all, because
`PROJECT_STATE.yaml` declared `declared_floor`/`declared_target` and the gate reads
`target_floor_words`/`target_ceiling_words` — exit 2 had been saying NOT RUN inside
output I had read past. Both key pairs now live in the state file.

## The list

| row | result | verdict | action |
|---|---|---|---|
| freeze | 15/15, `FREEZE HOLDS` | **PASS** | — |
| L1 length | 80,394 / 80,000–95,000 | **PASS** | 394 above the floor. True and thin; not to be made fatter on purpose |
| deslop (34 ch) | warnings only, exit 0 | **PASS** | warnings are dash-spelling notes and D2, inside every cap |
| U2 rhythm | spread 25.50 | **PASS** | — |
| U3 coda | 0/34 | **PASS** | — |
| U5 para variance | CV 96% | **PASS** | — |
| drift | one voice, first to last | **PASS** | — |
| arc A1 | changes direction | **PASS** | — |
| names | no collision, none at top of the prior | **PASS** | — |
| premise | job+engine unspent in the catalogue | **PASS** | — |
| comps | 16 rows, all stamped, 0 unverified | **PASS** | — |
| outline | OK, 3 warnings | **PASS** | the warns are the runs the outline itself declares deliberate (4–5, 11–12, 32–33) |
| surplus | 19,475 speech words / 1,141 turns | report | no row gates, by design |
| recoverable | dialogue share 25% | report | no row gates, by design |
| U4 | 59% one-sentence paragraphs | advisory | no convention declared; not a row |
| **U1 spread** | CV 22.8% (band 33.4–45.1) | **WARN** | **closed** — KF-007, the one decision |
| **U6 frames** | antithesis 11/34 (32%) | **WARN** | **fixed at the narrator's desk, residue closed** — KF-008 |
| **hand: ledger** | L18 in no outline column | **FIX** | added to ch 18's cell — fixed, not closed |
| hand: hard rules | 1919 planted ch 4 → paid ch 23; sixth effect never named; killer never in POV | **PASS** | — |
| hand: cold solve | rows land: 23/25 (ch 19→31), 24 (ch 21), 27 (ch 21→22), 30 (ch 30→31) | **PASS** | — |

A row that passes is not evidence of quality. Six rows here are advisory or
report-only, and `check-drift` holds on 34 chapters partly because it is one book
by one voice. This is a measurement.

## The three findings, each in a bucket

**1. U1 — CLOSED (KF-007).** CV 22.8%, warn under 28%, and the drafted book is more
uniform in length than the published band. It was drafted under
`DRAFTING_FRAMEWORK.md`, which rules in terms: *"No manuscript should be edited to
satisfy it twice."* The 17/17 bimodal plan that scored 33.70% on paper is exactly
the arithmetic-satisfiable design the framework withdrew — U1 cannot tell "these
chapters differ because they contain different things" from "because a plan put them
in two buckets," and the per-write ceiling then pulled the long half toward the
middle anyway. Chapters are as long as the things in them take. The row is not wrong
and is not suppressed; it keeps firing, and the answer now lives in a table.
Reopen when a measure of genuine chapter-length variety exists and this book fails it.

**2. U6 — FIXED at the narrator's desk, residue CLOSED (KF-008).** Measured 12/34
(35%); 18 instances found across 12 chapters. **17 of the 18 are spoken** — including
all five in ch 3, which run 1 kept because the construction is the demonstration. The
one narrator's-desk instance was ch 34's *"Nine inches is not a height. It is the
height a hall gives a person"* — a sentence my own expansion pass had added on
2026-09-30 — and it was rewritten by merging the sentence break, run 1's method.
Re-measured: 11/34 (32%), ch 34 out. The residue above the warn line is dialogue in
every remaining chapter, and the recorded taste (COMMONPLACE, 2026-09-30) is that
spoken formulas are voice and the fix applies at the narrator's desk only — the gate
cannot tell the speakers apart, and the reader has to. Closed with that reason.

**3. L18 — FIXED, not closed.** The ledger census of `outline.md` found L18 referenced
in **no** chapter's ledger column, while its content — the `[presumed / actual]`
notation — is planted in ch 18's prose and recalled in ch 24, and ch 18's own synopsis
features it. The evidence is intact; the index was wrong. A ledger contradiction is a
defect by definition, so: `L16, L17, L21` → `L16, L17, L18, L21`. One cell.

## What the sweep ran on

The expansion pass finished first, per the author's instruction before this sweep:
ch 21 took the Handover (clue row L24 — the word appeared nowhere in the manuscript
and the outline gives the row to ch 21) and ch 31 stated its own title's thesis (a
trick is done to a retinue; a hall of witnesses is the opposite of one, which is why
the only thing a hall can be given is a hand trick). Deslop clean on both. A
line-ending repair restored the ten files the edit passes' wrap helper had left mixed
(CRLF file, LF breaks) to each file's own drafting convention; prose untouched in all
ten. The `check-comps` invocation in `FULL_SWEEP.md` was stale — it passed a file
path where the gate wants the book directory — and the first run of this sweep exited
on it. The command is fixed in that file; the gate was right and the procedure
document was wrong.

## Termination

34 chapter files, count unchanged. Three findings, each assigned: two closed in
`incunabula/KNOWN_FINDINGS.md` with reasons and reopen conditions, one fixed and
re-checked by its own gate (U6 re-run: 11/34; deslop re-run on ch 34: PASS). No
fourth bucket was used. **The sweep is finished.**
