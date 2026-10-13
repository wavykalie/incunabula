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
- **Every rule here reads one document at a time.** That is a limitation of the whole
  method, not of the caps: uniformity between chapters is invisible to it by
  construction. See section 6.

---

## 6. The cross-chapter gate (`check-uniformity.py`)

### Why a second tool exists

Every rule above is measured per document. A book can pass all of them and still read as
machine-written, because the clearest signature is not a rate inside a chapter — it is
that the chapters are indistinguishable from each other. A per-document scan never holds
two chapters at once, so it cannot see this. It needed its own tool and its own
measurements.

### What was measured

Three finished manuscripts built by this pipeline, in different genres and written months
apart, against the same published corpus used above:

| manuscript | chapters | word range | CV | closing coda |
|---|---|---|---|---|
| project book A | 11 | 2,401–2,686 | **3.2%** | **6 / 11** |
| project book B | 7 | 2,077–2,402 | 5.8% | 0 / 7 |
| project book C | 7 | 1,882–2,511 | 10.8% | 0 / 7 |
| *published v01* | *17* | *559–7,521* | *48.4%* | *0 / 17* |
| *published v02* | *18* | *466–8,191* | *68.1%* | *0 / 18* |
| *published v05* | *13* | *593–9,184* | *70.6%* | *0 / 13* |

The separation is total. Published chapters vary by a factor of 20 inside one volume; a
project book held all eleven chapters inside an 11% band. Published prose never closes a
chapter on an explanatory coda in 50 chapters; one project book did it 6 times in 11.

Two tics were also measured as rates, and both became rules in `deslop-check.sh`:

| rule | patterns | published | worst published doc | project books | verdict |
|---|---|---|---|---|---|
| `A24` | explanatory coda | 0.03 / 1k | 0.88 / 1k | 1.59, 2.19, 2.11 / 1k | density, cap 1/1000 |
| `F1` | coda in the **closing paragraph** | **0 of 50 chapters** | — | 6 of 11 | **zero tolerance — a position, not a rate** |
| `A25` | antithesis *it was not X, it was Y* | 0.01 / 1k | 0.43 / 1k | 0.58, 0.71, 1.45 / 1k | density, cap 1/2000 |

### Measured and rejected

Several metrics that are widely recommended as AI tells do not discriminate on this corpus,
and are recorded here so nobody re-derives them expecting a rule:

- **Burstiness (sentence-length variance).** Published chapters: standard deviation 9.5 / 10.1
  / 10.4. Project books: 13.2 / 13.3 / 14.5. Machine-assisted prose here is *more* varied
  than published prose. The usable form of the idea is the spread of those figures **across**
  chapters, which is `U2`.
- **Type-token ratio.** Confounded by length — published chapters average 3,557 words against
  the project books' ~2,150, and TTR falls as a document grows. Needs normalisation before it
  can be a rule. Logged, not gated.
- **Word- and phrase-level candidates** — *in the world of*, spectral/dark-imagery vocabulary,
  vague attribution (*some say*, *many believe*), hedging openers, and the
  *utterly / entirely / absolutely* register — measured **≤ 0.02 per 1k in BOTH corpora**.
  Already covered by `A1`–`A25`, and the project books do not trip them.

`F1` is the interesting one. As a rate the coda is a weak rule — a dense chapter can trip
it on density alone. As a **position** it is categorical: no published chapter closes
there. A tic that only ever appears at one structural position is a habit, and habits are
not detectable by dividing by word count.

### The floors

Derived the same way as the caps — below the worst published document, with headroom, so
published prose always passes:

| check | published floor | gate |
|---|---|---|
| `U1` chapter-length CV | min 48.4% | FAIL under 30%, warn under 45% |
| `U2` per-chapter mean sentence length, spread | min 4.32 | FAIL under 3.0, warn under 4.0 |
| `U3` share of chapters closing on a coda | 0% | FAIL above 25% |
| `U4` share of single-sentence paragraphs | 50.3% | FAIL under 35%, warn under 50% |
| `U5` paragraph-length CV | 86.9% | FAIL under 55%, warn under 75% |

`U4` and `U5` measure page layout rather than sentences. Published prose gives a landing
line its own paragraph (50–62% of paragraphs are one sentence) and lets paragraph lengths
vary (CV 87–89%). A manuscript that breaks paragraphs onto a grid — one project book ran 14%
and 51% — has been laid out by something that does not know which sentence deserves the
white space.

### A26: a rule that could not be calibrated from this corpus

`A26` (default name clusters) is in the scanner's WARN-ONLY tier, and it is the only rule
here whose evidence does not come from `corpus/elaina`. It cannot: the corpus is a Japanese
light novel, so it can neither confirm nor deny a list of Western given names, and a name is
not a defect the way a phrase is — a real surname, or a name with cultural grounding, can
legitimately hit the list. Language models, however, reliably sample names from probability
peaks, and that behaviour is documented per model family in published research.

What validated it here is the AI-written control rather than the human one. Coldbrook
Junction contains **Aiden ×19** and **Okafor ×7** — one from each of two documented model
clusters. The three project books contain none. It warns, it never fails, and a hit is a
question for a human: *is this cast drawn from somewhere, or sampled?*

`U3` is deliberately distributional. One chapter with a rhetorical close is a choice; six
out of eleven is a machine habit, and no per-chapter rate can tell those apart.

### The trap this gate set for itself

The first thing it caught was this project: a real, finished, gate-passing manuscript that
failed `U1` and `U3`. It served as the positive control until it was fixed. It no longer
can: a control whose subject changes stops being a control. The uniform case is now
**synthesised** at run time — one published chapter sliced into six even pieces, uniform by
construction at any future date — and the project books are no longer controls at all.
See `validate-controls.sh` control 5.

### U6 — the signature frame, and the word that had to come out of it

`U1` and `U3` measure the SHAPE of a book. Neither can see the failure that is easier to
describe and harder to prove: a book whose chapters are individually fine but which keeps
reaching for the same construction, so the tic stops being a style and becomes a
fingerprint. One instance per chapter is a low rate in every chapter; the tic lives only in
the pattern across chapters.

`U6` counts, for each of a short list of distinctive frames, how many chapters contain at
least one instance, and fails when any frame appears in more than 40% of them.

| frame | published volumes | project book A | project book B | project book C |
|---|---|---|---|---|
| stall (`I want to be X`) | 0 / 0 / 0 | 3 / 15 | **9 / 11** | **10 / 11** |
| frame-opener (`Here is what`) | 0 / 0 / 0 | 3 / 15 | 5 / 11 | 2 / 11 |
| coda-link (`which is why`) | 0 / 0 / 0 | **6 / 15** | 1 / 11 | 1 / 11 |
| refrain (`That is the thing/all`) | 0 / 0 / 0 | 1 / 15 | 5 / 11 | 2 / 11 |
| antithesis (`not X. It was Y.`) | 0 / 0 / 0 | **13 / 15** | **6 / 11** | **8 / 11** |

The published maximum for any frame in any volume is **23%** (`Nobody X` in one volume),
and the other two volumes put no frame above 20%. The floor is set at 40%.

**`Nobody X` was in the first draft of this list and was removed.** It fired on project
book C in 10 of 11 chapters, and it was not measuring a tic at all: being unnoticed is that
book's subject, and a theme realised in diction clusters in every chapter that touches it.
Left in, the rule would have pushed the author to stop writing the word the book is about.
The judgement is that a frame is a **construction** and not a content word, and it is
recorded here because that line is the whole difficulty of this rule.

### The tic this was built for

It was built because a reader of the finished books reported, correctly, that they "use the
identical rhetorical tic at a very similar rate" and that "keeping everything so consistent
is basically AI already". The measurement above is that complaint, quantified. What the
reader heard across two books in different genres was the anti-thesis frame in 87% of one
book's chapters and 73% of another's, the same coda-link in 40%, and one narrator stall in
91%. None of it was visible to any per-chapter rule, and all of it was visible at once.

### Fixing the books did not move the caps

After the manuscripts were re-chaptered and the frames varied, the corpus numbers did not
change and no threshold was touched. Only the books moved:

| | before | after |
|---|---|---|
| book A chapter-length CV | 3.2% | **45.2%** |
| book A worst frame | antithesis 87% | coda-link 40% (warn) |
| book B chapter-length CV | 5.8% | **40.7%** |
| book B worst frame | stall 82% | stall 36% (warn) |
| book C chapter-length CV | 10.8% | **40.0%** |
| book C worst frame | stall 91% | stall 36% (warn) |

---

## 8. The drift gate (`check-drift.py`)

`check-uniformity.py` fails a book whose chapters are too ALIKE. This one fails a book
that stops being like itself, which is the opposite failure and the one the published
guidance on AI-assisted books names explicitly: *"if chapter 1 sounds polished and personal
but chapter 3 turns into bland generalities, someone likely used AI to finish the draft."*

Per chapter it computes a stylometric vector — mean and spread of sentence length, a
rarefied type-token ratio on a fixed 1,000-token window, dialogue share, commas per
sentence, mean paragraph length, one-line paragraph share, dashes and semicolons per 1k,
and the relative frequencies of fifteen function words. The step is the **RMS Cohen's d**
between the first half of the chapters and the second, per feature, pooled within halves.

Raw z-scores were tried first and abandoned. Summing `|z|` across ~23 features returns 10
or more for a single author's own volume, because the sum accumulates each feature's
ordinary chapter-to-chapter noise. Dividing by the pooled within-half spread removes that
floor, so a feature only counts when it moves further than it normally moves inside one of
the halves.

| document | RMS Cohen's d |
|---|---|
| published volume 1 (17 ch) | 0.58 |
| published volume 2 (18 ch) | 0.49 |
| published volume 5 (13 ch) | 0.80 |
| project book A (15 ch) | 1.26 — warn |
| project book B (11 ch) | 0.98 |
| project book C (11 ch) | 0.90 |
| *fixture: published half + Coldbrook half* | **2.73 — FAIL** |
| *fixture: project half + published half* | **2.34 — FAIL** |

**The cap is 1.40, and it is deliberately not tight.** Three published volumes are not
enough to set a tight boundary, and a false accusation of voice drift is worse than a
missed one, because the remedy is rewriting a book. The cap therefore sits at 1.75× the
worst published volume rather than just above it, and it is expected to WARN on books that
are merely uneven. 1.2 is not a verdict; 2.4 is.

The advisory trend row reports the largest Spearman correlation between a feature and
chapter position. It is a **warning band and never a failure**, because the published
maximum (ρ 0.69) sits too close to what a well-behaved project book returns for a failure
threshold on it to be honest.

Project book A does carry a real, slow drift — mean sentence length rising from 17.7 to
21.4 words across the two halves, ρ +0.81. That is recorded as a warning and not as a
defect: the book's late chapters are about institutions rather than people, longer sentences
are a defensible response to the material, and the reading is 1.26 against a cap of 1.40.

---

## 9. Four bugs found while fixing the books

All four were in the direction of the gate being **less** able to fail than it claimed.

**`F1` never once read the paragraph it was named for.** The closing-coda check splits the
chapter into paragraphs with awk's paragraph mode (`RS=""`), and on a CRLF file every blank
line contains a bare `\r` that awk does not treat as empty. The whole chapter therefore
collapsed into a single record and `F1` grepped the ENTIRE chapter for a coda phrase instead
of the closing paragraph. Every CRLF chapter failed; no LF chapter did, which is why it read
as a real finding on two books and was one on neither. Six chapters were reported as closing
on a coda. None of them did. Fixed by stripping `\r` before awk rather than after.

**The project books carried the boilerplate in the manuscript.** Fourteen chapter files
began with `<!-- Phase 3 draft, chapter N. Untitled (titles deferred). Status: first pass. -->`.
The EPUB builder strips comments, so it never reached a reader, but the front matter the
reader had complained about was still sitting in every source file, and the word
*untitled* was in a book whose chapters have titles. Stripped.

**`check-drift.py`'s first threshold was wrong and the corpus said so immediately.** The
initial cap (6.00) was set from an assumption rather than a measurement, and all three
published volumes blew past it — 9.3 to 13.0 — which is what a bad metric looks like from
the inside. The metric was replaced and the cap re-derived from the numbers above.

**`check-uniformity.py` could be blinded by a subdirectory.** Its `resolve()` picked the
chapters directory by testing `CHAPTER.search()` against one newline-joined listing of the
folder. `CHAPTER` is end-anchored and was compiled without `re.M`, so `$` could only match
at the very end of that string — which made the gate's ability to find a book depend on
whichever entry `os.listdir` happened to return last. Moving the writer self-reports into
`chapters/reports-pre-rechapter/` was enough to make it report **"no chapters found"** on a
manuscript it had checked a minute earlier. Fixed by testing each entry. Found because the
fix to the report files was a directory, which is exactly the kind of ordinary change this
kind of bug waits for.

---

## 10. What is still not covered

- **The per-chapter scanner still fails all three project books**, on `A25` (antithesis
  density inside a chapter), `D1` (em dashes, 10–17/1k against a cap of 10), `D2` (rule of
  three), `D3` (-ly adverbs) and `P1` (anaphora). `U6` reduced the *cross-chapter* spread of
  the antithesis; it did not remove every instance, and inside a single dense chapter
  there are still more than 1 per 2,000 words. This is unfinished work, not a passed gate,
  and it is recorded here rather than quietly left out.
- **D1 is the cap most likely to be wrong for this register.** It is governed by a
  translated light novel, and the note in section 1 already concedes that the resulting cap
  is looser than native-English KDP prose would justify. Three books of essayistic
  non-fiction running above it is evidence *for* that concession, not against it — but the
  cap has not been re-derived, because doing so needs a non-fiction corpus that this project
  does not have.
- **`U4` and `U5` are scoped to narrative prose** (`positioning: nonfiction` in
  `PROJECT_STATE.yaml` downgrades them to advisory). The corpus they were derived from is
  narrative fiction, and paragraph shape is genre-dependent in a way the other rows are not:
  dialogue manufactures one-line paragraphs, and an argumentative chapter has no reason to.
  A non-fiction corpus would let the scope come off. None was sourced — three public-domain
  candidates were downloaded, and all three turned out to use a Gutenberg line-break format
  that makes paragraph structure unrecoverable, so the attempt is recorded as failed rather
  than quietly dropped.

---

## 7. Re-deriving, if the corpus changes

```bash
cd tools/calibration
# 1. extract the epubs to plain text (one file per spine document)
python extract.py "<book>.epub" corpus/<name> <tag>
# 2. measure metrics and per-rule hit rates (afterword/appendix auto-excluded)
python measure.py corpus/elaina "<native control dir>" > calibration-report.txt
# 3. targeted greps decide hard-vs-capped: anything with 0 hits can be hard
grep -ohiE "<candidate pattern>" corpus/elaina/*.txt | sort | uniq -c | sort -rn
# 4. re-validate all five controls after any cap change (exits nonzero on failure)
bash ../validate-controls.sh
```

`measure.py` holds the **pre-split** rule families, so it measures rule groups as a
whole. The hard/capped split for individual phrases comes from step 3, not from it.

`validate-controls.sh` is the gate's own check: it re-runs the human, positive and
AI-written controls for the per-chapter scanner, the published-volume and machine-uniform
controls for `check-uniformity.py`, and the published-volume and two-voice controls for
`check-drift.py` — seven in all — and refuses to report success unless every one behaves as
the method predicts. The validation corpus is **not shipped with the tools**: it is
published commercial prose. `validate-controls.sh` exits 2 with a clear message when no
corpus is installed, so an un-run control can never be mistaken for a passed one.
