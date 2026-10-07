the ten controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only) |# ERRATA

The printer's errata sheet: corrections issued after the impression, and observations that
have not yet become corrections.

**Append-only.** Entries are added; entries are never edited to look better than they were.
An entry that turned out to be wrong gets a `WRONG` line under it, and the wrongness stays
visible. That is the point — a ledger with no recorded mistakes is a ledger being curated,
and a curated ledger cannot be trusted with the job.

This file feeds `PRINTERS_COPY.md`. It is the destination that `check-uniformity.py` has
needed since it was written: *"Reproducing the same exemption across books is itself the
pattern this check exists to catch."* The system identified a rule waived three times as
something that should be escalated, and had nowhere to escalate it to. This is that place.

## How an entry is promoted

Nothing here is a rule. An entry becomes a rule in `PRINTERS_COPY.md` only through the
protocol in its §7, and in the default `hand` mode that means a person, reading a diff.

**Three states, and the middle one is the trap:**

| state | meaning | may change a threshold |
|---|---|---|
| `observed` | one book did this | never |
| `proposed` | N books agree and the corpus is named | never — proposals move to the *registry*, not the gate |
| `adopted` | a person applied it to `PRINTERS_COPY.md`, with a diff | only on a corpus change, and only by hand |

A book that trips a rule twice writes a line. It does not move the gate. The reason is in
`PRINTERS_COPY.md` §4 and it is the finding this whole layer exists to respect: a
stylometric finding about human prose is a finding about **the sampled humans**. A threshold
re-derived from six books somebody liked has laundered a period confound into a permanent
constant, and nothing downstream will ever be able to tell.

Set `errata.mode` in `PROJECT_STATE.yaml` to change promotion behaviour — `hand` (default),
`bulk` (auto-promote observations to the project-local copy at three agreeing books), or
`auto` (thresholds may also re-derive, with a printed changelog and never without a named
corpus).

## Entry format

```
### YYYY-MM-DD — one line naming the observation
- **row:**      U4 | A1 | S1 | (brief | delegation) — what it touches
- **observed:** what happened, in one sentence
- **n:**        how many books, and how many independent
- **evidence:** file, tool, corpus, or the number
- **motive:**   aesthetic | privacy — required, and it is a human's account
- **state:**    observed | proposed | adopted
- **proposes:** what would change in PRINTERS_COPY.md, or "none"
```

`check-errata.py` validates this file against that format and against `PRINTERS_COPY.md`'s
own rules. It fails on a missing motive, a missing state, an undated entry, or a `proposed`
entry with no `n`.

---

## 2026-09-27 — VERMILLION reconciliation

The session that created this file. Five entries, in the order they were found.

### 2026-09-27 — U4 fails three human novels in five
- **row:**      U4
- **observed:** The one-line-paragraph floor fails 82 of 140 public-domain English novels
               (59%), and its median — 33.2% — is below its own 35% failure line.
- **n:**        140 novels, 13,041,370 words, five eras, 94 authors
- **evidence:** `tools/prose/calibration/measure-pd-corpus.py`, running
               `check-uniformity.py`'s own arithmetic. Five novels at 11.0, 12.3, 13.4, 13.6,
               14.0 per cent.
- **motive:**   aesthetic — a false accusation here costs an author an injected one-line
               paragraph in a book that does not want one
- **state:**    adopted
- **proposes:** `U4` advisory by default; enforced only on
               `paragraph_convention: commercial-dialogue`. See `PRINTERS_COPY.md` §3.

### 2026-09-27 — U5 passes 140 of 140, and U4 fails 82 of 140
- **row:**      U5
- **observed:** Same method, same corpus, opposite verdict: 0 of 140 human novels fall below
               `U5`'s failure line, against 59% below `U4`'s.
- **n:**        140
- **evidence:** as above. Human paragraph-length CV: min 57, q25 88, median 101, max 189%.
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** nothing. This is the confirmation that `U5` is the row that travels, and it
               is now the strongest entry in the confirmed registry.

### 2026-09-27 — the stated mechanism for U4's band is wrong
- **row:**      U4
- **observed:** `CALIBRATION.md` has asserted since the row was written that dialogue
               manufactures one-line paragraphs, which implied the gate could scope itself to
               dialogue-dense books. Measured, the correlation is r = 0.234.
- **n:**        140
- **evidence:** share of paragraphs that are *entirely* a speech span vs one-sentence share.
               The 19th-century canon is dialogue-sparse and still reaches 77.9%.
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** no automatic trigger. A cut point on that basis would have been invented, and
               an unmeasured one is what this directory forbids. Recorded in the
               **Rejected** registry because the plausible version of this fix is a bug.

### 2026-09-27 — the arc gate's lexicon was truncated, and the assert now catches it
- **row:**      A1
- **observed:** The valence lists were transcribed by hand into `check-arc.py` and 53 of 143
               negative words were dropped — *cold*, *tired*, *hungry*, *war*, *fate*,
               *sick*, *danger*. It inflated arc range roughly twofold and moved the human
               reversal mean from 0.570 to 0.647, which would have invalidated the threshold.
- **n:**        1 transcription, 53 words
- **evidence:** set-length comparison against `vermillion-study/analysis/lexicons.py`:
               121/90 against 121/143. Fixed, and `assert len(...) == 121 / == 143` added at
               import so a re-transcription cannot pass silently.
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** this entry is the argument for `check-errata.py` existing. VERMILLION's line
               about the lexicons being the instrument is not a caution; it is a description
               of a bug that took four minutes to find and would otherwise have shipped.

### 2026-09-27 — A1 does not catch our own AI control
- **row:**      A1
- **observed:** Hollow Bridge, written by a model, scores 0.533 — inside the human range
               and above the warn line. The gate has zero false failures across 140 human
               novels and flags 27% of the measurable machine corpus, and it still misses the
               one machine-written book we own.
- **n:**        1 control book, against 140 human and 83 measurable machine
- **evidence:** `tools/prose/check-arc.py` on `Hollow Bridge`; both corpora measured
               with the same code.
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** record the limit in the tool's own output, not only in its docstring, because
               a marketing pass will otherwise describe this row as a detector. It is a
               floor on a real failure mode and nothing more.

### 2026-09-27 — the arc window was wrong, and reading the source beat more measuring
- **row:**      A1
- **observed:** `check-arc.py` disagreed with VERMILLION by 0.08 on a metric it claimed to
               implement. Cause: it computed ONE curve per novel, while the study computes the
               arc PER 4,000-WORD WINDOW and takes the mean over windows. With the study's
               `windows()`, `SENT_RE` and `ABBREV` copied verbatim, the human distribution now
               matches the published one to three decimals — min 0.469, p25 0.555, q75 0.590,
               max 0.672.
- **n:**        140 novels, 13.04M words
- **evidence:** `engine.py` sets `WINDOW = 4000`; `aggregate()` is documented "Mean over
               windows". The single-curve version reads ~0.08 high on every text, which moves
               a threshold while looking plausible.
- **motive:**   aesthetic — a gate whose calibration cannot be reproduced is one nobody can
               re-derive
- **state:**    adopted
- **proposes:** `TURN_FAIL` moves 0.55 → 0.45 and the floor is now the worst human novel
               rather than a number from a different implementation. The single-curve reading
               is recorded in `CALIBRATION.md` because the wrong version was not obviously
               wrong.

### 2026-09-27 — the null is 0.5, and that is a better claim than "machine reverses less"
- **row:**      A1
- **observed:** A curve of independent steps reverses direction about half the time, so 0.5 is
               this metric's null. Human prose sits at 0.571, above it; machine prose at
               0.501, on it exactly.
- **n:**        140 human, 83 measurable machine
- **evidence:** both corpora measured with `check-arc.py`; the null follows from the sign-change
               rate of a random walk
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** state the null in the tool's output. "Machine prose reverses less often"
               compares two distributions; "machine arcs are indistinguishable from a random
               walk" says what one of them *is*, and is the claim that should survive a new
               corpus. A book under 0.45 is smoother than noise, not merely flat.

### 2026-09-27 — 70 of 153 machine texts are unmeasurable, not passing
- **row:**      A1
- **observed:** The method's unit is a 4,000-word window, so single-chapter serials yield one
               window and no second bin to compare. They are reported as unmeasured.
- **n:**        70 of 153
- **evidence:** `check-arc.py` requires two measurable windows before it will report
- **motive:**   aesthetic — reporting an unmeasured book as passing is the exact class of bug
               this directory's own history contains four of
- **state:**    adopted
- **proposes:** keep it unmeasured, and record the open question in `PRINTERS_COPY.md` §6:
               whether a 2,000-word chapter can be judged for arc at all.

### 2026-09-27 — five "published prose: 0" rules were all false positives
- **row:**      A1a, A2a, A3a, A19, A21
- **observed:** A second native-English corpus (Montgomery, 270,149 words) produced 11 hits
               across all five, and every one is ordinary English: "a soul **subtly** akin",
               "her **robust**, matter-of-fact common sense", "gold and silver brocade
               **tapestry**" (a literal wall hanging), "the **palpable** bids for favor",
               "the first thing is to give your hair a good washing", "the great question".
- **n:**        11 hits / 270,149 words = 0.04 per 1k, against a "zero tolerance" claim
- **evidence:** `corpus/montgomery/`; the scanner's verbatim patterns, re-checked against
               `deslop-check.sh` after a probe of mine mislabelled `A2a` and nearly produced
               a false finding of its own
- **motive:**   aesthetic — a gate that fails *Anne of Green Gables* costs a rewrite and
               teaches the author to avoid ordinary words
- **state:**    adopted
- **proposes:** all five demoted from HARD to a rate cap (~50x the observed rate), tagged
               `[demoted from HARD]` in the output. The ten hard rules that survived a second
               corpus untouched were left alone. Recorded in the **Rejected** registry as
               *zero-tolerance status for any word-list rule*.

### 2026-09-27 — a decimal in a warn field silently disabled the tier I had just added
- **row:**      scanner (all density rows)
- **observed:** The demoted tier was written with `0.5` warn numerators. Bash integer
               arithmetic threw `arithmetic syntax error`, aborted the loop, and the five rows
               **disappeared from the report** — which made both project books PASS the
               scanner, contradicting CALIBRATION §10.
- **n:**        1 bug, 5 rows affected
- **evidence:** caught by asking whether a rule that had just been *weakened* still appeared
               in the output, which is the only reason it was not shipped
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** numerators are integers; the reason is in the source next to `DEMOTED`. This is
               the fifth bug in this directory pointing the same way — the gate reporting
               itself more capable than it was — and the failure mode is worth naming
               generally: **a change that weakens a gate must be verified by confirming the
               gate can still fail.**

### 2026-09-27 — Gutenberg boilerplate was being scanned
- **row:**      scanner (all rows)
- **observed:** `deslop-check.sh` measured licence headers, transcriber's notes and contents
               lists as prose — 3,045 of the 105,546 "words" in one Montgomery file. Two hard
               rules fired inside the header.
- **n:**        every Gutenberg-sourced file ever scanned by this tool
- **evidence:** the strip is now at the top of `scan_file`; word count for that file drops
               from 105,546 to 102,501
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** nothing further. Recorded because this project has tried Gutenberg as a
               calibration source three times and failed twice for reasons that turned out to
               be something else.

### 2026-09-27 — a native-English commercial corpus existed, unused
- **row:**      calibration
- **observed:** Three L.M. Montgomery novels were sitting in
               `_archive/tests/book-genesis-anne-series/source/` as a fixture for a different
               pipeline. They are the first native-English commercial narrative in this
               project, and they immediately refuted five hard rules and independently
               confirmed `U4`'s advisory status from a corpus matching the target register.
- **n:**        270,149 words, 3 books, 1 author, 1923–27
- **evidence:** now at `corpus/montgomery/`; section 11 of `CALIBRATION.md`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** n=1 author is a corpus that can refute a rule and cannot set one. Recorded in
               the **Open** registry as the binding constraint on this calibration — the
               remaining gap is procurement, not research.

## Carried forward, unresolved

### 2026-09-27 — the study's machine corpus is not comparable to ours
- **row:**      A1
- **observed:** VERMILLION's machine figures come from a corpus filtered by `strip_rr_notice`,
               which removes Royal Road anti-piracy notices injected at arbitrary positions
               mid-scene. This directory has no equivalent filter, so its published machine
               numbers describe *that* corpus and not machine prose in general.
- **n:**        153 texts, 83 measurable for us
- **evidence:** our own measurement gives median 0.502 against the study's published 0.500 —
             agreeing on shape, and disagreeing on the extremes as expected
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** nothing. Recorded so that a future reader does not quote the study's machine
               minimum (0.167) as a property of machine prose; ours is 0.256.

### 2026-09-27 — the Gutenberg diagnosis was wrong, twice
- **row:**      calibration
- **observed:** `CALIBRATION.md` records an abandoned attempt to source public-domain
               nonfiction, on the grounds that Gutenberg files use a line-break format making
               paragraph structure unrecoverable. That is false of Gutenberg; the 140-novel
               corpus is blank-line separated and recovers perfectly. The three failed
               candidates had some other problem, and the attempt was given up for the wrong
               reason.
- **n:**        3 abandoned candidates, against 140 that work
- **evidence:** `measure-pd-corpus.py` over `vermillion-study/corpus/human`
- **motive:**   aesthetic — a wrong recorded failure is a task that gets abandoned twice
- **state:**    adopted
- **proposes:** correction applied to `CALIBRATION.md` §10, with the era confound named so the
               corpus is not mistaken for a replacement derivation. Nonfiction is still
               unsourced; the difference is that it is unsourced honestly.

### 2026-09-27 — the justified-inconsistency axis is positionally flat
- **row:**      recoverable
- **observed:** the study's claim that human formal irregularity "clusters at points where a
               motive can be supplied" was measured as the Gini coefficient of tic
               occurrences across ten equal position bins. Every corpus is flat: 19th-c.
               human 0.02 (em dash) to −0.02 (rule of three), Montgomery −0.10 to +0.01,
               machine −0.01 to +0.03. If position carried any of the signal, this is not
               the result.
- **n:**        137 human novels, 3 Montgomery, 120 machine texts
- **evidence:** `tools/prose/calibration/proto-recoverable.py`; section 10 of `CALIBRATION.md`
- **motive:**   aesthetic — a refuted measure re-derived is a rule nobody can check
- **state:**    adopted
- **proposes:** no positional rule may be derived from this study's clustering claim. Entered
               in the **Rejected** registry of `PRINTERS_COPY.md` §4.

### 2026-09-27 — register enrichment is what separates, and it cannot read intent
- **row:**      recoverable
- **observed:** enrichment = share of a tic's occurrences inside quoted speech ÷ the text's
               own dialogue share. Em dash: human 1.75, Montgomery 1.49, machine 0.79. The
               within-corpus confound test is clean (r = −0.06 to +0.28 against dialogue
               share), so the cross-corpus gap is not a format artefact. But the measure is
               about REGISTER, and the claim it was meant to support is about INTENT.
- **n:**        137 human, 3 Montgomery, 120 machine; threshold min 5 hits, 4 chapters
- **evidence:** `tools/prose/check-recoverable.py`, report-only, never gates
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** `check-recoverable.py` ships report-only with its limits in its own output
               and in `README.md`. Thresholds 1.15/0.85 are the prototype's separation points,
               **not measured floors** — recorded as such so no later reader mistakes them for
               calibration. Rare tics (n=1–4 documents) are unmeasurable, so no rule of the
               form "this tic must sit in dialogue" is implementable.

### 2026-09-27 — the `P3` 29-fragment run was never a positional-cluster example
- **row:**      P3
- **observed:** the 29-fragment run in *Anne of Avonlea* was recorded as a worked example of
               the study's positional clustering, in the same section that later measured
               clustering and found it flat. Both claims cannot hold. The run is concentrated
               in TIME; position in the document is not time.
- **n:**        1 claim, refuted against 260 measurable documents
- **evidence:** `CALIBRATION.md` §11, corrected in place
- **motive:**   aesthetic — a wrong mechanism in a section about false claims invites the
               decision to be re-argued and the decision itself to be doubted
- **state:**    adopted
- **proposes:** correction applied. The `P3` warn-only decision **stands**, on the cap
               argument alone: a threshold passing 29 passes the slop fixture's 9, so run
               length does not separate deliberate from accidental clipped sequences.

### 2026-09-27 — three density caps fail real published chapters
- **row:**      D1, D2, A25
- **observed:** the DENSITY caps were derived from the worst rate in a whole published
               DOCUMENT and are enforced per CHAPTER. Slicing the 140-novel public-domain
               corpus into ~2,150-word chapters and running the scanner over a
               stride-sample of 102 of them (84 distinct novels) fails published human
               prose on three rows: `D2` on 19 chapters (18.6%, 19 distinct novels),
               `D1` on 15 (14.7%, 14 novels), `A25` on 1. The worst chapter measured is
               D2 at 8.40/1k against a cap of 5, and D1 at 33.52/1k against a cap of 10
               — verified as genuine U+2014 characters in valid UTF-8, not a parse fault.
- **n:**        102 chapters, 84 novels, 13.04M-word parent corpus
- **evidence:** `tools/prose/calibration/chunk-pd-corpus.py` + `chapter-rates.py`;
               section 12 of `CALIBRATION.md`
- **motive:**   aesthetic — a gate that fails a fifth of the human canon is a gate
               against prose, not against machine prose
- **state:**    observed
- **proposes:** **no cap has been changed yet**, and this is deliberate. Raising D1 from
               10 to 51/1k and D2 from 5 to 13/1k is what 1.5x the worst chapter
               derives, but 1.5x-the-worst is a *floor* for headroom, not a licence to
               absorb a 19th-century outlier. `D1`'s era confound is already on record
               (era medians 2.8–8.7 straddle the cap; 45% of the corpus uses `--` rather
               than U+2014), so a chapter-level maximum is a worse basis for a cap than a
               document-level one. Entered in **Open** as a blocking question for the cap:
               either the caps are raised, or the rows are demoted to warn, and the choice
               needs a multi-author current corpus to make honestly — the same procurement
               gap that blocks every other re-derivation here.

### 2026-09-27 — the scanner's own output was two processes writing one file
- **row:**      method
- **observed:** a full-corpus scan was started and abandoned on a tool timeout. The shell
               pipeline's `awk` stage survived the timeout and kept writing into the same
               output file for a further 7 minutes while a second scan ran on a different
               sample. The result was a sparse file with 249,590 NUL bytes, and
               `grep -c '^== '` reported 302 chapters where the directory held 204.
- **n:**        1 contaminated run; 249,590 spurious NUL bytes
- **evidence:** the file scanned as binary; `grep` and Python disagreed on line count by
               up to 99 headers until the NULs were counted and the strays killed
- **motive:**   aesthetic — a contaminated measurement is worse than no measurement,
               because it looks like a number
- **state:**    adopted
- **proposes:** the re-run was on a fresh output file with 0 NUL bytes, a header count
               equal to the file count, and no process overlap; those three checks are
               now the standing guard before any corpus figure in this directory is
               believed. Recorded here because the first contaminated run also produced
               a plausible-looking per-rule failure table, and only the byte count
               caught it.

### 2026-09-27 — `DRIFT_FAIL` fails 100% of four-chapter published books
- **row:**      D1 (drift)
- **observed:** the voice-step cap of 1.40 was calibrated on three published volumes of 13,
               17 and 18 chapters. The gate splits a book in half by chapter count, so
               the score depends on how many chapters the estimate rests on. Holding text,
               author and voice fixed and varying only the chapter count, 30 published
               novels sliced to 4 chapters score a median of **2.99** and fail the cap
               **30 of 30 times**; at 20 chapters the same prose scores 0.69 and never
               fails. r = -0.777 between chapter count and score. `MIN_CHAPTERS = 4` admits
               precisely the size that fails.
- **n:**        30 published books x 7 chapter counts = 210 measurements
- **evidence:** `tools/prose/calibration/drift-units.py`, which runs check-drift.py's own
               `features()`/`step_and_trend()` rather than re-deriving them
- **motive:**   aesthetic — the gate's own remedy is rewriting a book, and a false
               accusation of voice drift costs a rewrite
- **state:**    observed
- **proposes:** **no threshold changed.** A size-dependent floor, or a minimum chapter
               count above 4, is the fix; both are decisions about published prose and
               §7 requires a person to make them. Filed in **Open**.

### 2026-09-27 — `A1`'s floor is below the worst novel mean but above the worst window
- **row:**      A1
- **observed:** the arc floor of 0.45 is derived from the mean over ~15 windows of a full
               novel (worst 0.469). Per individual 4,000-word window the same corpus
               scatters far wider (sd 0.104 vs 0.035, minimum 0.000): **12.7% of windows
               fall below the floor against 0 of 40 novel means**, and 147 of those 151 are
               well-formed 10-19 bin windows rather than degenerate three-bin artefacts.
               Running the actual gate on published prose truncated to book lengths: 4,000
               words fails 3 of 15, 8,000 fails 1 of 20, 16,000 fails 2 of 20, 32,000
               fails 0 of 10.
- **n:**        1,193 windows / 40 novels; 65 book-length gate runs
- **evidence:** `tools/prose/calibration/arc-units.py` and `arc-short-book.py`
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** the existing **Open** entry claiming short books are merely "unmeasured" was
               wrong in the safe direction and is corrected in `PRINTERS_COPY.md` §6. A
               short book is measured *noisily*, not unmeasured, and the row's
               smoother-than-noise claim does not survive a one-window book (6.6% of single
               windows sit below the 0.500 null). No threshold changed.

### 2026-09-27 — one generalisation: every threshold in this directory has a sample size
- **row:**      method
- **observed:** three separate gates, three measurements, one shape. `D1`/`D2` are derived
               on documents and enforced on chapters. `DRIFT_FAIL` is derived on 13-18
               chapter volumes and enforced on any book with >=4 chapters. `A1` is derived
               on a ~15-window mean and enforced on a book that may have one window. In
               each case the threshold was correct for the sample it was measured on and
               wrong for the sample it is applied to.
- **n:**        3 gates, 1 pattern
- **evidence:** `CALIBRATION.md` §12 and §13
- **motive:**   aesthetic — this is the third instance of one shape and the shape is now
               worth more than any single instance
- **state:**    adopted
- **proposes:** entered in **Rejected**: a fixed threshold independent of sample size is not
               a simplification, it is an unstated claim that the sample is large enough. Any
               new gate must state the sample size its threshold was derived at and the
               sample size it is enforced at, and if they differ the threshold has to move
               with the second one.

### 2026-09-27 — size-dependent floors adopted for `DRIFT_FAIL` and `A1`
- **row:**      D1 (drift), A1
- **observed:** both gates derived a fixed floor on one sample size and enforced it on
               another. Fixing it required measuring a floor at each size AND the cost of
               that floor, because a size-dependent floor can rise above a real defect.
               Measured over 40 published novels with each gate's own code.
- **n:**        40 books x 7 chapter sizes (drift); 1,193 windows / 40 books (arc)
- **evidence:** `calibration/size-floors.py`, `drift-units.py`, `arc-units.py`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** `SIZE_FLOOR` in `check-drift.py` (4ch 3.41, 6ch 3.41, 8ch 2.47, 10ch 1.94,
               12ch 1.73, 14ch 1.76, 16ch 1.60, 20ch+ 1.40) and `WINDOW_FLOOR` in
               `check-arc.py` (1w 0.30, 2w 0.35, 3w 0.41, 4w+ 0.45). Each is the worst
               PUBLISHED document at that size, so a clean book cannot fail. Verified
               against the positive control at every size: two-voice books fail
               12/12, 10/12, 11/12, 11/12, 10/12 across 4-20 chapters, and a synthetic
               monotone-arc fixture fails at 2 windows.

### 2026-09-27 — the 1.5x headroom convention cannot be used on the drift step
- **row:**      D1 (drift)
- **observed:** the project's standing convention is a cap at ~1.5x the worst reference.
               Applied to a size-dependent drift floor it is unusable: the two arms
               (one-voice and two-voice books) **overlap at every chapter count tested**,
               so 1.5x the worst clean book sits ABOVE the weakest real voice change and
               the gate stops firing. An intermediate 24-book run suggested separation
               existed at 10/16/20 chapters; at 40 books that disappeared, so the earlier
               "separable" reading was small-sample noise and was not acted on.
- **n:**        40 books x 7 sizes = 280 paired measurements
- **evidence:** `calibration/size-floors.py`
- **motive:**   aesthetic — applying a convention that disables the gate is not
               conservatism
- **state:**    adopted
- **proposes:** the drift floor is set from the negative arm alone, with the price
               recorded rather than hidden: it detects 37-38 of 40 genuine voice changes
               (92-95%) and misses the rest. The guarantee is "never fails a clean book",
               NOT "always catches real drift". This is a weaker guarantee than the rest of
               the directory's caps and is labelled as such in the source.

### 2026-09-27 — the monotone-arc fixture did not exist and the first rebuild passed
- **row:**      method
- **observed:** `CALIBRATION.md` claimed a synthetic monotone-arc fixture proved the arc
               gate can fail. It was built ad hoc and never kept, so the claim was
               unverifiable. Rebuilt from scratch it **scored 0.566 and PASSED** - a
               fixture built to prove the gate fires, passing. Cause: `curve()` bins at
               200 words, so a monotone decline must be monotone ACROSS A BIN; spreading
               it over 420 sentences moved each bin far less than the bin's own sampling
               noise, and every step changed sign at random.
- **n:**        1 fixture, 2 wrong builds before a correct one
- **evidence:** `calibration/make-arc-fixture.py`, now seeded and checked in
- **motive:**   aesthetic — an unverifiable claim that a gate fires is worse than no claim
- **state:**    adopted
- **proposes:** the fixture is generated by a committed script rather than stored prose,
               seeded so it is byte-identical every run, and the constants that make a bin
               steeper than its own noise are documented at their definition. It now fails
               at 2 windows, which also proves the new `WINDOW_FLOOR` still catches a real
               monotone arc at a window count where the old 0.45 would have been the bar.

### 2026-09-27 — `D1` and `D2` demoted to report-only, on measurement
- **row:**      D1, D2
- **observed:** §12 left one question open: raise the caps to clear published prose, or
               demote the rows. The question is settled by a measurement that had not been
               made — whether the AI control sits above the published distribution at all.
               It does not. This project's own books spell a dash `--`, so **D1 reads
               0.00/1k on all 22 control chapters** against a published chapter maximum of
               33.52/1k. D2's control chapters run p50 4.00, max 5.80, against a published
               median of 3.23 and maximum of 8.40 — the control sits *inside* the human
               distribution, below its 95th percentile. Neither row separates machine
               prose from human prose at any cap.
- **n:**        102 published chapters / 84 novels; 22 AI-control chapters across 2 books
- **evidence:** `tools/prose/calibration/d1d2-decision.py`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** new `REPORT` tier in `deslop-check.sh`. D1 and D2 keep their caps, their
               warn bands and their numbers; they cannot set `fail`. Re-raised caps
               (D1 51/1k, D2 13/1k) were **rejected**, not deferred: they would produce a
               row that passes every book, machine and human alike, and a green result
               read as evidence is worse than no row. Verified: 0 failures across 31
               published chapters, with D1 and D2 still reporting over-cap numbers; the
               slop fixture still FAILS on 16 other rows. Promote back only on a corpus
               where the control and the human distribution actually separate.

### 2026-09-27 — `D3` is in the same position and has not been acted on
- **row:**      D3
- **observed:** the same measurement run covers D3. The control's D3 chapters run max
               16.41/1k against a published chapter maximum of 19.56/1k and a cap of 26 —
               the control is inside the human distribution and the cap clears every
               published chapter. D3 currently fires on nothing in this comparison.
- **n:**        same 102 + 22 chapters
- **evidence:** `tools/prose/calibration/d1d2-decision.py`
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** **nothing, deliberately.** D3 is not demoted, because unlike D1 and D2 it
               causes no false accusation — it fails 0 of 102 published chapters — and
               demoting a rule that harms nobody would be tidying rather than correcting.
               But it is recorded that its value as a *detector* is unproven, and that
               distinction is the actual finding: a cap can be harmless and useless at the
               same time, and only one of those is worth acting on.

### 2026-09-27 — a book path containing a space silently emptied two measurements
- **row:**      method
- **observed:** the scanner prints headers as `== <path>  (<n> words)`. Parsing them with
               `line.split()[1]` yields `../Hollow` for the book "Hollow Bridge",
               because the path contains a space. Every downstream lookup then matched
               nothing, and the tool reported a confident per-book verdict built on one
               file instead of eleven — and on a file that was `ASSUMPTIONS.md`, since the
               scanner also accepts a book directory and reads every .md in it.
- **n:**        2 wrong measurements before caught; 1 control book silently dropped
- **evidence:** `d1d2-decision.py` now takes the path with a regex terminated by the word
               count, and points the scanner at the chapter directory explicitly
- **motive:**   aesthetic — a parser that quietly returns nothing on a file it read is
               worse than one that crashes
- **state:**    adopted
- **proposes:** recorded because this is the second time in this work that a
               whitespace-split assumption met a path with a space in it, and because
               both times the failure was invisible: a plausible number, wrong.

### 2026-09-27 — `A25` raised, not demoted: the deciding test is not the false-failure rate
- **row:**      A25
- **observed:** `A25` also failed published chapters (1.0%) under its 1/2000 cap, and the
               obvious reading was that it belongs with `D1` and `D2` in the report tier.
               That reading is wrong, and the wrongness is the finding. `D1`, `D2` and
               `A25` all false-fail human prose; what separates them is whether the AI
               control sits **above** the human distribution or **inside** it. `A25`'s
               control reaches 3.13/1k against a published chapter maximum of 0.93 — the
               arms separate — so a cap between them exists and should be opened up.
- **n:**        102 published chapters / 84 novels; 22 AI-control chapters
- **evidence:** `tools/prose/calibration/d1d2-decision.py`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** `A25` cap raised 1/2000 -> **3/2000**, which is 1.5x the worst published
               chapter — the one row in this table where the usual headroom convention
               fits. Published failures 1 -> **0 of 102**; 2 of the 3 control chapters that
               exceeded the old cap still do. Warn band moved 1/4000 -> 1/2000 so it sits at
               the published p95 rather than under it. `A25` is now the only A-row in the
               directory with both a zero false-failure rate and a control it can catch.

### 2026-09-27 — two new controls so none of this can be silently undone
- **row:**      method
- **observed:** every decision recorded above — the `D1`/`D2` demotion, the `A25` raise,
               the drift and arc size-dependent floors, the monotone fixture — was a
               one-time measurement. Nothing re-checked them, so a later edit could undo
               any of it and the suite would still pass.
- **n:**        2 controls, 9 total
- **evidence:** `tools/prose/validate-controls.sh` controls 8 and 9
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** control 8 reads the `REPORT` block out of `deslop-check.sh` and fails if any
               id in it ever prints `FAIL`, so re-promoting a demoted row is caught
               automatically and newly added rows are covered without editing the test.
               Control 9 regenerates the monotone-arc fixture and fails if `A1` passes it.
               Both proven to fire by tampering (removing the gate flag from the `REPORT`
               loop makes control 8 fail) rather than assumed.

### 2026-09-27 — the multi-volume corpus was procurable, and controls 4-7 now run
- **row:**      calibration
- **observed:** the binding constraint on this work has been recorded as "a current,
               multi-author, native-English commercial corpus", and controls 4-7 have
               never run. The *current* part is a copyright wall no amount of work climbs.
               The *multi-volume* part was never a procurement problem at all - it is a
               FORMAT requirement, and Project Gutenberg serves the format for free.
               `fetch-multivolume.py` downloads published English fiction, splits it on
               chapter headings, and stages it as `<stem>-vNN__chapter-NN.txt`.
- **n:**        6 volumes, 6 authors, 1813-1897, 303 chapter files (6 of 15 books fetched;
               the rest are wired and unused)
- **evidence:** `tools/prose/calibration/fetch-multivolume.py`; `validate-controls.sh`
               now exits **0** with all nine controls passing
- **motive:**   aesthetic — a control that cannot run is an unverified claim wearing a
               test's clothes, and four of them had never run
- **state:**    adopted
- **proposes:** **Control 4 is the first real validation of `U1`-`U6` against published
               prose.** Pride and Prejudice (61 chapters), Jane Eyre (38) and Tess (60) all
               pass the uniformity gate; the uniform-manuscript control fails on `U1` and
               `U5`; both published volumes hold one voice; and the two-voice control
               fails at 4.53 against the 10-chapter `SIZE_FLOOR` of 1.94 — which validates
               the size-dependent floor on real prose for the first time. The corpus is
               gitignored, so a fresh clone still needs one command to run them; that is
               the existing design, not a regression. **What is NOT solved:** a *current*
               corpus. These books are 1813-97 and this directory's own rejection registry
               already records that era measures the century as much as the prose.

### 2026-09-27 — a stray carriage return made every paragraph a line, and looked like a finding
- **row:**      method
- **observed:** fetching the corpus produced paragraph-length CV of **32%** where the
               existing 140-novel corpus gives 80-223% (median 110). U5's floor is 55%, so
               this read as U5 failing real published prose - a third instance of the unit
               error, and the row had been treated as settled. It was not. Cause: some
               Project Gutenberg files end lines `\r\r\n`, and opening them in TEXT MODE
               applies universal-newline translation, turning the stray `\r` into an extra
               `\n` - a blank line between every hard-wrapped display line. Every wrapped
               line became its own paragraph, the paragraph count tripled, and the metric
               this corpus exists to measure collapsed. The bug was found by asking why a
               316,000-word novel had 28,242 paragraphs.
- **n:**        1 corpus, 6 volumes, all paragraph measurements
- **evidence:** `fetch-multivolume.py` now decodes bytes and normalises `\r\r\n`
               explicitly, asserting no `\r` survives; post-fix CVs are 116-162% across
               three volumes, in line with the existing corpus
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** recorded because the near-miss is the point. A measurement that disagrees
               with a settled finding defaults to "the finding is wrong", and this one
               would have sent a correct 55% floor back for revision on the strength of a
               file handle.

## 2026-09-27 - U1 does not transfer to non-fiction; advisory on a declared nonfiction book

- **Rule:** U1 (chapter-length variance) fails under CV 30%. 140 PD English novels give
  48.4-70.6%, so the floor is safe on fiction. Six published non-fiction volumes (Darwin
  x3, Douglass, Dana, Smith) give 28.2 / 35.7 / 60.4 / 92.5 / 99.4 / 113.7%.
- **Measured:** 1 of 6 fails outright (Darwin, *Journal of Researches*, 28.2%) and 2 more
  warn. Fiction minimum 48.4% vs non-fiction minimum 28.2% - one floor cannot serve both.
- **Cause:** not a unit error. A chapter in a novel runs as long as its scene does; a
  chapter on a species runs as long as the argument does. Different shapes, same measure.
- **Decision:** U1 becomes advisory on a book declaring `positioning: nonfiction`, in the
  existing convention mechanism, alongside U4 and U5. Enforced everywhere else. The
  number is still printed, with the measurement in the row's own output.
- **Rejected:** re-deriving a separate non-fiction floor. n=6 volumes from 5 authors is
  enough to refute a floor, not to set one - the same asymmetry that made Montgomery a
  refuter rather than a calibrator.
- **Evidence:** `calibration/fetch-multivolume.py --nonfiction`; control 10 in
  `tools/prose/validate-controls.sh`, which stages all six volumes and was proven to fire
  by removing the scoping (suite exit 1, naming `darwin-beagle-v01`).
- **Status:** verified. Fiction arms unchanged - control 5 (uniform manuscript) still
  FAILs U1 at CV 0.8%, and control 4 (published fiction) still passes.

## 2026-09-27 - U1's published band came from a light novel; re-derived on English fiction

- **Rule as shipped:** U1 FAIL under 30% chapter-length CV, warn under 45%, quoting
  "published min 48.4%" from a 3-volume corpus (Wandering Witch, Yen Press, a translated
  Japanese light novel; chapters 466-9,184 words inside one volume).
- **Measured:** six published ENGLISH FICTION volumes split on real chapter headings
  (Austen, Bronte x2, Eliot, Hardy, Stoker; 25-86 chapters) give 33.4 / 39.7 / 42.2 / 43.0
  / 43.5 / 45.1%. The worst is 33.4%, not 48.4%. Under the old numbers **five of six
  published novels WARNED** - the gate was warning on the human canon it is calibrated
  against. The 30% floor also gave only **1.11x** headroom against the worst real novel,
  against this project's own 1.5x convention.
- **Ruled out:** sample size. Resampling each book's real chapter lengths to n=17/13/11
  moves CV by at most 4 points (Pride 43.0 -> 38.7), nowhere near the 15-point gap. The
  cause is the register: short interludes in a light novel are not English novel chapters.
- **Decision:** FAIL 30% -> **22%**, warn 45% -> **28%**, both 1.5x-style below the
  measured 33.4% worst case. Detection preserved - Hollow Bridge still FAILs at
  13.7% CV, and the uniform-manuscript control still FAILs at 0.8%.
- **Consequence:** the 140-novel PD corpus cannot have produced 48.4%; that number came
  from the 3-volume light-novel corpus, and any CV band quoted as "the human range" in
  this project should be checked for which corpus produced it.
- **Evidence:** staged via `fetch-multivolume.py`; control 4 (published fiction passes
  uniformity) now covers six volumes and all six read `ok` with no warnings.

## 2026-09-27 - drift's Spearman manufactured a perfect trend from a constant feature

- **Rule as shipped:** `check-drift.py`'s D2 reports the largest monotonic trend across
  the chapter order, warning above rho 0.75.
- **Measured:** on a book with no quoted speech in any chapter, it reported dialogue share
  at **rho +1.00** across eleven chapters - a perfect correlation for a feature measured
  at 0.000% in every one of them. The word "dialogue" appears zero times.
- **Cause:** two defects in `trend_of()`. Ties were given sequential ranks, so sorting a
  constant series yields 1,2,3..n - a perfect ramp that correlates perfectly with position
  BY CONSTRUCTION. And a zero-variance series was never rejected, so the one case where no
  trend exists is the case that reported the strongest one.
- **Fix:** ties take the average of the ranks they span (which is what Spearman means),
  and a series with no variance returns 0.0. Verified on synthetic input: constant -> 0.000,
  true ramp -> 1.000, reversed ramp -> 1.000, alternating ties -> 0.000.
- **Why it matters more than the row:** a gate that reports maximum confidence about a
  feature it never measured is worse than a gate that reports nothing. This is the same
  shape as the `chapter-rates.py` header bug and the spaced-path bug: the failure mode
  here is always a confident number derived from nothing.
- **Evidence:** re-run on the same book now reports `sent_sd` rho +0.90 and `fw_it` +0.81,
  both real. See `sons-of-heaven-v2/RUN_REPORT.md`.
- **Status:** verified. All ten controls still pass; control 7 (a book that changes voice
  must FAIL) still fails at 4.53 against the 10-chapter floor of 1.94.

## 2026-09-27 - a gate's own defect found by a book, not by a corpus

- **Rule affected:** `check-drift.py`'s `trend_of()`. Two defects: tied values were given
  sequential ranks, and a zero-variance series was never rejected.
- **Measured:** on a book with no quoted speech in any of eleven chapters, the tool reported
  dialogue share at **rho +1.00** - a perfect trend for a feature measured at 0.000% in
  every chapter. The word "dialogue" appears zero times in the manuscript.
- **Why this entry is about the corpus, not the gate.** 6 published fiction volumes (303
  chapter files) and 6 non-fiction volumes (143 files) did not produce this input. Every
  published book has *some* dialogue, so a zero-variance feature never arises. The only
  corpus that produces the degenerate case is a book that **this pipeline wrote**, because
  the pipeline has never produced a book with quoted speech and nobody had noticed until
  one existed.
- **Conclusion added to the system:** a calibration corpus made of other people's books
  cannot cover the input space of a generator's own output. Human prose varies in every
  feature because humans use every feature. Generated prose does not, and the features it
  skips are precisely the ones no human corpus will ever exercise.
- **Status:** fixed, verified on synthetic input, ten controls still pass.
- **First entry of its kind.** The previous three entries this date were all found by
  analysing corpora. This one was found by running the system, which is the only method
  that produces degenerate inputs on demand.

## 2026-09-27 - a tic caught twice, and what that says about additive revision

- **Observed:** the antithesis construction ("X is not Y. It is Z") was caught by `U6` at
  91% of chapters on the first full draft, revised down to 18%, then **reintroduced by the
  expansion pass** - 15 instances in chapter 1 alone - and caught again by `A25` at
  2.04/1k. Final: 0.00-0.75/1k across all eleven chapters.
- **Not recorded anywhere in the system before this entry:** that revising a draft by
  *subtraction* and by *addition* are different operations with different failure rates.
  Cutting a tic removes it. Adding material to a chapter reintroduces every tic the author
  reaches for while writing new prose, because the tic is load-bearing for how the author
  makes a correction land.
- **Practical consequence:** a gate cleared once is not evidence the habit is gone. Any pass
  that ADDS text to a manuscript re-runs every construction row, and an author who has been
  caught once should expect to be caught again after expanding.
- **Evidence:** `sons-of-heaven-v2/RUN_REPORT.md`, first-draft and post-expansion gate
  tables. Both failures are recorded there with the counts.

## 2026-09-27 - "vary your chapters" plus no word floor is a licence to delete

- **Observed:** `sons-of-heaven-v2` reached a chapter-length CV of 30.3% and passed `U1`
  at 17,872 words against a 28,000-32,000 target. Two expansion passes closed the gap by
  38% and 22%, both short.
- **The mechanism, located in the skills rather than assumed.** Five instructions across
  the skill set tell a drafting pass to vary chapter length or "break the book's uniform
  shape" (`composing` step 6, `quoin` op 9, `deslopify`, `incunabula` gate description,
  `phases.md`). The explicit remedy given for a uniformity failure is "fixed by varying
  chapter length" - a *length* remedy, with nothing requiring length to be *added*.
  Against that, the only word-count target in the pipeline is
  `incunabula-codex/references/intake-schema.md: target_range_words: [0, 0]` - a default of
  zero - and one intake prompt asking for the figure. There is no per-chapter minimum
  anywhere in the skill set.
- **The perverse incentive, measured.** `U1` is a CV, so it is scale-invariant: truncating
  every chapter proportionally leaves it unchanged. But *disproportionate* cutting improves
  it. On this book, cutting the two longest chapters by 40% removes 1,892 words and takes
  CV from 30.3% to 22.5% - still passing the 22% floor. **The cheapest way to satisfy the
  one chapter-shape row the system enforces is to delete prose from the long chapters.**
- **Consequence for the theory.** The finding "chapters vary like human prose" is
  *correct* and it is also, on its own, satisfiable by making the book worse. A
  distributional rule with no floor beneath it constrains the shape of a book without
  constraining its size, and the cheapest way to move any variance measure is to shrink the
  tail. This is the same Goodhart shape as the prohibition-brief finding, arrived at from
  inside our own system.
- **Not the whole cause, stated honestly.** The dominant cause was that the drafting pass
  missed a target it had itself written: the architecture specified 2,000-3,600 words per
  chapter and delivered a 944-1,350 range (38% of the band mean); the corrected targets of
  1,400-4,500 produced 874-2,725 (56% of the band mean). Two different bands, the same
  systematic ~half-length outcome. A target written in a planning document has no
  enforcement point, and no row in the directory reads `target_range_words`.
- **Fix, applied.** `tools/prose/check-length.py` (row `L1`). It reads the book's own
  declared range and compares. Deliberately **not** another corpus measurement: it makes no
  claim about human prose, so there is no population it can false-fail, which is why it can
  be enforced on exactly the books whose convention declaration switched `U1` off. That
  blindness is where a book half its intended length went unnoticed.
  - Enforced when the book declares `target_floor_words` + `target_ceiling_words`.
  - **Advisory** when it declares only a single `word_count_target`, because failing a
    single figure means inventing a tolerance, and this project does not set a threshold
    from an unmeasured number. It says so on the run.
  - Exit 2 when nothing is declared. Not run, never pass.
  - Control 11 in `validate-controls.sh` proves both directions: a book delivering 64% of
    its declared range FAILs, and a book inside its range passes.
- **A note on how this entry was written, because it is the same failure twice.** The
  first version of this entry ended "it is a decision about the pipeline's shape and is left
  to a person" - routing the fix to a human while I had already located it. The finding was
  correct, the hedge was the weasel, and the only reason it was visible is that this file
  requires a stated state for every claim, so "state: not fixed, deferred to a person" had
  to be written down rather than assumed. The entry has been corrected rather than appended,
  because a stale entry is worse than a missing one.

## 2026-09-27 - pointing deslop-check.sh at a book directory fails the book's own planning docs

- **Observed:** `bash tools/prose/deslop-check.sh <book>/` reports FAIL on
  `RUN_REPORT.md`, `foundation.md` and `voice-matrix.md` — on rows including `A4`
  serves-as, `A1a` delve, `A3a` grandiose nouns and `A20` unicode arrows — and prints
  "fix the rows above before this chapter counts as drafted", for files that are not
  chapters. The same book pointed at `<book>/manuscript/chapters` PASSES.
- **Not a new defect, but an unpriced one.** The pipeline already states the rule
  (`phases.md`, prose gate rule 4: "Manuscript prose only — outlines, scene packets, and
  state documents are written to be exact, and their register deliberately sits above the
  prose ceilings"), and `CALIBRATION.md` §5 records that the project's own engineering
  documents fail this scan and are exempt. So the exemption is documented and the tool
  does not implement it. Pointing the scanner at a book is the *natural* command and it
  returns a confident, wrong verdict with a remediation line addressed to a file that
  cannot be fixed.
- **Cost:** a planning document is held to a prose cap, and a human debugging the failure
  edits their own run report trying to make it read like fiction. The obvious workaround
  — exempting the filenames — is wrong, because a chapter could legitimately be called
  `foundation.md`.
- **Fix, deliberately NOT a filename blocklist.** The correct guard is that the tool
  should say which files it treated as prose, and should not print a prose remediation
  line for a file it cannot identify as a chapter. Left unimplemented and recorded here,
  because it changes the scanner's contract and `PRINTERS_COPY.md` §7 reserves that.
- **Interim rule, now in `tools/prose/README.md`:** always pass the chapters directory.

### 2026-09-27 — a tool defect has no motive, and the vocabulary has no slot for it
- **row:**      delegation — `check-errata.py`
- **observed:** Two `validate-controls.sh` defects were written up here and the gate
               rejected both: `motive` is a closed vocabulary of exactly
               `('aesthetic', 'privacy')`. Both are *author-facing* motives — what a
               threshold costs the person writing. Neither defect has such a motive,
               because neither makes any claim about how to write: one is a stale
               default path, the other is corpus runtime.
- **n:**        1 harness, 1 session, 2 rejections
- **evidence:** `python tools/prose/check-errata.py` →
               `FAIL ERRATA 2026-09-27: motive is 'measurement', must be one of
               ('aesthetic', 'privacy')`, twice.
- **motive:**   aesthetic — and this is the honest reading, not a workaround. The
               vocabulary is doing its job: ERRATA is the channel by which a claim
               about *writing* becomes a rule, so a claim with no author-facing cost
               has no business in it. Forcing `aesthetic` onto a stale path bug would
               launder a tooling defect into a claim about craft, which is the same
               failure shape as re-deriving a threshold from six liked books. Widening
               the vocabulary to admit `tooling` is the real fix and is a §7 decision,
               because `check-errata.py` is frozen.
- **state:**    observed
- **proposes:** none, and deliberately not applied. The two `validate-controls.sh`
               defects were moved to `tools/prose/README.md`, which already carries the
               interim operational rule for the sibling directory-scanning defect. If a
               person widens `motive` to admit a non-author-facing value, they should
               require a `row: delegation` entry to carry a *different* mandatory field
               — because "no motive" and "an aesthetic motive" are not the same
               absence, and the gate currently cannot tell them apart.

### 2026-09-27 — two of six comp titles did not exist, and the pipeline's Phase 1 debt was the only reason anyone checked
- **row:**      delegation — `scout` / `intake-schema.md`
- **observed:** Book 2 (`a-matter-of-record`) entered Phase 2 with a six-title comp set
               sourced entirely from orchestrator recall, each carrying a
               `confidence:` field. Phase 1 (`/scout`) ran and verified them:

               | recalled | verdict |
               |---|---|
               | Yarbrough, *The Bureau of Missing Persons* (2017) | **does not exist** |
               | Davies, *The Dying Light* (Devils and Dusters III) | **does not exist** |
               | Tudor, *The Burning Girls* (2018) | real, 2021, genre misdescribed |
               | Doughty, *Apple Tree Yard* (2016) | real, 2013 |
               | Griffiths, *The Dark Angel* (2016) | real, verified |
               | Banville, *The Untouchable* (1997) | real, verified |

               Two fabrications, three wrong years, one wrong genre. The Yarbrough
               entry was marked "closest comp, confidence: high" — it was the least
               real thing in the set. The Davies entry invented both a title and a
               series name; "Devils and Dusters" returns zero results anywhere.

               Searching for a *real* comparable in the same slot then immediately
               produced one that the recall had missed entirely: Tom Baragwanath,
               *Paper Cage* (Knopf 2024) — a police-station **records clerk** as
               protagonist in a small town, Ngaio Marsh Award finalist and 2025 Barry
               Award nominee. The book's entire load-bearing commercial assumption
               (`A3`, the claimed market gap) was false, and the book that falsified it
               was one search away from where the fabricated title had been sitting.
- **n:**         6 recalled comps, 2 nonexistent, 3 with wrong metadata
- **evidence:**  `a-matter-of-record/research/market-research.md` §1, §2;
               Wikipedia "Peter Ho Davies" complete novel list; Kirkus/Irish Times
               (Banville 1997); Quercus/Houghton (Griffiths 2016); Knopf
               (Baragwanath *Paper Cage*).
- **motive:**    aesthetic
- **state:**     observed
- **proposes:** The `confidence:` field on recalled comp titles is actively harmful
               and should be deleted from `intake-schema.md`, not merely flagged
               unverified. A number on an unverified recall is worse than no number:
               it converts "nobody checked" into "someone checked and rated it high,"
               and the one entry the project itself was most confident about was the
               one that did not exist. Comp titles arriving from a language model
               should carry no confidence value at all, and the field should not exist
               to be filled. Recording this as `motive: aesthetic` because the
               author's own time is what the false confidence cost — a book built on a
               fabricated comp is a book built on nothing.

### 2026-09-27 — a claimed market gap survived into Phase 2 with zero evidence, and the market had moved
- **row:**      delegation — `scout` / `ASSUMPTIONS.md`
- **observed:** Book 2 declared `A3` as its load-bearing commercial assumption: *"mysteries
               where the filing system is the crime scene rather than the backdrop is
               a gap."* `ASSUMPTIONS.md` labelled it **"This is a guess... it has zero
               evidence behind it right now"** — and the book was nonetheless taken
               through Phase 2 (foundation, canon ledger, 30-chapter outline, clue
               ledger) on the strength of it. Phase 1 ran afterwards, in book 2 rather
               than book 1, and returned:

               - **The protagonist slot is occupied.** Baragwanath, *Paper Cage* —
                 police-station records clerk, small town, buried institutional wrong.
                 Knopf, Ngaio Marsh finalist, 2025 Barry Award nominee.
               - **The quiet middle of the market does not exist.** The CrimeReads
                 2025 best-of 20 contains no quiet documentary procedural at all, and
                 trade reporting (Murder & Mayhem, 2025-12-30) describes a
                 *bifurcation* between escape-reading and dark-reading rather than a
                 market with a middle. The small-town books that place are quiet in
                 setting and propulsive in structure.
               - **Both comparable comps without series momentum were received
                 disappointingly** — *The Burning Girls* ("at the 80% mark") and
                 *Apple Tree Yard* (3.5/5, "ripping beach-read").

               A guess that happened to be marked as a guess is still a guess, and
               three phases of architecture were built on it before anyone looked.
- **n:**         1 load-bearing assumption, 2 of 3 legs falsified, 3 phases of work
               built on it unverified
- **evidence:**  `a-matter-of-record/research/market-research.md` §2, §3, §5, §6;
               Knopf (Baragwanath); CrimeReads 2025 best-of; Murder & Mayhem
               2025-12-30; Goodreads/Amazon sentiment on Tudor 2021 and Doughty 2013.
- **motive:**    aesthetic
- **state:**     observed
- **proposes:** `ASSUMPTIONS.md` already asks the right question — *if /scout finds
               that A3 is false, the correct response is to change the premise, not to
               write it anyway* — and that instruction was written and then not
               followed, because the ordering put Phase 2 before Phase 1. The fix is
               ordering, not more documentation: **an assumption that is named as
               load-bearing must be tested in the same phase it is created.** On
               fiction, Phase 0 already forces the length contract; the same forcing
               function should apply to the commercial claim, because the length
               contract is enforced by `check-length.py` returning non-zero and this
               one is enforced by nothing at all. A hypothesis that can only be tested
               by a later phase should not be load-bearing in an earlier one.

### 2026-09-28 — a cast name shipped in two books, and the suite had never opened a second book
- **row:**      delegation — `check-names.py`
- **observed:** The coroner in `the-origin-point` was `Priya Raghunathan`; `Hollow Bridge` already had a co-lead also named `Priya`, and a reader persona in
               `incunabula-test` was also Priya. The author caught it. No gate did, and
               none could have: `check-uniformity` reads chapter-to-chapter inside one
               book, `check-drift` reads prose shape, `check-arc` reads structure,
               `check-errata` reads no manuscript. **Not one had ever opened a second
               book.** A name is the only part of a cast that crosses a book boundary,
               and a returning reader is the only reader positioned to notice — so the
               one defect class catchable by memory had no instrument at all.
- **n:**        7-person cast, 2 books, 3 projects
- **evidence:** `grep -ril priya "D:/KDP Books"` → Hollow Bridge
               (`artifacts/03-characters.md`, `ENTITY_STATE.yaml`, `voice-dna.md`),
               `incunabula-test/readership.md`, `the-origin-point` (5 files);
               `grep -rn "name" tools/prose/*.py tools/prose/*.sh` → every hit is a
               filename or `os.path` variable, none reads a character name.
- **motive:**   aesthetic — a returning reader meets the same first name in two books
               by one author and learns something false about the books, and the fix
               (rename a character in a finished chapter) costs the author a rewrite
               they did not ask for. This is the most direct author-facing cost in the
               suite.
- **state:**    observed
- **proposes:** `check-names.py` (Freeze 4). `FIRST`/`EXACT` on a character FAIL; a
               shared surname WARNs, because a shared surname is sometimes deliberate.
               Reader personas are explicitly not cast, or a calibration document could
               fail a manuscript. Verified on a negative control (old name restored →
               exit 1, naming Hollow Bridge).

### 2026-09-28 — the corpus could not measure model-default names, and the first attempt measured the period
- **row:**      delegation — `check-names.py`
- **observed:** The claim behind a default-name filter is that models converge on
               familiar names. Measured across all four AI books (72 files, 213,772
               words) for names appearing in 3+ independently-generated books: **one
               token** (`In`). Cross-book convergence on given names is essentially
               zero. And the 1813–1905 prose corpus cannot supply the denominator —
               over 303 files / 945,924 words its most frequent first tokens are `Miss`
               (802), `Sir` (326), `Lady` (165), `Mrs` (116), `Mr` (69), because
               nineteenth-century fiction names characters behind honorifics.
               `Elizabeth` appears **twice**; `Roy` and `Ruth` appear **zero times in
               946k words.** A threshold from that corpus would not measure model
               defaults, it would measure that pre-1900 prose does not often write
               names in the two-word capitalised form this filter reads.
- **n:**        2 corpora, 1,159,696 words, 1 broken measurement
- **evidence:** first measurement returned `human hits = 0` for all 132 names while
               simultaneously reporting 481 distinct human firsts — a contradiction
               that located the bug in the harvester (the corpora are hard-wrapped at
               different widths, Austen ~50 chars and the AI books ~80, so a two-word
               pattern never matched across a newline); fixed by normalising
               whitespace. The corrected run then produced the honorific distribution
               above. Convergence test: `/tmp/converge.py` over the four books.
- **motive:**   aesthetic — a wrong denominator makes the filter refuse names for the
               wrong reason, and the author pays by renaming correct names.
- **state:**    observed
- **proposes:** the denominator is real-world name frequency, not prose: SSA national
               top 20 (FAIL) and Nameberry top 100 girls + 100 boys (WARN), frozen as
               `calibration/NAME_FREQUENCY.tsv` with provenance in
               `calibration/NAME_FREQUENCY.md`. **Tier B is deliberately not a
               failure** — `Cora` is Nameberry #28 and is also the correct name for a
               woman born in 1951 in a rural American county; popularity measures what
               a name is *now*, and a cast is mostly people named long before now. What
               makes a popular name a tell is anachronism, which a gate cannot judge.
               `A stylometric finding about period prose measures the period` — the U1
               lesson, in a new place. The author's own standard that names should
               carry meaning is **explicitly not encoded as a gate**: a rule enforcing
               it could not produce a plain name for a character who needs one, and
               would convert a preference into a rule generating a different preference
               in disguise.

---

## 2026-09-28 — U1 cannot see a distribution that was designed

**Bucket: instrument limit. This is not work to do on any manuscript.**

`check-uniformity.py` row `U1` measures the coefficient of variation of chapter lengths and
compares it to a band derived from six published English fiction volumes (33.4–45.1%).

It cannot distinguish two books that score the same number:

- one whose chapters differ because they contain different things, and
- one whose chapters differ because a plan assigned them to two length buckets.

A bimodal design — 17 chapters at 3,150–4,220 and 17 at 1,760–2,000 — produces two tight
clusters whose *combined* CV is 33.7%, inside the band, while each cluster is internally
uniform. This was built deliberately, in `demo-magician`, and it is the only way found so
far to move a manuscript across U1 without a gate being wrong.

Measured, same instrument, same day:

    Merope 1   478 – 2,304   4.8x   CV 40.9%   no length targets
    Merope 2   519 – 2,406   4.6x   CV 40.0%   no length targets
    The Trick 1460 – 3,442   2.4x   CV 23.7%   length targets applied

**The targets subtracted variance.** 24 of 34 chapters in the targeted book fall inside a
1,004-word band, with adjacent gaps of 5 and 8 words. The two untargeted books produce a
range of nearly five to one.

The row is not wrong and the corpus is not wrong. The row is answering a narrower question
than the one that matters, and it is answering it correctly. Recorded so that nobody
optimises against it a second time, and so that a future U1 revision knows what it has to
see that it currently does not: **not the spread, but the number of distinct modes.**

*Author's note, same session, and the reason this is in the file at all: the U1 target was
raised from a real corpus and it was spent, over a long drafting run, as a thing to write
to. It took two completed books to see it, and the author saw it, not the instrument.*
## 2026-09-29 — the archive held the previous version of the framework, unindexed for two months

**Bucket: process. Nothing was measured; nothing was wrong.**

`_archive/` was 574 files and 56 MB with no index, and the working assumption was that it
held old manuscripts. It did not. `_archive/hollow-bridge/book-genesis-v4/` is a complete
checkout of **Book Genesis V4 — the direct ancestor of this framework** — with its own
git history (last commit 2026-07-29), 19 skills, and 5 more under `deprecated/` and 5
under `optional/`.

All 20 live skills have a direct ancestor there, and the mapping is clean:

| archived (v4) | live (incunabula) | | archived (v4) | live (incunabula) |
|---|---|---|---|---|
| `book-genesis` | `incunabula` | | `book-editor` | `corrector` |
| `book-genesis-codex` | `incunabula-codex` | | `literary-agent-panel` | `agent-panel` |
| `book-genesis-full` | `incunabula-auto` | | `book-swarm-panel` | `reader-swarm` |
| `book-bestseller-studio` | `bestseller-studio` | | `production-prep` | `presswork` |
| `book-researcher` | `scout` | | `editorial-package` | `colophon` |
| `narrative-foundation` | `forme` | | `series-architect` | `series-binder` |
| `prose-craft` | `setting` | | `manuscript-manager` | `press-ledger` |
| `beta-reader` | `proof-panel` | | | |

Five were promoted out of `optional/` rather than dropped: `entity-tracker` →
`case-keeper`, `continuity-guardian` → `collator`, `reader-persona` → `readership`,
`voice-fingerprint` → `voice-matrix`, `book-auto` → `incunabula-auto`. The five under
`deprecated/` have no successor and are mentioned nowhere in the live tree.

**This is the sixth instance of the same failure.** `KNOWN_FINDINGS.md` records it: the
instrument was honest and the gap was filled with the more dramatic story. Here the
dramatic story is "a graveyard of old manuscripts", and the true story is "the last
version of the tool, which is the one thing worth reading when a design question comes
up." Both are consistent with `ls`, and only one is true.

**The fix is the cheaper kind, again.** Not a detector — there was nothing to detect; the
files were fine and nothing was checking them. A file: `_archive/README.md`, plus two
rules that make the next occurrence cheap. `skills/rewrite/SKILL.md` gains a step 2,
*read the archive before you decide what needs rewriting*, because that is the moment
the prior version is still reachable. `maintenance-protocol.md` §7 requires a new archive
subdirectory to be indexed in the same commit that creates it.

**Second, smaller finding in the same directory:** `reference-reading/` is 88 scanned
pages from published books, and it sits beside the calibration corpus where a future
reader could reasonably assume it belongs. It is not corpus, must not become corpus, and
the index says so — those are copyrighted images; the corpus is native-English
commercial prose in text form and exists to be measured.

**Also noted, not acted on:** `validation-series/` carries seven untracked scratch scripts
(`_a25_audit.py`, `_diff.py`, `_dist.py`, `_find.py`, `_locate.py`,
`_normalize_eol.py`, `_whichfail.py`) from the 2026-09-28 session. Five are referenced by
nothing at all. Left in place pending a decision on whether the session's verification
code has any future value.
## 2026-09-29 — three copies of the framework, and a draft would have used the wrong one

**Bucket: process. No manuscript was affected yet, which is the only reason this is cheap.**

A skill dispatch reads the *installed* copy. There were three copies of the Incunabula
skill set on this machine and no defined winner:

| location | what it was | state found |
|---|---|---|
| `incunabula/skills/` | the repo, 29 skills | current |
| `~/.agents/skills/` | installed | drifted, 10,693 lines |
| `~/.claude/skills/` | installed | the pre-rename v4 names |

`~/.claude/skills/` held `book-genesis`, `book-editor`, `manuscript-manager`,
`narrative-foundation`, `prose-craft` and fifteen more — the versions that predate the
freeze, `DRAFTING_FRAMEWORK.md`, and the archival rules, with no `maintenance-protocol.md`
at all. The installed `incunabula-codex` was a snapshot from before §7a was written; it
references `GATE_FREEZE`, `DRAFTING_FRAMEWORK` and `ERRATA` in **zero** files where the
repo references them in one or two.

**The consequence, stated plainly: a book drafted from scratch would have been drafted
against a specification no document in the repo describes, and every measurement taken
from it would have been meaningless while looking completely normal.** Nothing would
have failed. The uniformity check would have returned a CV, the deslop check would have
returned a pass, and both would have been attached to a spec that was not the one being
documented.

This is the seventh instance of the same failure. KF-004 (key names) and KF-005 (the
CR-blind grep) were fixed in the detector. Freeze 8 (missing vs declared) and Freeze 9
(corpus present vs absent) were fixed by making a gate name its own state. This one is
fixed by naming the winner and making the copies checkable against it.

**Resolved.** `incunabula/skills/` is the authoritative copy. `tools/sync-skills.py`
syncs it to both home directories and quarantines the 20 superseded v4 names — moved,
not deleted, each with a `_SUPERSEDED_BY` provenance file — and `--check` verifies
byte-equality. `tools/SKILLS.md` states the rule. Full pre-change copy of both
directories at `~/_skills-backup-20260929/`; quarantined skills at
`~/_skills-quarantine-20260929/`. Third-party skills (`mantis-*`, `ponytail*`, `watch`,
`workctl`, `orca-cli`, `computer-use`, `find-skills`, `gauntlet-loop`,
`antigravity-protocol`, `aso-appstore-screenshots`, `source-command-seed-*`) are excluded
by prefix and verified untouched.

Not a sixteenth row in `GATE_FREEZE.md`, and the reasoning is recorded there: it measures
which copy of the tool will run, not anything about a manuscript, and freezing a check
about the freeze mechanism would mean the next session to touch any gate had to
re-record it.

**A related count correction.** Earlier today I described the repo as holding 27 skills.
It holds 29. The listing I counted from predated `deslopify` and `rewrite`. The sync
reports 29, and both destinations now hold 29.
## 2026-09-29 — the first from-scratch book failed U1, and the framework's explanation of variance is not the right one

**Bucket: instrument premise. This is the most consequential entry in this file.**

`DRAFTING_FRAMEWORK.md` justifies removing per-chapter targets with this:

> "The variance came from the places nobody had decided in advance."

Evidence until today was three books — Merope 1 at CV 40.9%, Merope 2 at 40.0%, and
`incunabula-test` at 45.2% — **all three of which were re-chaptered after the fact**. Two
books re-derived post hoc cannot show that drafting under a rule produces the result the
rule claims. That gap was stated openly in `REWRITE.md` and in step 9 of
`skills/rewrite/SKILL.md`, and `muzzle-and-marrow` exists to close it.

It closes it in the other direction. Ten chapters, drafted from scratch, **no per-chapter
target, floor, ceiling or planned distribution anywhere in the project**:

    n         10
    total     16,686
    range     1.53x  (1,322 - 2,029)
    CV        12.1%

`check-uniformity.py` **exit 1**, U1 FAIL against a published band of 33.4-45.1% and a
failure line of 22%. It is the most uniform book in the project — the three books that
justified the framework scored 23.7%, 40.0% and 40.9%. `check-length.py` also exits 1 at
16,686 against a declared 22,000 floor.

**So the stated mechanism is falsified: removing the numbers did not produce the spread.**
The spread in the two Merope books came from something other than target-absence, and the
document's explanation of it is wrong.

The likely mechanism, offered as a hypothesis and not a finding: mean sentence length
climbs monotonically across the manuscript (16.4, 19.0, 18.9, 24.4, 22.4, 24.6, 20.8,
23.1, 26.6, 25.0) while chapter lengths do not follow it. The prose gets more expansive
and the chapters stay the same size, because each chapter was written to finish a question
of roughly the same size, and a writer who knows the shape of a chapter before sitting
down produces a uniform book even with no numbers in the document. Variance may come from
chapters written *into* — chapters that find out what they are.

**One book is not a distributional claim.** This is recorded as falsifying the
*explanation*, not the framework, and the band has not been touched and no chapter was
trimmed to chase the number. That is the failure this file exists to prevent.

What the pilot does establish, and this is the first from-scratch result of its kind:
the **prose gate passes with no repairs at all** — A25 at 0.00/1k across 16,686 words,
against 30 hand repairs needed in `incunabula-test` — and **drift holds** at exit 0.

Also recorded, and it is a different class of finding: probed the frozen
`check-names.py` against this book's pet-name convention before drafting, and a title
lands in the first-name slot while several names are dropped entirely as single bare
parts. A cast named "Duke Rocky of Cavalton" would have been **largely invisible** to the
gate — a pass on a book never looked at, which is Freeze 8 and Freeze 9's defect class.
Fixed by declaring each character twice in `ENTITY_STATE.yaml` (`canonical_name:` for the
parser, `called_in_prose:` for the reader). **The frozen gate was not modified and no
manuscript text was bent to satisfy a parser.**

Full write-up: `D:/KDP Books/muzzle-and-marrow/PILOT.md`.

---

## 2026-09-29 — the 40% evidence was a filing artifact, and the mechanism is now known

**Bucket: framework evidence falsified. The band is untouched. No manuscript is affected.**

The two entries above both rest on the same three-book table. Two of its three rows are now
explained, and the explanation removes the support.

**The recovery.** `_archive/validation-series-meta/` holds Merope v1 as it was actually
drafted: seven chapters, recovered from the v1 EPUBs and verified byte-identical by
rebuild. The live `validation-series/` books are v2: eleven chapters. The v2 chapter files
**overwrote v1 in place**, which is why the manuscript was lost from the archive and had to
be pulled back out of the build artefacts.

**What v2 actually is.** Measured against v1, per chapter, same instrument:

| | book 1 | book 2 |
|---|---|---|
| v2 chapters opening with prose verbatim in v1 | 10 of 11 | 11 of 11 |
| v2 chapter words matched to their v1 parent | 97.1–99.9% | 97.9–99.7% |
| total words, v1 → v2 | 15,439 → 15,377 (**−0.4%**) | 15,057 → 14,962 (**−0.6%**) |

The v2 books are **not re-drafts**. They are the v1 prose re-partitioned. Nothing was written
and nothing was cut away — the totals hold to within half a percent. The disposition is
plain: some v1 chapters were left whole, others were split in two.

| | left whole | split | gap between group means |
|---|---|---|---|
| book 1 | 2,077 / 2,304 | 475, 769, 776, 1,112, 1,222, 1,273, 1,617, 1,688 | 2,190w vs 1,116w |
| book 2 | 851, 1,865, 2,161, 2,393 | 519, 972, 1,012, 1,203, 1,266, 1,342 | 1,818w vs 1,052w |

A 40.9% CV is the arithmetic signature of *some chapters halved and some not*. It is a
property of the cut pattern, not of any drafting decision.

**The reproduction.** Take the v1 prose. Cut it into the v2 chapter sizes. Write nothing.

    book 1   v2 actual CV 41.0%   reproduced from v1 prose alone  41.0%
    book 2   v2 actual CV 39.9%   reproduced from v1 prose alone  39.9%

To the decimal, with zero words authored. The framework's two load-bearing figures are
fully accounted for by a partitioning operation performed on a manuscript that had already
been written to explicit targets.

**The targets were there all along.** v1's own outline declares the target the framework
says was absent:

    **Target:** 7 chapters × ~2,450 words ≈ 17,150 words (60 formatted pages).

and carries `~2,450` in the heading of all seven chapters, with
`average_words_per_chapter_planned: 2450` in `PROJECT_STATE.yaml`. The v1 books score
**CV 5.8% and 10.9%** — the most uniform books in the project, drafted to numbers. The
table row reading `Merope 1 … no` is wrong about the book it names. It is reporting the
provenance of the *file* (re-partitioned, untargeted) and calling it the provenance of the
*drafting*.

So the correlation the framework drew is an artifact of a file overwrite. The one book in
the table whose targeting is real — The Trick, `demo-magician`, 34 chapters, CV 23.7% — is
the one that actually had targets. Merope had targets too, and scored lower.

**What the numbers now say.** Across every book measured:

| book | targeting | CV | note |
|---|---|---|---|
| Merope v1 (7ch) | **yes**, 2,450 × 7 | **5.8%** | the drafting, archived |
| Merope v1 (7ch) | **yes**, 2,450 × 7 | **10.9%** | the drafting, archived |
| Merope v2 (11ch) | n/a | 41.0% | same prose, re-partitioned |
| Merope v2 (11ch) | n/a | 39.9% | same prose, re-partitioned |
| The Trick (34ch) | yes | 23.7% | targeting real |
| pilot (10ch) | no | 12.1% | genuine from-scratch, no targets |

Targets are associated with the **lowest** variance in the corpus, not the highest. The
pilot — genuinely unconstrained, and the only book drafted from scratch under the current
framework — sits at 12.1%, far below the 33.4–45.1% band. **The claim that removing targets
produces band-level variance is not supported by any book in this project.** The books
that scored in the band got there by being cut.

**Why this was never caught.** The v2 overwrite changed the chapter files without changing
the project's identity, so every later measurement re-read the re-partitioned file and
attributed its shape to the drafting that preceded it. This is the ninth instance of the
recurring failure — instrument honest, gap filled with the more dramatic story — and the
first where the gap was *filled by a real measurement of the wrong artifact*. Earlier eight:
KF-004, KF-005, Freeze 8, Freeze 9, deletion-layer escalation, archive-as-graveyard,
three-copies, the from-scratch U1 failure.

The cheaper fix applies again: **name the state, don't build a detector.** A provenance line
in `PROJECT_STATE.yaml` recording that a chapter file is a re-partition of an earlier
division would have carried the fact forward. No new gate is warranted, and none is added —
Freeze 6 holds, and the instrument is untouched.

**What survives.** The published band, the corpus behind it, and `U1` itself are
unaffected: they were never derived from these three books. The *rule* — do not put length
numbers in a drafting document — is not touched by this either. What is withdrawn is the
evidence offered for it. A rule that cannot cite its evidence should be re-derived, not
defended, and the honest position is that **this project has never demonstrated that a book
drafted without length targets lands in the band.** The pilot says the opposite.

It also revises yesterday's entry. The pilot's monotone mean-sentence climb was read as
evidence that a writer who knows a chapter's shape produces a uniform book. That remains
true, but it is no longer the only explanation available, and it is no longer needed to
explain a failure — the band was never reached by drafting here, so the pilot's 12.1% is
the expected result of the method actually in use, not an anomaly in it.

Reproduce with `check-uniformity.py` against
`_archive/validation-series-meta/book-{1,2}/manuscript/chapters/` and
`validation-series/book-{1,2}/manuscript/chapters/`. The recovery is documented in
`_archive/validation-series-meta/V1-MANUSCRIPT-RECOVERY.md`.

**Files touched, and what was deliberately not.** Four documents corrected: this file,
`DRAFTING_FRAMEWORK.md` (table marked withdrawn, the 478-word stub example struck),
`skills/rewrite/SKILL.md` (the two `had targets: no` rows), and
`tools/prose/calibration/CALIBRATION.md` (the re-chaptering table, which is where the
error entered — it already said "after the manuscripts were re-chaptered" and did not
carry that forward).

`CALIBRATION.md` is listed among the frozen files in `GATE_FREEZE.md`. It is corrected
here rather than left standing because it is the origin of the claim, and a frozen
document that carries a known-false statement is worse than an edited one. **It carries no
hash** — the freeze manifest covers the twelve gate files and `verify-freeze.sh` verifies
those, not this — so no freeze row is added and no threshold is touched. Freeze 6 holds:
this is documentation, not an instrument change. The band still derives from *Tess of the
d'Urbervilles* (33.4%) and *Wuthering Heights* (45.1%), both published volumes, neither
one of them ours.
---

## 2026-09-29 — the drafting rule is demoted to a convention: re-derivation failed

**Bucket: framework claim withdrawn, not corrected. No manuscript, no gate, no threshold.**

Yesterday's entry withdrew the *evidence* for the drafting rule. This entry records the
attempt to replace it, which was made against the only published chapter-level corpus in
this repository and **did not succeed**. Two candidate mechanisms were measured and both
were falsified. The rule is therefore kept as a convention with no numeric claim behind it.

## What was available

`tools/prose/calibration/corpus/multivolume/` — six published fiction volumes with real
chapter boundaries, 303 chapters:

| volume | chapters | words | CV | min | max |
|---|---|---|---|---|---|
| *Pride and Prejudice* | 61 | 126,006 | 42.9% | 681 | 5,227 |
| *Jane Eyre* | 38 | 190,336 | 39.9% | 1,950 | 11,296 |
| *Wuthering Heights* | 33 | 119,763 | 45.0% | 1,430 | 7,354 |
| *Middlemarch* | 86 | 324,110 | 43.5% | 874 | 8,327 |
| *Tess of the d'Urbervilles* | 60 | 155,843 | 33.3% | 1,036 | 4,710 |
| *Dracula* | 25 | 46,281 | 41.5% | 1,006 | 4,859 |

The band re-measures to **33.3–45.0%** against the recorded 33.4–45.1%. `U1`'s calibration
is sound and is untouched. That much stands.

## A limit that had to be stated first

The 140-novel public-domain corpus **cannot answer this question**. `chunk-pd-corpus.py`
slices it into fixed 2,150-word chunks, so it has no chapter boundaries of its own and holds
no evidence about chapter length. This is recorded because it is the obvious place to look,
and any claim resting on it would repeat the error being corrected — a real measurement of
an artifact that is not the thing being asked about.

## Candidate 1 — distribution shape. FALSIFIED

All six real volumes are right-skewed (0.27 to 2.39). The pilot is −0.08; the
re-partitioned Merope books are 0.04 and 0.52. That reads as a clean discriminator: real
boundaries leave a short tail, cut chapters make a flat distribution.

Tested by re-partitioning each volume's **own prose** into random equal-count parts, 200
trials each — 1,200 null distributions in total:

| volume | real skew | null min | null median | null max |
|---|---|---|---|---|
| *Pride and Prejudice* | 1.51 | 0.33 | 1.53 | 3.12 |
| *Jane Eyre* | 1.21 | −0.66 | 0.21 | 1.30 |
| *Wuthering Heights* | 0.71 | −0.90 | 0.17 | 1.96 |
| *Middlemarch* | 0.57 | −0.37 | 0.31 | 1.33 |
| *Tess of the d'Urbervilles* | 0.27 | −0.49 | 0.23 | 1.27 |
| *Dracula* | 2.39 | −0.63 | 0.43 | 2.00 |

Every real value falls inside its own null range, and **2 of 6 sit at or below the pooled
null's 25th percentile.** The discriminator was the null distribution, not the books.

## Candidate 2 — short chapters close the same way long ones do. FALSIFIED

If "a chapter ends when the thing in it is finished" is a real mechanism, a 500-word
published chapter should end as resolved as a 3,000-word one. Scored all 36 short chapters
(under 0.6 × median) against 267 long ones, on whether the closing paragraph leans resolved
or suspended.

    short chapters   0.36
    long chapters    0.36

No separation whatsoever. The measure is a word-list proxy and too crude to defend with a
better version of itself, which is why it is reported as a failed attempt rather than
quietly dropped.

## The decision

The rule — **a chapter is as long as the thing in it takes, and not a word more** — is
retained as a **convention**. It is not deleted, because nothing here shows it produces bad
books; the pilot was written under it and reads well. What is withdrawn is its standing as
a derived finding.

`DRAFTING_FRAMEWORK.md` now states that the rule is a convention, carries no numeric claim
and no distributional promise, and that **nothing in this project has shown that a book
written this way lands in the published band.** The pilot's 12.1% is the expected output of
the method in use, not a defect to be repaired.

**The tenth instance of the recurring failure** — instrument honest, gap filled with the
more dramatic story — and the first where the temptation was to publish a mechanism because
two measurements had not yet come back. The skewness result looked publishable for about
one tool call: six real volumes, all positive, our books near zero, and a clean story about
tails. The null was what made it a story about nothing.

Earlier nine: KF-004, KF-005, Freeze 8, Freeze 9, deletion-layer escalation,
archive-as-graveyard, three-copies, the from-scratch U1 failure, the re-partition evidence.

**What would actually settle it.** Not more statistics over chapter lengths. A real
mechanism would have to be something a reader or writer recognises in a specific chapter —
which means the test is a held-out judgement, not a distributional one. Six volumes is also
a small corpus for any distributional claim, and this entry does not pretend otherwise.

Cheaper fix, applied as always: **name the state, don't build a detector.** The state is now
named — the rule is a convention, and the reason is written down where the rule is stated.

---

## 2026-10-01 — the all-books suite: a rule that fires on its own source, and rows that cannot see progress

Found by running every gate across every book (`incunabula/SUITE-2026-10-01.md`).

### 2026-10-01 — A22 fires on the book it was calibrated on
- **row:**      A22
- **observed:** Running deslop on Hollow Bridge itself fails A22 "excluded-book
               residue" about thirty times on the book's own plot device (`a ledger`,
               `the ledger` — the Ledger is the novel's form). The rule's own comment
               names the calibration: "Hollow Bridge scores 30 hits here. Zero
               tolerance is intended." Zero tolerance is intended for other books; the
               rule has no exclusion for its own source.
- **n:**        1 book (the excluded book itself)
- **evidence:** `tools/prose/deslop-check.sh` HARD list; suite run 2026-10-01
- **motive:**   aesthetic — a rule that convicts its own corpus teaches its reader to
               ignore its verdicts
- **state:**    observed
- **proposes:** none by the table (n=1). Applied anyway by human ruling the same day —
               Freeze 11 demotes A22 to report-only on a self-scan of the excluded
               book itself; cross-book scans unchanged, control-probe verified. See
               `GATE_FREEZE.md` Freeze 11.

### 2026-10-01 — L1 cannot see a book in progress
- **row:**      (brief)
- **observed:** `check-length.py` reports a book that is still being drafted as LENGTH
               FAILURE ("the book being shorter than the book that was asked for") —
               The Origin Point is 13 of 30 planned chapters in. In-progress and
               delivered-short are different states and the row cannot tell them apart.
- **n:**        1 book
- **evidence:** `tools/prose/check-length.py`; suite run 2026-10-01
- **motive:**   aesthetic — a delivery gate that cries during drafting is trained out of
               its reader before delivery
- **state:**    observed
- **proposes:** none by the table (n=1). Applied anyway by human ruling the same day —
               Freeze 11 gives check-length an exit 4 keyed on the book's own
               `status: in_progress`, with control 12 testing both arms. See
               `GATE_FREEZE.md` Freeze 11.

### 2026-10-01 — a published book trips A10a twice
- **row:**      A10a
- **observed:** Hollow Bridge (published, in print) carries `notably,` at chapter 10
               line 101 and chapter 11 line 64 — two words of nonfiction filler in a
               novel, both inside the "published prose: 0" cap.
- **n:**        1 book
- **evidence:** `tools/prose/deslop-check.sh`, suite run 2026-10-01
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. The prose is in print; recorded so the finding is not re-found.

### 2026-10-01 — a published book's delivered shape fails U1 and U6
- **row:**      U6
- **observed:** Hollow Bridge's delivered chapters vary at CV 13.7% (U1) and open
               with the antithesis frame in 6 of 11 chapters (U6) — both deliberate
               consequences of its fixed per-chapter architecture and its linked-chapter
               form, both now in print.
- **n:**        1 book
- **evidence:** `tools/prose/check-uniformity.py`, suite run 2026-10-01
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. Recorded in `finished-manuscripts/hollow-bridge/RUN_REPORT.md`;
               not repaired post-publication.

### 2026-10-05 — an append-only file rewritten end to end by a text-mode write
- **row:**      brief | delegation
- **observed:** `tools/niche-grow.py` grew the niche pool correctly but wrote it with
               Python's default text mode, which on Windows rewrites every `\n` as `\r\n` —
               so a growth that added 960 lines and removed none showed in git as 1010
               added and 45 deleted, and the append-only guarantee was a fiction in the one
               file where it is load-bearing for published rolls.
- **n:**        1 tool, 1 pool, 1 growth
- **evidence:** `git diff --numstat tools/niche-pool.txt` reading `1010 45` after a run whose
               own prefix check had passed; `file` reporting CRLF terminators on a repo that
               stores LF. Found by running the tool, not by reading it.
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none, and the fix is in the tool rather than in a registry: `newline=""`
               on read, `newline="\n"` on write. Worth noting that a prefix check comparing
               *raw lines* is also too strict — it would have made the pool header
               uneditable, since the dice skips `#`-comments and the header is not part of
               the invariant. The check now compares parsed niche lines.

### 2026-10-05 — a pool grown without a concept budget reads as depth and is padding
- **row:**      brief | delegation
- **observed:** The first growth to 1000 niches drew each aesthetic concept
               independently, so 202 concepts appeared more than once and the
               worst — cyberpunk — appeared 14 times, which is one shelf with the
               dice loaded, not fourteen. A pool is a set; this was a distribution
               wearing a set's clothes. The same run also shipped 19 bare concept
               names ("incoherents", "systems art") that describe no book at all.
- **n:**        1 pool, 960 grown niches, 636 concepts available
- **evidence:** counting the longest harvested concept per niche across the grown
               region: 202 reused, max 14, against 424 distinct concepts used.
               Sibling defect found in the same pass: five entries in
               `tools/aesthetics-concepts.txt` (cyberpunk, parody, adaptation,
               ensemble cast, sequence) are also genre or form words, so one word
               could be drawn from two axes and spend the budget on a collision.
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none — the fix is a `CONCEPT_BUDGET = 2` in the grower and dropping
               the bare-concept shape, not a threshold anybody adopted. The grown
               region was rebuilt under them (seed 20261006) after checking that the
               only published roll records `pool_size: 35`, so no niche beyond the
               35th has ever been drawn and nothing published could be invalidated.
               Max reuse 14 -> 2, bare concepts 19 -> 0, "art" entries 86 -> 74.

### 2026-10-05 — a contamination check that flagged the English canon
- **row:**      brief | delegation
- **observed:** `tools/check-manuscript-integrity.py` was written to find stray
               CJK and Cyrillic in a non-English manuscript, and on its first run
               across the workspace it reported 2,000-plus contaminated lines in
               books that are perfectly clean, because "the", "and" and "with"
               were on its English word list with nothing to say the book under
               test was written in English. Two further versions of the same
               mistake: reading `language: "en"` as a non-English code, and
               treating an undeclared language as foreign.
- **n:**        1 tool, 3 defects, 12 books, ~1,900 chapters scanned
- **evidence:** the check's own first run: 183 false positives on one chapter of
               demo-magician, 145 on marrow-light chapter 24. All from the English
               word list. Zero real findings in the whole workspace afterwards.
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none, and the fix is the opposite of a threshold. The English-word
               check now runs ONLY where the book has declared itself non-English;
               unknown is treated as unknown rather than as foreign. The character
               allowlist is built from Unicode BLOCKS instead of being typed from
               memory, because the hand-typed one rejected German "Ö" in
               Vorräte and "²" in a fire report's "0.6m²" within one run.
               **Markup is counted, not judged** — bold in a draft is a convention,
               and reporting it put 103 FAILs across clean books. A check that
               fails on everything has no signal left to give.

---

## 2026-10-05 — Kagiroi Drift production review

Four observations from the production and revision of one short novel. All n=1, all
`observed`, none promoted: a book that trips something writes a line, it does not move
the gate.

### 2026-10-05 — declared-arcs diversity passed while one resolution circuit ran four times
- **row:**      N2 (beat arcs) | resolution mechanisms
- **observed:** A book passed N2 with eight distinct declared beat arcs while executing one
               interpersonal resolution circuit — sensory overload, physical anchoring,
               intimacy, calm — across four consecutive chapters. N2 compares declared arc
               strings, so any declaration phrased distinctly passes while the same
               mechanism repeats underneath.
- **n:**        1 book (kagiroi-drift), 8 chapters, 4 consecutive repetitions
- **evidence:** kagiroi-drift/RUN_REPORT.md — N2 reported "8 distinct chapter arcs" PASS
               against a recorded fourfold circuit; the circuit was broken only when a
               structural revision staged its deliberate failure in chapter 3.
- **motive:**   aesthetic — the author's account: the book having one scene four times is
               not variety, and a gate that reads declared labels cannot see it
- **state:**    observed
- **proposes:** give each declared beat arc a `resolution_mechanism` field in
               NARRATIVE_LEDGER.yaml, and have N2 report any mechanism succeeding more
               than twice consecutively. Report-only, like N2 itself: a repeated circuit
               is sometimes deliberate, and no corpus of published resolution sequences
               exists from which a cap could be derived.

### 2026-10-05 — a character brief with no aesthetic contract filled itself in from trope
- **row:**      intake schema (Phase 0) | case-keeper (ENTITY_STATE)
- **observed:** Given "fit, muscular female salvor in a hard-SF yuri novel", the drafting
               model defaulted to heavy, clunky, butch signifiers — broad shoulders, heavy
               thighs, coarse odours, masculine mass — where the stated aesthetic was
               slender athletic femininity with defined muscle. The intake schema had
               nowhere to record physique, muscle tone, or excluded stereotypes, so the
               drift was invisible until the prose existed.
- **n:**        1 book (kagiroi-drift), 8 chapters rewritten
- **evidence:** kagiroi-drift chapter-01 through chapter-08 rewrites; manual purging of
               the heavy/butch signifier set against a brief that named the intended
               athletic-feminine aesthetic.
- **motive:**   aesthetic — the author's account: the brief named the aesthetic and the
               model still defaulted; a contract with no slot for the body is a contract
               that outsources it to the training distribution
- **state:**    observed
- **proposes:** add a Physique & Aesthetic Contract round to
               `skills/incunabula-codex/references/intake-schema.md` — frame, muscle
               definition, beauty register, and an explicit anti-trope list per named
               character — mirrored into ENTITY_STATE.yaml so case-keeper carries it and
               collator can audit the manuscript against it.

### 2026-10-05 — a foundational wound sat as lore until it was forced
- **row:**      N1 (narrative debt) | foundation trauma
- **observed:** The Minato-9 pod trauma — the strongest psychological anchor in
               foundation.md, with full sensory specificity — sat as passive backstory
               texture for six chapters and was fired only when a structural revision
               staged it. N1 would have caught it at delivery; nothing flags a crucible
               that has not yet trapped anyone mid-book.
- **n:**        1 book (kagiroi-drift)
- **evidence:** kagiroi-drift/NARRATIVE_LEDGER.yaml D-001, resolved only by the chapter 7
               rewrite (Skiff Lock Omega); RUN_REPORT.md item 1.
- **motive:**   aesthetic — the author's account: a wound the story never re-opens is
               scenery with a tragic press release
- **state:**    observed
- **proposes:** foundation-declared wounds carrying sensory tokens enter the ledger as
               wound-class obligations with a `fire_by` milestone (pre-climax by default),
               and check-narrative N1 reports a wound still unfired past its milestone.
               The delivery gate is unchanged — it already forbids shipping OPEN debt, so
               this is a timing signal, not a new failure.

### 2026-10-05 — leads lost their working register outside the scenes that justified it
- **row:**      V2 (dialogue register)
- **observed:** Outside intimate scenes the romantic leads collapsed into breathless,
               poetic whispering, while secondary characters held sharp, grounded,
               technical voices. The tag layer showed it first and is not the whole of it.
- **n:**        1 book (kagiroi-drift), 2 leads, chapters 3 and 6 audited
- **evidence:** kagiroi-drift dialogue audits (RUN_REPORT.md item 4);
               `tools/prose/check-dialogue-tags.py` V1/V2 was built from this failure and
               reports the breath-family share — it sees the tags, not the register range.
- **motive:**   aesthetic — the author's account: two people who work a salvage rig
               together should be able to argue about hydraulics without reverence
- **state:**    observed
- **proposes:** two moves, both unenforced: (1) the Phase 4 evaluation asks explicitly
               whether each lead pair holds a peer-to-peer workaday register — technical
               jargon, dry banter, irritation — distinct from the intimate register; (2)
               V2 extends to per-character breath-family share per chapter so the audit
               has the table. No corpus of per-character register range exists, so
               nothing here may gate.
### 2026-10-05 — a slop rule that could only see half of English
- **row:**      A23 (parenthetical dash) in `tools/prose/deslop-check.sh`
- **observed:** The rule's regex is `—[^—\n]{1,70}—`. In POSIX ERE a backslash inside a
               bracket expression is a literal backslash, not an escape, so the class is
               em-dash, backslash, and the letter `n` — not "em-dash or newline". The
               rule can therefore only fire on a parenthetical dash containing neither
               `n` nor a backslash, which is most parenthetical dashes in English. The
               drafting linter `tools/lint-chapter.py` reads the same table and hands the
               regex to Python, where `[^—\n]` means what it was meant to mean, so the two
               instruments disagree — and the disagreement is in the frozen scanner.
- **n:**        1 rule. Measured on 449 chapter files / 2,562,491 words of the installed
               calibration corpus, the frozen regex matches 561 of the 1,159 occurrences
               the rule is written to match — it cannot see 51.6% of them. Fiction only
               (306 files): 421 of 855, so 49% unseen. In kagiroi-drift: 0 of 8 chapters
               flagged, containing 4 occurrences the scanner cannot see.
- **evidence:** kagiroi-drift NARRATIVE_LEDGER.yaml `lint` section, rows A23; the four
               occurrences are ch-01 `—clean copper and bitter neuro-balm—`, ch-04
               `—the sudden, irreversible loss of their lifeline to the station—`, ch-05
               `—warm metal, ozone, bitter glycol—` and `—the ghost of Saito's frozen
               limbs—`, every one containing an `n`. Scanner output: `A23 parenthetical
               dash 0.00 per 1k` on all three chapters while the linter reports 0.49,
               0.50 and 0.80. Isolated test: `grep -cE '—[^—\n]{1,70}—'` returns 0 on
               each of the four and 1 on `—oh, wow—`. Corpus counts by regex reading,
               measured read-only at `tools/prose/calibration/corpus/`:

               | subset | intended | frozen regex | worst chapter |
               |---|---|---|---|
               | all 449 files | 1,159 hits, 0.45/1k | 561 hits, 0.22/1k | 6.03 vs 2.48 /1k |
               | fiction, 306 files | 855 hits, 0.70/1k | 421 hits, 0.34/1k | 6.03 vs 2.48 /1k |
               | nonfiction, 143 files | 304 hits, 0.23/1k | 140 hits, 0.10/1k | 1.68 vs 2.24 /1k |
- **motive:**   aesthetic — the author's account: a rule that cannot see most of what it
               was written to see is worse than no rule, because the book is certified
               clean against an instrument that was not looking
- **state:**    proposed
- **proposes:** re-derive A23 before fixing it, then fix it — and treat the two as one
               change, because the numbers make a naive fix worse than the bug. Three
               things are wrong at once:
               (1) **The blind spot.** The bracket needs `[^—\\n]` in a POSIX context, or
               the whole rule should be restated as a form grep cannot misread.
               (2) **The cap.** `deslop-check.sh` states its own rule — cap = ~1.5x the
               worst calibration document. Under the reading the rule was *meant* to have,
               the worst fiction chapter on the installed corpus is 6.03/1k, so that
               arithmetic wants a cap near 9/1000, three times the present 3/1000. Fixing
               the regex while keeping the cap would fail published Hardy and Eliot; fixing
               it and quietly keeping the old number would be a silent loosening dressed
               as a bug fix. Neither is acceptable. The cap has to be set from a stated
               corpus.
               (3) **The provenance.** `CALIBRATION.md` records A23 as "85 occurrences,
               1.79/1k" from "the 48 narrative documents" and gives no path. That figure is
               not reproducible from any subset installed here (fiction 421, nonfiction
               140, montgomery alone 54), so the number that makes the cap trustworthy
               cannot currently be checked by anyone. An unattributable measurement is the
               defect this whole directory was built to prevent, and it is a second entry
               in its own right.
               So the order is: identify the derivation corpus, re-measure under the
               corrected regex, set the cap from that, then re-key `deslop-check.sh` in
               GATE_FREEZE.md and re-run the controls. Until then nothing moves —
               `tools/prose/deslop-check.sh` is untouched at `20e1976d20312974`.
               Nothing in kagiroi-drift changes either way: its worst true reading is
               0.80/1k against the current cap, and 0.80 against a re-derived one too.
