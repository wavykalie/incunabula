# RUN_REPORT — Quiet Hours (NF Conventions Demo Run)

Run date: 2026-10-08 · Mode: nonfiction (`book.mode: nonfiction`, primary field) · Status: complete

## What this run was

The first end-to-end run of the nonfiction pipeline: a short prescriptive guide to
bedtime routines (5 chapters, 1,987 words) staged to exercise every gate under
`mode: nonfiction` — the scoped register row (Freeze 20, CALIBRATION.md §21), the
rows that step aside for nonfiction, and the rows that are live in every mode.

Two design notes:

- **The A10a hits are deliberate.** Chapter 1 carries "due to the fact that" and
  chapter 3 "At its core," — one each, the register the §20 sweep scoped. Under
  fiction or an undeclared mode these FAIL the scanner (control 17, arm 2); under
  `mode: nonfiction` they report as `--`. The contrast is the demo.
- **This is the first staged book to declare the mode through the primary
  `mode:` field** rather than the legacy positioning/genre fallback.

This run changed no tooling: at delivery the gates sat at their Freeze 20 hashes.
The two instrument findings below were resolved the same day in **Freeze 21** —
`check-names.py` gained its nonfiction case and `validate-controls.sh` gained
controls 18–19 (the names case, and a pin on the A24 blind spot).
`deslop-check.sh` remains `35ed380c20db520e`.

## Voice seam found and repaired (D1)

The first full-gate run **failed D1 voice-step at 4.51** (fail above 3.41):
`fw_and` 31.0 → 20.5/1k, `fw_it` 18.6 → 7.7, `fw_of` 24.7 → 9.0 between the first
two and last two chapters. Chapters 1-2 were nouny-abstract ("the fumes of a
day", "a change of state"); 4-5 were plain-imperative. That is the seam the gate
exists to name.

Repaired by rewriting across it, not by padding: ch-01/02 shed "of"-phrases and
"it"-clauses; ch-04/05 gained the texture the prescriptive register wants anyway
("the discomfort of a hotel room", "the arithmetic of illness"). Per-feature
half-steps afterwards: and 0.4, it 0.1, of 0.4, on 0.8.

D1 now reads 1.91 — warn band, below the fail line. The remaining steppers
(`punct` 5.68, `ttr` 5.07) are small-sample features on ~400-word chapters;
recorded, not tuned away.

## Gate Status at Delivery

| Gate | Target / Threshold | Result | Status |
| :--- | :--- | :--- | :--- |
| **Deslop HARD rows** | zero violations | 0 across 5 chapters | **PASS** |
| **Deslop A10a (scoped)** | report, not fail, under `mode: nonfiction` | `--` x1 ch-01 ("due to the fact that"), x1 ch-03 ("At its core,") — CALIBRATION.md §21 | **PASS (scoped)** |
| **Deslop report tier** | prompts only, cannot fail | D2 rule of three 4.85/1k in ch-05 (cap 5/1000, report only) | WARN (report-only) |
| **U1 length variance** | fiction band 33.4–45.1% | CV 15.7% — advisory on a nonfiction book (ERRATA 2026-09-27; published non-fiction spans 28.2–113.7%) | N/A advisory |
| **U2 rhythm variance** | fail under 3.0 (published min 4.32) | spread 3.14 — chapter means 11.5–14.6 words/sentence | WARN |
| **U3 coda distribution** | fail above 25% | 0/5 chapters (0%) | **PASS** |
| **U4 single-line paragraphs** | advisory on nonfiction | 2% | N/A advisory |
| **U5 para-length variance** | advisory on nonfiction | CV 39% | N/A advisory |
| **U6 signature-frame** | fail above 40% | "refrain" in 1/5 (20%) | **PASS** |
| **D1 voice-step** | fail above 3.41 | 1.91 (4.51 at first run — see seam note) | WARN |
| **D2 sustained trend** | warn above 0.75 (advisory row) | `ttr` rho +0.80 on a 5-point series of ~400-word chapters | WARN (advisory) |
| **A1 arc** | ≥ 0.35 reversals/bin | 1 window at 1,987 words — not measurable, not a finding | N/A |
| **S1–S4 surplus** | narrative property | declared nonfiction; all rows report-only ("a low S1 in nonfiction is not a finding") | N/A (reported) |
| **L1 declared length** | 1,850–2,250 words | 1,987 (494/374/301/406/412) | **PASS** |
| **N1 narrative debt** | nothing open at delivery | 3 resolved, 0 deferred, 0 open | **PASS** |
| **N3 pure texture** | no cap set by this directory | 38% of declared scene words | N/A (reported) |
| **N4 ledger schema** | conforms, covers every chapter file | ok | **PASS** |
| **Names** | zero cross-book collisions | no named cast — `reported, not run`, exit 0 (Freeze 21); see note 1 | N/A (reported) |

## Instrument notes

1. **check-names had no nonfiction case — fixed the same day (Freeze 21).** It
   exited 2 ("Failing rather than passing on an empty read") on a book with no
   named cast, which a prescriptive guide legitimately has — this book's actors
   are "you", "the child", "the grandparent". The gate now reports instead of
   failing for `mode: nonfiction` with no cast (keyed on `conventions.py`, the
   same single reader as surplus and arc), while fiction and undeclared books
   keep exit 2 and a nonfiction book that declares cast is still checked.
   Control 18 runs all four arms. Re-run after Freeze 21:
   `reported, not run`, exit 0.
2. **A24 case sensitivity.** A sentence-initial "This is why…" coda dodged the
   density row (which matches `grep -oE`, case-sensitively) while F1 and the HARD
   pass read case-insensitively. Logged in `ERRATA.md` 2026-10-08 at
   `state: observed`; the frozen scanner is untouched at `35ed380c20db520e`, the
   sentence was rewritten rather than shipped behind a regex gap, and control 19
   now pins the behaviour (`calibration/a24-case-upper.md` / `a24-case-lower.md`)
   so a silent fix flips the suite instead of re-pricing the density caps
   unnoticed.
3. **U2's published floor (4.32) is measured on full-length novels.** Five
   ~400-word chapters compress sentence-rhythm spread by construction; the warn
   is recorded rather than manufactured away.

## Deliverables

- Book: `manuscript/chapters/chapter-01..05.md` (1,987 words)
- `PROJECT_STATE.yaml` — `mode: nonfiction` (primary field), length contract 1,850–2,250
- `NARRATIVE_LEDGER.yaml` — 3 debts, all closed (promise, skill, clock)
