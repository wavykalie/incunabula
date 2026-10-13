# Scanner calibration record

How the thresholds in `tools/deslop-check.sh` were set, what evidence they rest on,
and what the scanner still cannot do.

Previously the caps were invented. They were also actively wrong: the old em-dash
cap (4 per 1,000 words) failed **36 of 51** published chapters of the reference the
book is meant to sound like. A gate that rejects published human prose is not a
gate, it is noise.

---

## 1. Corpus

| Corpus | Documents | Words | Role |
|---|---|---|---|
| *Wandering Witch: The Journey of Elaina*, vols. 1/2/5 (Yen Press) | 48 | 175,144 | **governing** — the register this book targets |
| *Coldbrook Junction*, chs. 1–11 | 11 | 56,144 | native-English control |
| **Combined** | **59** | **231,288** | |

Elaina's afterword and appendix files are excluded: they are non-fiction back
matter, and including them inflates rates for prose that is not narrative.

The exclusion is enforced in the tooling (`measure.py`, and the two-control runner
in `tools/validate-controls.sh`), so the record and the measurement cannot drift
apart again. Every number below comes from one run of
`measure.py corpus/elaina`, saved to `calibration-report.txt`.

### Two properties of this corpus that limit it

**Coldbrook cannot calibrate dashes or quotes.** It writes dashes as `--` (22 of
them) and quotes as straight ASCII. Its em-dash and curly-quote rates are therefore
`0.00` as a *formatting* artifact, not a style signal. Any cap derived from it for
D1 or A20 would be meaningless, so D1 is governed by Elaina alone.

**Elaina is a translation.** Its em-dash density reflects a Japanese light-novel
dash convention carried into English by the translator as much as authorial voice.
Since that is exactly the register this book targets, Elaina legitimately governs —
but the resulting D1 cap is *looser than native-English KDP prose would justify*, and
that is a deliberate choice, not an oversight.

---

## 2. Method

Two rules, applied mechanically:

1. **A rule may stay zero-tolerance only if published narrative prose never does it**
   — literally 0 hits in 231,288 words. If published prose does it, it cannot be
   banned; it can only be overdone.
2. **A density cap is set at roughly 1.5× the worst single calibration document**, so
   the reference passes with headroom rather than squeaking by.

Caps are expressed as rationals, `allow_n` per `allow_w` words. The original script
used `hits * 1000 / words`, which truncates: **any cap below 1 per 1,000 words was
silently unenforceable**, because a single hit in a 2,500-word chapter evaluates
to `0`.

---

## 3. What the measurements showed

### Style metrics (per document, n=59)

| Metric | median | p90 | max | was | now |
|---|---|---|---|---|---|
| D1 em dash /1k | 3.9 | 6.7 | 8.9 | 4 (**failed 22 of 48**) | **10** (warn 7) |
| D2 rule of three /1k | 1.0 | 2.0 | 3.6 | 8 | **5** (warn 4) |
| -ly adverbs /1k | 14.4 | 17.4 | 24.3 | note only | **26** (warn 20) |
| P1 repeats of one opener /1k | 0.9 | 2.2 | 4.3 | fail at >2 **absolute** | **6** |
| P1 top opener, share of sentences | 2.5% | 5.2% | 11.8% | — | **15%** |
| P2 duplicate sentences / doc | 0 | — | 4 | fail at ≥2 | **1 per 2,000 words** |
| P3 longest short-sentence run | 2 | 4.0 | 6 | fail at ≥4 | **fail at ≥7** |
| short sentences, % of sentences | 9.8% | 14.2% | 16.9% | — | note only |

**D2 is the one cap with a two-sided validation.** The human corpus tops out at
3.6/1k, and Coldbrook (the AI-written control) runs 5.5–5.8/1k in chapters 2 and 3,
so 5/1k is the smallest round allowance that separates them. An earlier revision
of this record put the D2 worst document at 5.8 and set the cap at 7; 5.8 was never
a human document — it was Coldbrook chapter 3, read off the wrong control. Fixed.

**For P1, P2 and P3 the scanner's own count governs, not `measure.py`'s.** They
tokenise differently, so the two disagree on the tail of the distribution, and the cap
has to be set against the number the gate actually computes.

- **P2.** The scanner counts 4 duplicates in one published chapter (a deliberate
  refrain); `measure.py` requires a longer normalised form and reports 1.
- **P3.** The scanner finds a run of **6**; `measure.py` reports 5. Six must pass,
  because a published document reached it, so the cap is 7.
- **D2.** Its regex matches any `X, Y, and Z` comma shape, so it also fires on ordinary
  compound sentences carrying an `, and` clause, not only on rhetorical triads. In a
  2,400-word chapter that is a handful of harmless hits against a cap of 12. Found by
  running the gate on a real draft. **Read the hits before rewriting them**: the first
  draft of chapter 1 failed at 5.40/1k, and the honest fix was to write the missing
  material and rework the two genuinely rhetorical triads, not to strip every `, and`.

P1 needed a second condition because the absolute count does not scale: 7 repeats in
a 9,000-word chapter is unremarkable, 7 in a 600-word sketch is not. It now fails on
either a per-1k rate or a share-of-sentences test.

### Rules that published prose *does* trip

This is the finding that reshaped the rule list. Each rule was split into the phrases
that **never** occur in 231k words (kept hard) and the phrases that **do** (capped).

| Rule | Hits | Worst doc /1k | What actually fired |
|---|---|---|---|
| A2 magic adverbs | 37 | 0.95 | `quietly` ×20, `deeply` ×13 — all **literal**: "sighed deeply", "bowed deeply", "listened quietly", "returned quietly from the kitchen" |
| A3 grandiose nouns | 9 | 4.29 | only `landscape`, `realm`, `vibrant` — ordinary nouns in a travelogue |
| A15 superficial -ing | 7 | 1.69 | only `, feeling`, `, knowing`, `, allowing` — ordinary participial phrases |
| A23 parenthetical dash | 85 | 1.79 | **all 85 distinct and legitimate**: `—the cat—`, `—and only her sister—`, `—in fact, it wasn't much of a road at all—` |
| A10 filler transition | 14 | 1.13 | only `in order to` ×9, `when it comes to` ×5 |
| A5 negative parallelism | 10 | 0.61 | "was not about", "were not just" — normal English |
| A6 *Not X. Not Y.* | 1 | 0.30 | a character's emphatic speech |
| A1 delve family | 2 | 0.31 | only `harness`, `leverage` |
| A17 invented label | 0 | — | nothing — it only fires on Coldbrook, which is the guard working |
| A22 excluded-book residue | 4 | 0.91 | **only Coldbrook**, the excluded book — the guard working |

Hit counts and rates here are from the 48 narrative documents. The earlier version
of this table was measured with the afterword and appendix still in the corpus, which
inflated most of them (A22 30 → 4, A6 10 → 1) because back matter talks about the book
rather than being the book.

`delve`, `tapestry`, `seamless`, `robust`, `cutting-edge`, `myriad`, `palpable`,
`at its core`, `it's worth noting`, `underscoring`, `showcasing`, `experts say`,
`in summary` — **zero occurrences in 231,288 words of published prose.** Those stay
zero-tolerance. That contrast, not taste, is what separates the two tiers.

### A20 was broken

A20 (`unicode decoration`) lumped decorative arrows together with curly quotes and
scored **17,146 hits, 97,897 per million words, in 48 of 48 documents** — because
typeset books use curly quotes. A rule that fails 100% of published prose is a bug.
Split: arrows (`→ ⇒ ← ↔`, genuinely 0 occurrences) stay hard; curly quotes became a
note.

### P2 is legitimately imperfect

A flat "0 duplicates" is wrong. One published 9,184-word chapter repeats **four
sentences verbatim** as a deliberate refrain ("She could, to put it clearly and
concisely, see the future."). Intentional repetition exists in good prose, so P2 is
scaled by length and will always carry a false-positive mode on refrains. Read the
hits before rewriting.

---

## 4. Validation

Run after every cap change. A scanner that passes everything is worthless; one that
fails human prose is worse. `tools/validate-controls.sh` runs all three and exits
nonzero if any control misbehaves.

| Control | Kind | Expected | Result |
|---|---|---|---|
| Elaina, 51 files (48 narrative + 3 back matter) | human | all PASS | **0 failing rows** |
| `slop-fixture.md` (synthetic) | positive | FAIL | **FAIL, 17 failing rows** |
| Coldbrook, 11 final chapters | AI-written, published | should not all pass | **9 FAIL, 2 pass** |

The Coldbrook result is the useful one. It is a published book written by this same
pipeline, and it fails on exactly the tells that survived calibration — `A1a`
(*seamless*, *leverage*), `A10a` (*at its core*), `A22` (the excluded engine), `P2`,
and `D2` (chapters 2 and 3). The scanner rejects the AI-written book and accepts the
human-written one.

**A bug found while re-validating this section, June 2026.** Directory mode globbed
`"$target"/*.md` only. The Elaina corpus is `.txt`, so the command recorded here as
the negative control matched **zero files**, ran no checks, left the failure flag at
0, and printed `RESULT: PASS`. The earlier "48 / 48 PASS" was therefore the vacuous
kind of pass — the exact failure mode this gate exists to prevent. Fixed: directory
mode now scans `.md` and `.txt`, and an empty expansion is reported as a failure
rather than a pass. The numbers above are from the fixed scanner.

**A third bug, and the worst of the three.** P3 (short-fragment run) could never fail.
The awk pass emitted `nsent | opener count | duplicates | "two word opener" | run`,
and the shell read field 5 as the run length — so it read the *second word of the
opener* instead. `[ "was" -ge 6 ]` is an error, and an error is false, so the check
reported `ok` for every document ever scanned and the column printed the opener's
second word where a number belonged. The measurement inside the awk was right; only
the read-back was wrong. Worse, the same field confusion truncated the reported opener
to one word. Both fixed, and switching P3 on immediately caught the *threshold* being
wrong too: the reference corpus reaches a run of 6, so capping at 6 failed human prose.
The cap is now 7, and the fixture (a run of 9) still fails. Three defects, all of them
in the direction of the scanner being more permissive than it claimed.

**A second correction.** The previous version of this tool was reported as finding
"genuine tells" in Coldbrook — a 10× repeat of *"it was"*, two *Not X. Not Y.*, a
four-sentence fragment run. Under measured caps those are **false positives**:
published human prose does all three (P1 to 4.3/1k, A6 to 0.30/1k, P3 runs of 5).
They were cap errors, not findings.

---

## 5. Limits, on the record

- **Mechanical only.** No voice, rhythm, dead metaphor, or one argument restated ten
  ways. Passing is necessary, never sufficient.
- **These caps are tuned to this register.** They are derived from light-novel
  narrative prose. Non-fiction, thriller, or literary fiction would want a different
  derivation from a different corpus.
- **A22 is a canon guard, not a slop rule.** It is meant to fire on anything resembling
  the excluded book's engine. Its near-total absence from Elaina is coincidental.
- **The engineering documents in this project fail this scan** and are exempt. Scene
  packets run at 16–25 em dashes per 1k against a cap of 10 — the documentation
  register genuinely sits above the prose cap.

---

## 6. Re-deriving, if the corpus changes

```bash
cd tools/calibration
# 1. extract the epubs to plain text (one file per spine document)
python extract.py "<book>.epub" corpus/<name> <tag>
# 2. measure metrics and per-rule hit rates (afterword/appendix auto-excluded)
python measure.py corpus/elaina "<native control dir>" > calibration-report.txt
# 3. targeted greps decide hard-vs-capped: anything with 0 hits can be hard
grep -ohiE "<candidate pattern>" corpus/elaina/*.txt | sort | uniq -c | sort -rn
# 4. re-validate all three controls after any cap change (exits nonzero on failure)
bash ../validate-controls.sh
```

`measure.py` holds the **pre-split** rule families, so it measures rule groups as a
whole. The hard/capped split for individual phrases comes from step 3, not from it.

`validate-controls.sh` is the gate's own check: it re-runs the human, positive, and
AI-written controls and refuses to report success unless all three behave as the
method predicts.
