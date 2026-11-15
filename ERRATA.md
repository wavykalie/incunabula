# ERRATA

The printer's errata sheet: corrections issued after the impression, and observations that
have not yet become corrections.

**Append-only.** Entries are added; entries are never edited to look better than they were.
An entry that turned out to be wrong gets a `WRONG` line under it, and the wrongness stays
visible. That is the point — a ledger with no recorded mistakes is a ledger being curated,
and a curated ledger cannot be trusted with the job.

**Amended 2026-10-14 — standing claims are repaired in place.** Append-only governs
history: a dated entry records what was measured on its date, and is never rewritten.
It does not make a claim immortal. Text outside the dated entries — a heading, a tally,
a count in prose — describes the program **as it is now**, and the program moves. When
the live program contradicts one of those standing claims,
`tools/prune-stale.py` (the self-prune) corrects it in place and keeps the old wording
verbatim in `maintenance/PRUNING_LOG.md`, in the maintenance-protocol §7 format. A
claim inside a dated entry is never edited: it is reported with the number the program
now has, for the author to rule on, because a record of what was true then is history
and not drift. This is the one carve-out from append-only, author direction 2026-10-14,
and it is exactly this wide.

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


---

## The ledger

**One entry, and it is the only one a fresh install should carry.** A new ledger is
empty, and this file is where your own findings accumulate — seeding it with somebody
else's would make the record a default rather than evidence.

The entry below is not a finding about prose. It records the constraint that produced
it, in the ledger's own format, so that the next person to notice an entry in a fresh
install does not have to guess why it is here.

### 2026-10-15 — the validator requires an entry, so the template ships one
- **row:**      (brief) — the record layer's own shape
- **observed:** `tools/prose/check-errata.py` fails on a ledger with no entries in the
               required format, so an empty template cannot pass the guard on a fresh
               install. The alternative was to ship somebody else's findings as the seed.
- **n:**        1 — every install, from the first run
- **evidence:** `tools/prose/check-errata.py`, run against an empty ledger
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. If the guard should accept an empty ledger, that is a change to a
               frozen instrument, and it goes through the freeze procedure in
               `GATE_FREEZE.md` — not through this entry.

An entry is added when a book trips something, an instrument is found to be wrong,
or a measurement is re-derived. `tools/prose/check-errata.py` validates every entry
against the format above and against `PRINTERS_COPY.md`'s rules, and it is the
mechanism by which this layer improves rather than merely accumulates.

**Nothing here is a rule until it is adopted, and adoption is a person's act.** An
entry that turns out to be wrong gets a `WRONG` line under it; the wrongness stays
visible, because a ledger with no recorded mistakes is a ledger being curated.

### 2026-10-15 — the anti-AI catalog merged into one home
- **row:**      (merge) — the record layer's own shape
- **observed:** The `humanizer` skill's 24-pattern catalog and `setting`'s anti-AI tell
               list described the same tells as `deslopify/references/style_guide.md`
               under two other roofs — the same catalog in three places, with the
               scanner as the mechanical fourth. All three are now one catalog in the
               deslopify guide. The duplicates were folded in, not appended, and where
               two lists described one tell the sharper wording won: negative
               parallelism, tricolon, vague attributions, em dashes, the serves-as
               dodge, superficial analyses, false ranges, "despite its challenges",
               grandiose inflation. Tells that existed in only one list moved in whole:
               promotional tone, insisting on notability, synonym cycling, chatbot
               residue, knowledge-cutoff hedging, sycophancy, filler, over-hedging,
               generic positive endings, title-case headings, named emotions,
               over-smooth transitions, dramatic And openers, decorating metaphors, the
               pseudo-profound closing. `humanizer`'s constructive half ("add a pulse")
               is the guide's second half; its per-chapter checklist moved to the
               `deslopify` skill. `setting` now references the catalog and restates
               nothing. The scanner is untouched, per the audit's own constraint.
- **n:**        1 — one catalog, one checklist
- **evidence:** `skills/deslopify/references/style_guide.md`, `skills/_archive/humanizer/MOVED.md`
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. Three lists of the same tells is redundancy in the documentation,
               not a measurement; no threshold, rule, or regex moved.

### 2026-11-06 — V3 gates, and U5's warn line moves to the measured p10
- **row:**      V3 (new) | U5
- **observed:** `check-dialogue-tags.py` gains V3, the first row in that class with a
               measured population: the whole-book breath-family share of tagged spans,
               fail above 0.107, warn above 0.082. The corpus is 167 public-domain
               English novels (stratum C-dist-2 of `tools/prose/study`, frozen extractor
               v2, disjoint from the 140 novels in `calibration/`), where 5% of books
               exceed the fail line. The pipeline's fifteen books run at median 0.168 and
               11 of 15 exceed it; the twenty naive-draft books exceed it six times. U5's
               warn line moves 75 -> 73.7, that stratum's p10, which fires on 12 of the
               fifteen pipeline books and none of the naive ones.
- **n:**        167 human books; 35 pipeline and naive-draft books
- **evidence:** `tools/prose/study/STUDY_REPORT.md` section 5.3;
               `tools/prose/study/corpus/dist-features-2/cdist.csv`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none further. The fail line is a corpus percentile and may not move on a
               book's failure; the 1.5x headroom convention does not apply to a two-sided
               band, and tightening the fail line to the p10 would fail 26% of humans.

### 2026-11-06 — four study measures enter the Rejected registry
- **row:**      (registry) — `PRINTERS_COPY.md` section 4
- **observed:** The prose-tell study's AI-term cap, weather-opener gate, cross-book
               name-reuse threshold and opening-similarity row are recorded as rejected,
               each with the arm-level count that killed it. The Rejected registry goes
               30 -> 34 entries, and `REJECTED_FLOOR` in `tools/prose/check-errata.py`
               is raised to 34 in the same change.
- **n:**        1 change; the counts behind it come from 167 human books and 35
               pipeline/naive books
- **evidence:** `PRINTERS_COPY.md` section 4; `tools/prose/check-errata.py`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none. The rows now work in the other direction: a future proposal that
               reaches for one of them has to argue with the count that rejected it.

### 2026-11-06 — P1 is a rate whose denominator assumes a chapter, and a document layer is not one
- **row:**      P1 (anaphora abuse) — appears only when the prose gate is scoped per layer (candidate 17)
- **observed:** one occurrence of a repeated two-word opener fails any scanned file smaller than 167 words, because P1 fails when count x 1000 exceeds 6 x words; two layers of a layered book (78 and 96 words) therefore fail on prose that the whole-chapter scan passes.
- **n:**        1 book (test-books/ashgrove-inventory), 2 independent documents in that book
- **evidence:**  tools/prose/deslop-check.sh over artifacts/layers/03-letters (exit 1, "amend to" x1, 10.0% of sentences) and artifacts/layers/00-film (exit 1, "a line" x1, 5.3%); the same chapter whole exits 0 with "i have" x4 at 2.9%. Row arithmetic from the scanner's own caps, not a re-measurement.
- **motive:**    aesthetic
- **state:**     observed
- **proposes:**  none. This is a scoping defect, not a threshold defect: the fix is a minimum-size rule of the same class as check-dialogue-tags.py MIN_TAGGED_FOR_V3 (report UNMEASURED below the denominator), which is a frozen-instrument change requiring a corpus. Padding a document to 167 words to satisfy it would be writing to a number.

### 2026-11-06 — `P1` fails a short document on its first repeated opener, and a second cluster replicates it
- **row:**      P1 (anaphora abuse), under per-layer gate scoping (candidate 17)

- **observed:** a document shorter than 167 words fails on a single repeated opener, because
  the cap allows 6 per 1,000 words and 167 is the first length at which one occurrence fits

- **n:**        1 book, 4 independent documents (78, 96, 131, 132 words); the second cluster
  replicates the failure and does not raise n, because it is the same book

- **evidence:** `evaluations/layer-gates-ch01.md` and `evaluations/layer-gates-ch02.md`;
  cluster 2 failed 4 of 4 layers before any fix, two of them on a single occurrence

- **motive:**   aesthetic — a 78-word letter failed on prose the whole-chapter scan passes,
  and the only way to pass was to lengthen the document to satisfy arithmetic

- **state:**    observed

- **proposes:** none. A floor now stops the rate judging such a document (`GATE_FREEZE.md`,
  2026-11-06); the entry stays `observed` until a second **book** trips it.

### 2026-11-07 — A25 has P1's arithmetic, and cluster 3 is the first real document to report it
- **row:**      A25 (antithesis formula), under per-layer gate scoping (candidate 17)
- **observed:** the cap is 3 occurrences per 2,000 words, so a single antithesis computes 3.27 against it on any document under 667 words. A 612-word annotation layer failed A25 at 1.63/1k on one instance: "the 0.25 is not a recess cut into anything. It is a gap between two skins of brick".
- **n:**        1 book (test-books/ashgrove-inventory), 1 document (cluster 3 annotations, 608-612 words)
- **evidence:**  evaluations/layer-gates-ch03.md; deslop-check.sh artifacts/layers/02-annotations exit 1 before the rewrite and exit 0 after. The hit was a real antithesis, so the prose was rewritten and no cap moved.
- **motive:**    aesthetic
- **state:**     observed
- **proposes:**  none. This is P1's finding one row over and it is deliberately NOT repaired here: adding a floor to A25 in the run that just failed on it is the sequencing GATE_FREEZE.md forbids. P1's floor was added after two clusters reproduced the arithmetic and only changed files that had failed BEFORE it existed. An A25 floor added today would change the file that failed today. Editor's decision, with its own probe and freeze entry.

### 2026-11-07 — P1 has the same size floor as A25, at about 330 words
- **row:**      P1 (anaphora abuse), under per-layer gate scoping (candidate 17)
- **observed:** the row fires on a share of sentences, so a short document reaches the cap on very few instances. Reel 8 of cluster 4 is 280 words and 46 sentences; two lines opening "Camera ..." compute 4.3% and fail. At 3,000 words the same two lines are 0.4% and pass. Fixing one line moved the count to 4.3% again on a different repeated opener, which is what a rate doing its job looks like at that size.
- **n:**        1 book (test-books/ashgrove-inventory), 1 document (film layer, 280 words). Against it: 44 published documents of 167-1,500 words scanned with the same instrument, **0 P1 failures**, including 8 at 167-400 and 11 at 400-667.
- **evidence:**  evaluations/layer-gates-ch04.md; evaluations/ch04-passes.md; tools/prose/calibration/corpus/layers (fetch-document-layers.py)
- **motive:**    aesthetic
- **state:**     observed
- **proposes:**  none. The measured human base rate is zero at this size, so a floor is not what the evidence asks for. What it asks for is the same thing A25's entry asks for: a decision about whether a 280-word shot list can be judged by a sentence-share rule at all, made with its own probe and its own freeze entry rather than in the run that failed.

### 2026-11-07 — A25 gets the 667-word floor its own rate implies
- **row:**      A25 (antithesis formula)
- **observed:** the fail line is 3 occurrences per 2,000 words, so at 666 words one real
               antithesis computes 1.50/1k against a 1.50/1k cap and fails on arithmetic;
               at 667 the same sentence passes. The row now reports UNMEASURED below 667.
- **n:**        410 published documents of 167-1,500 words, 0 A25 failures; 1 book
               (test-books/ashgrove-inventory) whose 612-word layer failed on one
- **evidence:** tools/prose/calibration/fetch-document-layers.py; the 410-document scan;
               GATE_FREEZE.md 2026-11-07; probes at 666, 667 and 678 words
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none. The cap is unchanged; the floor is derived from it.

### 2026-11-07 — P1's 167-word floor stands; the 280-word reel was a real repetition
- **row:**      P1 (anaphora abuse)
- **observed:** raising P1's floor to 334 words would pass cluster 4's 280-word film layer,
               which failed on two "Camera" openers at 4.3% of sentences. The widened layer
               corpus has 124 human documents at 167-400 words and 0 P1 failures, so the
               rate is not false-failing human prose at that size.
- **n:**        410 published documents, 124 of them at 167-400 words; 1 book
- **evidence:** tools/prose/calibration/fetch-document-layers.py; the 410-document scan;
               evaluations/layer-gates-ch04.md
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. No floor or cap moved; the decision is recorded so the next run does
               not re-derive it from the one failure.

**WRONG (2026-11-07, before the entry was a day old).** The 44-document layer corpus was 41
Evelina letters plus 3 Walton letters. The widened 410-document corpus has 47 P1 failures,
45 under 667 words, across Emily Montague, The Coquette and Humphry Clinker. The entry above
is kept as written because it records what the smaller corpus said; the decision below
supersedes it.

### 2026-11-07 — P1's floor moves to 667 on the widened corpus
- **row:**      P1 (anaphora abuse)
- **observed:** the 410-document layer corpus has 47 P1 failures under the 167-word floor,
               45 of them under 667 words and spread across three books; above 667, only
               2 of 129 fail, at 1,303 and 1,434 words with 5 and 9 instances. A rate
               calibrated on chapters cannot judge a published letter at 176 words, and the
               share test failed 22 of the same human documents, so it is not a rescue.
- **n:**        410 published documents; 281 under 667, 129 above; 3 books for the failures
- **evidence:** tools/prose/calibration/fetch-document-layers.py; the 410-document scan;
               GATE_FREEZE.md 2026-11-07; probes at 285 and 1,303 words
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none. P1 and A25 now share the 667-word document floor; the cap, numerator
               and denominator are unchanged, and the two surviving chapter-sized failures
               still fail.

### 2026-11-14 — a world that only subtracts turns a modern book into a period one
- **row:**      (delegation) — the world-rules layer, and the half of it that was missing
- **observed:** *The Parts Still Warm* passed every prose cap in the suite, at 130,003
               words, and read as though it were set a century before its own artifacts.
               The cause was not an unmeasured tell but an unmeasured absence:
               `WORLD_RULES.txt` forbade every modern object on the street (van, lorry,
               tram, tyre, road fuel, bus, cab) and no rule anywhere required a modern
               noun back, so the permitted world's vocabulary was the oldest surviving
               one. `DIRECTION.md` named the city "Victorian" while fourteen briefs in the
               same project said "Nothing Victorian"; both could be true because nothing
               measured either. Spellings and cadence had been fixed on 2026-11-12 and the
               ticket closed green, because those were what had instruments.
- **n:**        1 book, 13 chapters, 130,003 words; the defect class is a rule shape, not
               a number, so it needs no corpus to be visible and no second book to be real
- **evidence:** `tools/prose/check-diction.py` first run (34 hits, 33 of them correct
               prose), `test-books/the-parts-still-warm/DICTION_RULES.txt`, the modern-noun
               census of the thirteen chapters, `GATE_FREEZE.md` Freeze 24
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. No cap or floor moved. The proposal this entry carries is structural
               and already applied at book scope: a world's rules must say what it carries
               as well as what it forbids, and a book's register is checkable only against
               a register it declared. Promoting a *rate* from one book would repeat the
               n=1 error this ledger exists to prevent; three books that drift the same way
               would make the proposal.
