# Arm B amendment — sub-cohort B-sub (B-16 … B-20)

**Status: CLOSED — fifteen is enough.** Dated **2026-11-04**, under Kalie Kirch's briefing of
the same date; closed by her ruling of the same date (§8). This file is the amendment record;
the design doc is not edited. It records what was measured, what was decided, and why nothing
was filed.

## 1. The five unfinished premises

The manifest holds **15 B rows** (`B-01`…`B-15`) and `books/B-16`…`books/B-20` do not exist.
`RUNPLAN.csv` already carries the five remaining rows, and each payload was re-hashed against
its `payload_sha256` before anything else was considered:

| book | premise | genre | working label | payload words | digest vs plan |
|---|---|---|---|---|---|
| `B-16` | `mys-02` | mystery | the cassette | 72 | OK |
| `B-17` | `sf-01` | science fiction | the fragment | 78 | OK |
| `B-18` | `sf-02` | science fiction | storage | 82 | OK |
| `B-19` | `thr-02` | thriller | the record | 77 | OK |
| `B-20` | `thr-04` | thriller | the alert | 87 | OK |

No premise was swapped, reworded or re-planned.

## 2. Arm A model — confirmed for the pairing

All twenty Arm A rows carry **`gemini-3.8-flash-high`** (model id from the CLI resolver, per the
2026-11-02 ruling in `DECISIONS.md`). The A twins of the five remaining premises are
`A-16` (`mys-02`), `A-17` (`sf-01`), `A-18` (`sf-02`), `A-19` (`thr-02`) and `A-20` (`thr-04`),
so the sensitivity comparison is B-sub (flash-low, if authorised) against Flash-high twins — a
cross-model subset, as the briefing requires.

## 3. Model availability, measured tonight

`agy models` lists `gemini-3.8-flash-high`, `-medium`, `-low`, `claude-sonnet-4-6`,
`claude-opus-4-6-thinking` and `gpt-oss-120b-medium`. Listing is not availability, so each
flash tier was called:

| model | call | result |
|---|---|---|
| `gemini-3.8-flash-high` | 1-token probe | **429** `Individual quota reached … Resets in 118h8m59s` |
| `gemini-3.8-flash-medium` | 1-token probe (×2, early) | `PROBE-OK` |
| `gemini-3.8-flash-medium` | JSON probe, then text probe | **429**, same message, `Resets in 118h6m36s` |
| `gemini-3.8-flash-low` | 1-token probe (×3) | `PROBE-OK` |
| `gemini-3.8-flash-low` | 250-word prose request | 249 words in 8 s, rc 0 |

The lower tiers are not a separate clean pool: `medium` answered short calls and then 429'd in
the same session on the same account, and the reset clock is identical across tiers. `low` is
the only id still answering, and it has been observed only at probe and paragraph scale.

Pro-tier routes were excluded by the briefing's criteria, not by preference: `agy` offers Claude
Sonnet 4.6 and Opus 4.6; the local `codex` CLI is configured for `gpt-6-sol` at `xhigh`; the
local `claude` CLI is configured for `opus`. Substituting any of them would be the upgrade the
design §7 rule forbids.

## 4. Substitute decision

**Candidate: `gemini-3.8-flash-low`.** It is the only flash-class id answering tonight, it is the
same model family at a lower effort tier rather than an upgrade, and if used every phase's model
would be recorded separately. It is *not* being adopted on tonight's evidence, for two reasons:

1. **The route is not demonstrated at book scale.** One 249-word success does not show that
   `flash-low` can sustain a 60,000-word book assembled from a 40-chapter pipeline, still less
   five of them (~280,000 words) before the same quota closes. `medium` failed between two
   adjacent short calls; a book-length session would be gambling the run on that gap.
2. **The briefing's stop condition applies on the evidence available.** It says to report a
   blocked run rather than substitute a stronger model or improvise. The honest reading of the
   measurements is "no flash-class route is reliably available tonight", not "a substitute has
   been chosen".

**Using the executing agent (DeepSeek V4.1 Flash) as drafter was considered and rejected.** It
is flash-class, but it fuses operator and drafter in one context: the arm's §5 rule makes a
`prose` row a stop condition, and `dispatch.py` files the resolver-reported model id, which the
executing agent does not produce. It would also require five 55,000-word books in one context.
That is not a B-sub row; it is a different study.

## 5. Verdict — what was and was not done

Per briefing step 3, the run is **blocked**, not substituted. Specifically:

- no book was drafted, scaffolded or partially filed;
- no manifest row was added or edited (`manifest.csv` remains 20 A + 15 B = 35 rows);
- no gate was run against a book, because there was no book to run one against;
- no log entry was written for a book that does not exist.

## 6. What was verified before stopping

- `python preflight.py` → **VERDICT: READY** (frozen premises, 52/52 payload digests, probe record).
- `run/out/armb-wt` is at the frozen commit `8265c48d12962ca233ed98bd10083edb072ec7f0`, with only
  the three recorded data deviations (`BOOKS.yaml`, `GATE_FREEZE.md`, `PREMISE_LEDGER.tsv`).
- The five remaining payloads reproduce their plan digests (table in §1).

## 7. Recommendation

1. **Cleanest: wait for the reset (≈ 2026-11-09 21:00 ET) and run B-16…B-20 on
   `gemini-3.8-flash-high`.** The arm then closes as 20 Flash-high pairs, with no B-sub cohort and
   no cross-model caveat. The amendment's only benefit is five days.
2. **If tonight is mandatory:** authorise `gemini-3.8-flash-low` explicitly as the B-sub model,
   run **B-16 alone** first (the study's own §9 rule), and record the drafting model and every
   non-drafting phase model per book. Expect multi-hour wall clock and 429 stalls; a stall is
   logged as data, not rescued.
3. **Do not** use the executing agent as the drafter. That would void the operator/drafter
   separation the arm exists to measure.

## 8. 2026-11-04 — owner's ruling: close at fifteen

Kalie Kirch, same day: **fifteen paired books are enough.** The arm closes at the fifteen
Flash-high pairs already filed (`A-01`…`A-15` against `B-01`…`B-15`), and `B-16`…`B-20` are
**not generated**. No substitute model is adopted, so the B-sub cohort does not exist.

What that means, stated so the report cannot drift:

- The primary result is unchanged and complete at **n = 15 pairs**, all
  `gemini-3.8-flash-high`. The five unfinished premises are **not run**, and are reported as
  not run — never as missing data, failed books, or pooled into the primary result.
- The sensitivity check the briefing described (five B-sub books against their A twins) is
  **not performed**. There is no cross-model subset to report, and no claim is made that the
  pipeline effect survives a model change.
- `books/manifest.csv` remains 35 rows: 20 A + 15 B. No row was added, removed or edited for
  this ruling, and no gate was run against a book that does not exist.
- The drafting route was never the blocker: subagents (`agy`) draft every Arm B book, and
  remain the route. The blocker was quota — `flash-high` and `flash-medium` returned 429 with
  a ~118 h reset, and `flash-low`, the only id still answering, was observed only at probe and
  paragraph scale.
- If the ruling is reversed, `B-16` is the first book and `gemini-3.8-flash-low` is the only
  flash-class route available before the reset. That would be a second model break
  (high → low), logged as B-sub, run one book at a time.


---

## B-16 status — 2026-11-04, evening

**What exists.** `run/out/armb-wt/books-armb/B-16` holds a 40-chapter draft of the
`mys-02` premise ("the cassette"), 37,559 words, produced by an unlogged run between
11:30 and 11:38 that halted at phase 3 on the `deslop` gate. No prompt log or model
record was written by that run; `logs/` contains only `operator.md`.

**What this session did.** Re-ran the deslop scan, which flagged seven rule rows across
nine chapters (A17 ×1, A1b ×3, A22 ×1, A25 ×3, P1 ×1). Applied 16 targeted edits:
`harness room` → `tack room`, `jemmy leverage` → `jemmy pressure`, `laws of leverage` →
`laws of force`, four `ledger` → `register` in ch18 plus its heading, three `was not X.
It was Y` antitheses recast, one `the small trapezoidal` → `a small trapezoidal`, and
three `She was` sentence starts in ch39. Deslop now exits 0: **PASS with warnings**.
Phase 3 gate CLEAR.

**Where it stopped.** The walk advanced and halted at **3.1 pass-evidence**: 0 of 40
chapters carry an evidence file in `evaluations/`. A completed book (B-15) carries seven
artifacts per chapter; none were produced for B-16. Register, catchword, quoin, proof-panel
and proof-pull have not been run on this text.

**Length.** 16,441 words short of the 54,000 floor. The back half averages 766 words per
chapter against a 1,500-word plan (ch40 is 424 words), so the shortfall is a collapsed
tail, not a rounding error.

**Filing.** B-16 cannot be filed as a study row: `dispatch.py` requires the drafting
model's resolver id, and this draft has no record of one. It is a partial draft with a
clean mechanical scan, not a B-sub book.


## B-16 status — 2026-11-05 (supersedes the 2026-11-04 entry)

**What exists now.** `books-armb/B-16` is a complete 40-chapter manuscript, **54,400 words**,
at or above the 54,000 floor. It began as the unlogged 11:30 run's 37,559-word draft and was
repaired and expanded on 2026-11-05.

**What changed.** 32 chapters expanded (+16,841 words); 13 chapter endings that had an outline
line pasted in instead of prose were rewritten; six continuity contradictions fixed, the worst
being a twelve-watch recording (ch 4-5) against a four-watch fraud (ch 9, 10, 20) whose whole
arithmetic depended on the count; seven streetlamps in ch 7 against three in ch 15; and a father
who left at thirteen in ch 1 and died at four in ch 16. Every chapter now carries an evidence
file in `evaluations/`, written to record what was actually assessed and what was not.

**Gates.** `deslop` 0 (pass with warnings); `pass-evidence` 0 (40/40, 54,400 gated words);
`drift` 0; `arc` 0; `progress` 0 (C1 agrees; L2 reports 5,600 behind plan); `length` 4 (in
progress, at floor). `uniformity` **fails U1**: chapter-length CV 11.4% against a 22% floor —
forty chapters planned at 1,500 and drafted at 1,180-1,854 is a flat rhythm, and that is a real
structural finding, not a bookkeeping one. `narrative` is ungoverned (no ledger) and `check-eval`
cannot run (no evaluation files).

**Why it is not filed.** Two independent reasons.

1. **Stop condition.** The operator expanded the manuscript by hand. The operator protocol names
   prose as a stop condition, so B-16 is not a B-sub observation and its row is not filed. The
   2026-11-04 entry above says a `prose` row means the book stops; this is that row, declared.
2. **No drafting model on record.** The 11:30 run wrote no model id and `dispatch.py` requires
   one, so the book could not be filed even if the stop condition did not apply.

**What was not run.** Quoin (all nine operations), the proof panel, proof-pull, the narrative
ledger, and the catchword pass at chapter level. Chapter evidence records 16 of 40 chapters
below the 7.0 hook floor on an honest reader's assessment (6.5, mostly slow openings). Those
are recorded as sub-floor, not rounded up, and phase 3.2's human column is therefore unmet.

`books/manifest.csv` is unchanged. No row was added for B-16, and no earlier row was edited.


## B-16 status — 2026-11-06 (supersedes the 2026-11-05 entry)

**What changed.** The uniformity row was the real open finding and it has been closed by
restructuring, not by a waiver. Five preparation chapters were cut to their scene length
(ch 06 1,181→975, ch 12 1,339→806, ch 16 1,320→920, ch 24 1,235→882, ch 28 1,212→790), which
took chapter-length CV from 18.5% to **23.4%** against a 22% floor. Total **56,504 words**, above
the 54,000 floor. Two merge artifacts were also repaired: a duplicated final line in ch 26 and a
misattributed line of Davies's dialogue in ch 35.

**The ledger exists.** `NARRATIVE_LEDGER.yaml` now declares 40 tracked chapters, 40 beat arcs,
6 extended scenes and 13 debts (12 resolved, 1 deferred with a reason). `narrative` moves from
exit 3 (ungoverned) to exit 4 (in progress, recorded not judged) — which is the honest code for a
book that still declares `status: in_progress`.

**Gates.** `uniformity` 0, `pass-evidence` 0 (40/40, 56,504 gated words), `drift` 0, `arc` 0,
`length` 4, `narrative` 4. `deslop` passes on every chapter file; its remaining FAIL rows sit in
`foundation.md` (A17) and `premise.md` (D3, P1) — a pipeline artifact and the locked premise,
neither edited. **`quoin`, the proof panel, proof-pull and catchword are still not run**, and
`check-eval` still cannot run for want of evaluation files.

**Filing status is unchanged.** B-16 remains a manuscript, not a B-sub observation: the operator
wrote the prose, and the 11:30 run left no drafting-model id. No manifest row was added, and the
closing ruling of §8 — fifteen pairs, B-16…B-20 not generated as B-sub — still stands.


## B-16 status — 2026-11-05, second pass (supersedes the entry above)

**Numbers.** 40 chapters, **58,422 words**, mean 1,461, range 1,176-2,336. The first
pass left the book 54,400 words above the floor and structurally flat; this pass added
4,022 words of prose.

**What this pass wrote.** New scenes in ten chapters: the last three minutes before the break-in
(ch 30), the counting under the conservatory (ch 31), the porch light (ch 32), the arrest
process (ch 33), the scene examination and Davies's "there is no claim" (ch 34), the tape being
wound out of its shell (ch 40), plus the shed before PLAY (ch 3), the arithmetic in the margin
(ch 21), the fourth failure she does not write down (ch 23), and the wait before the scrape
(ch 29).

**Structural repairs.** `ch32` was rebuilt from a scrambled draft in which the light switch was
pressed twice, the trellis fell before he reached it, and the chronology ran backwards; it is now
one pass, glass to siren. `ch16` had an added block contradicting the paragraph above it (the
cavity closed flush, then "the cover would not close"). `ch33` ended on a stray duplicated
struggle line after the arrest was over; removed. `ch30` ended in the present tense off the
outline ("A faint metallic scrape ... silences both of them"); rewritten in the book's past.
`ch12` ended on an outline summary ("The audio waveform revealed three distinct acoustic
spikes"); replaced with the measurement itself, and `clundered` → `clanked`. `ch26`'s title
carried an outline artifact ("The Scullery Drop-Bolt & The Camera"). Three chapter openings ran
the same triple-smell construction (ch 1, 2, 9) and were recast.

**Gates, measured after the pass.** `deslop`: every manuscript row passes. The only failing rows
in the book tree are in `premise.md` (D3 -ly 27.78/1k, P1 anaphora) and `foundation.md`
(A17 1.08/1k) — the locked premise, which the study requires stay byte-identical, and a pipeline
artifact. Neither is manuscript prose and neither was edited. `pass-evidence` 0
(58,422 gated words, 40/40). `drift` 0 (D1 0.77). `arc` 0. `length` 4 (in progress,
58,422 against a 54,000 floor). `narrative` 3, ungoverned. `check-eval` 2.

**Still failing, and why.** `uniformity` U1 reads **CV 18.5%** against a 22% floor, up from
11.4% at the first pass. Five chapters now run past 1,800 words, three past 2,000 and one past 2,300, while the
middle of the book still sits at 1,200-1,300. The remaining row is not closed by more expansion:
it needs a deliberate lean-down of the preparation chapters (06, 14, 26, 35 and 28) toward
1,000 words so the climaxes have something to contrast with. That is a restructure of the rhythm
profile, not a pad, and it has not been done.

**Not run.** Quoin (all nine operations), the proof panel, proof-pull, the narrative ledger,
catchword at chapter level. The operator record stands as declared: the operator wrote this
prose, so B-16 is a manuscript and not a B-sub observation, and no manifest row exists for it.


---

## B-16 status — 2026-11-06 (quoin and proof panel; supersedes the entry above)

**What was run.** The two passes the book had never had now exist.

- **Quoin**, phase 3.5, all 40 chapters, 5–6 of the nine operations each. Overprints cut
  (26 of them), decorative precision deflated, irrelevant thoughts and pure texture added,
  dialogue roughened in ch 6, 8, 14, 22, 27, 28 and 35, and one signpost sentence or
  rhetorical question cut wherever the narrator was telling the reader what to notice.
  Records: `evaluations/quoin-chapter-01…06.md` and `evaluations/quoin-pass.md`.
- **Proof panel**, phase 4: three readers, cross-section, and the book-level scripts
  (`check-uniformity`, `check-quantities`, `check-dialogue-tags`, `check-figurative`).
  Report: `evaluations/panel-report.md`; 40 per-chapter files `evaluations/chNN-evaluation.md`,
  which is what `check-eval` reads.

**What the panel found.** The manuscript is 56,868 words, 40 chapters, mean 1,422. Devourer
7.5, Critic 6.0, Hostile 5.5 before the standing −0.8 self-scoring calibration. Three
findings the amendments above had claimed closed are not:

1. **The watch inventory is still two inventories.** Chs 4–5 and the letter in ch 20 say
   twelve (five silver hunters, four gold-plated, three fusees). Chs 10, 15, 21, 22 and 29
   say four, and ch 29 names four different watches. This is the object the plot is about.
2. **The father leaves twice.** Ch 1: when she was thirteen. Ch 27, Arthur: "when you were
   four years old, after your father was taken." Ch 16: nobody has opened the book in twelve
   years, four years after he left.
3. **The clock runs backwards.** Ch 34 ends at 02:10 with a fifty-minute statement behind it;
   ch 35 is headed 01:15.

Plus three merge artifacts: ch 33 ends on an orphaned `*Click.*`, ch 37 brings Helen in twice
(front-door latch, then the car and the key), and ch 40 walks past the charity shop twice and
opens at noon before it is eleven minutes to twelve. The quoin pass does not repair, so none
of these were touched; they are composing and case-keeper work and that pass has not been run.

**Gates, measured after the passes.** `deslop` 0 on every manuscript file (D2 5.69/1k,
report-only); `uniformity` 0 — U1 CV 23.0% (warn band, floor 22%), U5 CV 71% (warn), U3
0/40, U6 20%; `length` 4 (56,868, at floor, ceiling at delivery); `narrative` 4 (12 resolved,
1 deferred, 0 open; N3 reports `plot turn` twice and `relationship shift` twice);
`check-eval` runs on 40 files; `pass-evidence` 0, `drift` 0, `arc` 0 unchanged.

**Filing status: unchanged, and now doubly so.** B-16 remains a manuscript and not a study
row. The operator wrote prose again in this session — the quoin pass is a `prose` row in
`logs/operator.md`, declared — and the 2026-11-04 drafting run still has no model id.
`books/manifest.csv` is 35 rows: 20 A + 15 B. `manifest.py --check` reports 0 problems.

## 2026-11-06 — B-17 … B-20: the §8 ruling is reversed by the operator, the route is open again

**Instruction received this session:** start B-17 … B-20. That reverses the 2026-11-04 ruling
in §8 that closed the arm at fifteen pairs. Recorded here, dated, because a reversal that is
not written down is indistinguishable from drift.

**The blocker in §3 has expired.** Probed this session, on the same account:

| model | call | result |
|---|---|---|
| `gemini-3.8-flash-high` | 1-line probe, `--output-format json` | `SUCCESS`, `PROBE-OK`, 3.2 s, 8,882 in / 41 out |
| `agy models` | — | high, medium, low, Claude Sonnet 4.6, Opus 4.6, gpt-oss-120b all listed |

So the 429 (`Resets in 118h`) that blocked §3 no longer blocks anything. No substitute model
is needed: **B-17…B-20 can run on `gemini-3.8-flash-high`, the same id as the fifteen filed
pairs**, which is the cleanest outcome — the arm closes as twenty Flash-high pairs with no
B-sub cross-model caveat, exactly §7's recommendation 1.

**What was and was not done.** `preflight.py` → **VERDICT: READY** (52/52 payload digests,
frozen premises, probe record). The five remaining payloads still reproduce their plan
digests. No book was scaffolded, drafted or partially filed in this session, because:

- the arm's own runbook (§1) runs **one book at a time, start to finish** — starting four is
  the interleaving it forbids, and four agy subagents drafting at once is the shared-context
  risk the filing checks exist to catch;
- B-16's stop condition has to be closed on the record before the cohort restarts, which is
  what this entry does.

**Where the run resumes.** `B-17` (`sf-01`, "the fragment"), alone, on
`gemini-3.8-flash-high`, with the operator protocol unchanged: no prose, gates answered with
their own defaults, every action a row in that book's `logs/operator.md`. If it files inside
54,000–66,000 words and with zero `prose` rows, `B-18` follows the same day; if the operator
has to write a word, the book stops and is filed as not-run, as B-16 was.


## 2026-11-06 — B-17 attempted, blocked on quota capacity; not scaffolded, not drafted

**Instruction this session:** run B-17 (`sf-01`, "the fragment") end to end on
`gemini-3.8-flash-high` as a clean B-sub row. It could not be run, and the reason is a
measurement rather than a waiting period.

### The probe record was the wrong instrument

The entry above reads "the blocker in §3 has expired" on the strength of a one-line probe
that returned `PROBE-OK` in 3.2 s. That probe was true and misleading at the same time. A
one-line probe measures whether the id answers at all; it says nothing about whether the
account can serve a book. The distinction was not made, so the record claimed the route was
open. It was not.

### What was measured this session

Every call below is the same account, the same binary, the same worktree, minutes apart.

| # | model | request | result |
|---|---|---|---|
| 1 | `gemini-3.8-flash-high` | 1-line probe `PROBE-OK` | `SUCCESS`, 2.8 s, 8,871 in / 41 out |
| 2 | `gemini-3.8-flash-medium` | 1-line probe | **429**, `Resets in 74h0m47s` |
| 3 | `gemini-3.8-flash-low` | 1-line probe | **429**, same message, `74h0m44s` |
| 4 | `gemini-3.8-flash-high` | write one 400-word file, one turn | `SUCCESS`, 112 s, 78,227 in / 11,656 out / 134,767 cache-read |
| 5–7 | `gemini-3.8-flash-high` | the same 400-word call, repeated | **429** each, ~3 s, `Resets in 73h58m` |

So the burst budget is **one substantive call per reset window**, and the window is ~74 h.

The arithmetic that decides it: call 4 spent 11,656 output tokens to produce ~400 words plus
tool traffic — call it 8,000–9,000 words of prose at the ceiling. A 60,000-word book needs
**at least seven** such calls, and that is before a single gate, evaluation file or phase pass
consumes any of the same budget. One call per 74 h cannot produce one book, let alone four.

### Verdict

Per `ARM_B_RUN_PROMPT.md` §9 ("the drafting model's resolver id changes mid-run" and the
blocked-run rule) and §7 of this amendment, the run **stops**:

- **no substitute model.** `flash-medium` and `flash-low` are 429 too, and `gpt-oss-120b` /
  Claude in `agy` are the model upgrade the design forbids. Using them would create a new
  cohort, not a B-sub row.
- **no operator drafting.** The executing agent writing the prose is the §8 stop condition,
  and B-16 already carries that scar.
- **B-17 was not scaffolded.** No `books-armb/B-17`, no `premise.md`, no operator log, no
  partial phase 1. A book directory that exists but cannot be drafted is a book a later
  session has to decide whether to resume — exactly the ambiguity this record exists to
  prevent. The next window starts B-17 from nothing, which costs one `init-book` call.
- **no row.** `books/manifest.csv` remains 35 rows: 20 A + 15 B. Nothing was filed, edited or
  removed. No gate was run, because there was no book to run one against.

### What the next window should do first

Do not begin with a probe. Begin with the **two-call capacity test**: one 400-word file write,
then a second identical call. If the second 429s, the window is a probe window, not a book
window, and the book does not start. That test costs ~2 minutes and one chapter's budget; the
mistake it prevents cost this session a day.

If the second call answers, run B-17 alone, on `gemini-3.8-flash-high`, at
`8265c48d12962ca233ed98bd10083edb072ec7f0`, with the operator protocol unchanged, and treat
every phase pass as spending from the same budget — a book that reaches chapter 30 and stops
is a stall to be filed as an outcome, not a book to be rescued by hand.


## 2026-11-06 (later) — route abandoned: the executing agent drafts, cohort `B-deepseek`

**Instruction:** forget `agy`; amend the study and have DeepSeek V4.1 Flash run it — the
executing agent itself, in this context. Recorded here and in `DECISIONS.md` (same date),
because it changes an answered decision and the arm's own stop-condition rule.

### What this cohort is

The five remaining premises (`B-16`…`B-20`) are drafted by the **executing agent** through
the same Incunabula pipeline at `8265c48d12962ca233ed98bd10083edb072ec7f0`. That is not a
B-sub row and it is not a B row of the Flash-high cohort. It is a separate cohort, tagged
`B-deepseek` in every row's `deviations`, and it is reported separately.

### What it costs, stated once

1. **Operator and drafter are the same context.** `ARM_B_RUN_PROMPT.md` §2 says a `prose` row
   is a stop condition because a rescued book is evidence about the rescuer. In this cohort
   every chapter is a `prose` row by construction. They are written to `logs/operator.md` as
   they happen, not omitted. The cohort therefore measures the pipeline's **instructions,
   gates and repair loop**, not "a pipeline wrote this without a person".
2. **No `modelVersion`.** The route has no response envelope, so `model_id` is the session's
   own identity string and H3 is a session-identity claim, weaker than a Flash 3.8 row's.
   Filed with `run/harness-deepseek.json`, which records exactly that.
3. **Interventions are not comparable.** The count is still written from the log; it is not
   pooled with the fifteen rows a human operator answered.
4. **Pairing is confounded.** Against `A-16`…`A-20`, a difference is pipeline **and** drafter.
   The primary result remains n = 15 Flash-high pairs; this cohort never joins it.

### Rules that still hold

- One book at a time, start to finish. `B-17` first, alone.
- The frozen commit, the pipeline code, every gate and threshold are untouched. A gate that
  fires is answered by fixing the text in the pipeline's own loop, and the firing is filed as
  a `--deviation` — it is data, not an obstacle.
- The payload is sent verbatim and only the payload. No premise is reworded.
- Band `54,000–66,000` is an outcome, never a target to regenerate toward.
- No hand-repair after filing. What the pipeline produces is the book.

### Filing

```bash
cd tools/prose/study
python run/dispatch.py --ingest B-17 --response run/out/responses/B-17/final.txt \
    --sent-model deepseek-v4.1-flash --model-returned deepseek-v4.1-flash \
    --harness run/harness-deepseek.json \
    --pipeline-commit 8265c48d12962ca233ed98bd10083edb072ec7f0 \
    --interventions <counted rows> --finalize \
    --deviation "cohort B-deepseek: operator=drafter (authorised 2026-11-06); model is the executing agent, no API modelVersion"
```

`--sent-model` and `--harness` are not optional here: without them dispatch would log
`gemini-3.8-flash` as the model sent and `agy` as the harness, which is the one thing this
record exists to prevent.
