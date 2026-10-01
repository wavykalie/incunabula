# Scanner calibration record

How the thresholds in `tools/deslop-check.sh` were set, what evidence they rest on,
and what the scanner still cannot do.

Previously the caps were invented. They were also actively wrong: the old em-dash
cap (4 per 1,000 words) failed **36 of 51** published chapters of the reference the
book is meant to sound like. A gate that rejects published human prose is not a
gate, it is noise.

---

## 1. Corpora

### 1a. The primary corpus (unchanged)

### 1b. A second, native-English commercial corpus

Three L.M. Montgomery novels, 1923–27, 270,149 words, at `corpus/montgomery/`. The first
native-English **commercial narrative** in this project — see section 11, which is the whole
of what was done with it and what it changed.

Its limits, stated once and repeated wherever it is used: **one author, three books in a
series, a century old, and a distinctive lyrical stylist.** n=1 author. It is a cross-check
that can *refute* a rule; it is not a basis for *setting* one. Where the two corpora
disagree, the correct reading is "this rule is corpus-dependent", and in every case examined
that is what turned out to be true.

## 1. Corpus (primary)

| Corpus | Documents | Words | Role |
|---|---|---|---|
| *Wandering Witch: The Journey of Elaina*, vols. 1/2/5 (Yen Press) | 48 | 175,144 | **governing** — the register this book targets |
| *Hollow Bridge*, chs. 1–11 | 11 | 56,144 | native-English control |
| **Combined** | **59** | **231,288** | |

Elaina's afterword and appendix files are excluded: they are non-fiction back
matter, and including them inflates rates for prose that is not narrative.

The exclusion is enforced in the tooling (`measure.py`, and the two-control runner
in `tools/validate-controls.sh`), so the record and the measurement cannot drift
apart again. Every number below comes from one run of
`measure.py corpus/elaina`, saved to `calibration-report.txt`.

### Two properties of this corpus that limit it

**Hollow Bridge cannot calibrate dashes or quotes.** It writes dashes as `--` (22 of
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
3.6/1k, and Hollow Bridge (the AI-written control) runs 5.5–5.8/1k in chapters 2 and 3,
so 5/1k is the smallest round allowance that separates them. An earlier revision
of this record put the D2 worst document at 5.8 and set the cap at 7; 5.8 was never
a human document — it was Hollow Bridge chapter 3, read off the wrong control. Fixed.

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
| A17 invented label | 0 | — | nothing — it only fires on Hollow Bridge, which is the guard working |
| A22 excluded-book residue | 4 | 0.91 | **only Hollow Bridge**, the excluded book — the guard working |

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
| Hollow Bridge, 11 final chapters | AI-written, published | should not all pass | **9 FAIL, 2 pass** |

The Hollow Bridge result is the useful one. It is a published book written by this same
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
"genuine tells" in Hollow Bridge — a 10× repeat of *"it was"*, two *Not X. Not Y.*, a
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
- **"Machine prose is lexically impoverished."** Not a limitation of this scanner's TTR, which
  is merely confounded — it is backwards, and the popular advice built on it ("swap buzzwords
  for concrete words" as a humanising fix) is therefore aimed at a real problem in the wrong
  place. VERMILLION measures machine prose as *more* lexically varied than the human corpus:
  moving-average TTR at AUC 0.739 and Yule's *K* at 0.615, both favouring the machine side, and
  the single most diverse machine text out-varied all 140 novels. Machine prose is not short of
  words. It is long of them without needing them. Do not add a lexical-variety rule here, and
  treat any inherited "vary your vocabulary" instruction as unevidenced on narrative prose.
- **Word- and phrase-level candidates** — *in the world of*, spectral/dark-imagery vocabulary,
  vague attribution (*some say*, *many believe*), hedging openers, and the
  *utterly / entirely / absolutely* register — measured **≤ 0.02 per 1k in BOTH corpora**.
  Already covered by `A1`–`A25`, and the project books do not trip them.
  Two of these have independent large-scale confirmation, and not the sign that is usually
  assumed: VERMILLION's sensory-density cue runs at AUC 0.672 for the **machine** side (machine
  prose is *more* sensory-laden, not less), and its imprecise-abstraction cue carries no signal
  at all (p = .16). Both are register-dependent, which is why they are absent from this rule
  set rather than set to zero.

The pattern across all of these is the same one, and it is the reason this section is worth
more than any rule in it: **the measures that survive are the ones about local syntax, and the
measures that fail are the ones about register convention.** Sentence openings, clause
moulds, punctuation variety and structural repetition all transfer from policy prose into
fiction. Word choice, paragraph convention and social scale do not. Any future rule proposed
here should be able to answer which of those two it is.

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

### U4/U5 are a convention, and one of them was measured the other way

Both rows above read as statements about English prose. They are statements about **one
corpus**, and an independent measurement of a much larger one contradicts the direction of
`U4`.

VERMILLION (`vermillion-study/`, this repository) compared 140 public-domain English novels
— 13.04M words, 94 authors, five eras, seven genre strata — against 185 machine-generated or
machine-assisted texts, with controls for genre, period and document length. Its
short-paragraph-frequency cue separates the corpora at **AUC 0.715 for the machine side**:
in that data, machine prose carries *more* one-line paragraphs than human prose.

Both measurements are correct about their own corpora, and the gap between them is the
useful part:

| | human corpus | machine corpus | period |
|---|---|---|---|
| this project (`U4`) | 50–62% one-sentence paragraphs | 14% (Hollow Bridge) | current commercial fiction |
| VERMILLION (cue L) | 19th-c. novels, below the convention | Royal Road serialisation, above it | 2020s web fiction |

`U4`'s floor is a property of **dialogue-dense commercial fiction sold into the current
market**. The control corpus is a translated Japanese light novel, which is dialogue-heavy by
construction and which markets on the same beat-per-line convention. That is a real
convention and this project should keep writing to it — the thresholds stay exactly where
they are. What must not happen is the row being quoted as a rule about prose, because
outside that market a book can sit at 20% and be entirely human. VERMILLION's own Finding 2
is the general form: cues that depend on register and format convention do not travel, and
a threshold inherited from one register is a measurement of that register.

`U5` is the row that survives the cross-corpus test. Paragraph-length variation is not
genre-dependent in any corpus measured so far — the machine side is the flat one everywhere,
because a model has one setting and holds it. **Variation is the human signature; the
one-line share is a house style.** `U5` is the transferable rule, `U4` is the market rule,
and the gate now says which is which at the point of use rather than in a file nobody opens
twice.

### U4 is advisory by default, and `U5` is the proven row

The claim above was worth more measured than cited, so it was measured. VERMILLION's corpus
of 140 public-domain English novels — 13,061,961 words, 94 authors, five eras — is in this
repository, and its files turn out to be blank-line separated with fully recoverable
paragraph structure. `calibration/measure-pd-corpus.py` runs `check-uniformity.py`'s own
arithmetic over it (same splitters, same per-chapter-then-averaged aggregation, chapters of
~3,000 words, because whole-novel variance is a different quantity and would look like
corroboration without being it):

| row | this corpus | 19th-c. English novels | verdict against current gates |
|---|---|---|---|
| `U4` one-sentence share | 50–62% | min 11.0 · q25 27.0 · **median 33.2** · q75 39.3 · max 77.9 | **82 of 140 FAIL (59%)** |
| `U5` paragraph-length CV | 87–89% | min 57 · q25 88 · **median 101** · q75 113 · max 189 | **0 of 140 FAIL**, 14 warn |

`U4`'s **median** on the human canon is 33.2%, which is *below its own 35% FAIL line*. The
five lowest are 11.0, 12.3, 13.4, 13.6 and 14.0 per cent — real novels, in the tens of
thousands of words, that the current gate would fail. Half the corpus sits under the 50%
warn line. A row that fails three novels in five is not measuring a defect; it is measuring
an era.

`U5` returns the complement, and it is the cleaner result of the two: **not one of the 140
novels falls below the 55% FAIL line**, and only 10% reach the warn line at all. Across five
eras and 13M words, flat paragraph layout never once appeared in human prose. That is what a
transferable rule looks like, and it is the same shape as VERMILLION's own burstiness null
(p = .72) — variation survives every control, sameness never does.

Neither threshold was changed, and neither should be. This corpus is not the register the
pipeline sells into, and the era confound runs in a known direction: paragraph-breaking
practice moved across the twentieth century, and VERMILLION's period control shows human
sentence length falling from 37.7 words pre-1830 to 15.9 post-1939. Later prose breaks more.
Re-deriving `U4` from this corpus would replace one convention with another and lose the
market signal that makes the row useful.

What the measurement does establish is enough, and it changed the gate:

- **`U4` no longer fails anything by default.** Its median on the human canon is below its own
  failure line, so a gate that fires on it fires on three novels in five — and a false
  accusation here is not free, because the remedy it suggests is to inject one-line
  paragraphs into a book that does not want them. The number is still printed, both known
  conventions are printed with it, and the reader judges. A book that wants the market row
  declares `paragraph_convention: commercial-dialogue` in `PROJECT_STATE.yaml` and gets it
  enforced exactly as before. **The burden of proof moved to the book.**
- **`U5` stays enforced**, and it is now the row with the strongest evidence in this file:
  0 failures in 140 novels, 13M words, five eras, corroborated independently by VERMILLION.
  Flat paragraph layout is the transferable tell. The one-line share is a house style.

**An automatic trigger was tried and rejected on evidence, and the rejection is recorded
because the tempting version of this fix is a bug.** The obvious mechanism is that dialogue
manufactures one-line paragraphs — the reasoning `CALIBRATION.md` has carried since the row
was written — so the gate could scope itself to books with enough of them and enforce
everywhere else. Measured across the same 140 novels, the correlation between the share of
paragraphs that are *entirely* a speech span and the one-sentence paragraph share is
**r = 0.234**. Speech density does not predict the row. The 19th-century canon is
dialogue-sparse and still reaches 77.9%.

So the stated reason for the 50–62% band turns out not to be its reason, and a cut point
placed on that basis would have been invented. The README's rule — never set a threshold
from a number you have not measured — forbids it, so the row is advisory and a human
declares. The explanation in this file and in the old docstring is wrong in its mechanism and
right only in its conclusion, which is the more interesting failure: a plausible causal
story survived years of reuse because nobody had a second corpus to check it against.

Note also what VERMILLION measured and this project had already recorded independently: its
within-window sentence-length burstiness is **identical** to the human corpus (p = .72), and
its finding is that the flattening is *across* documents. That is the same conclusion as the
"burstiness" rejection above, reached by a different method on 13M words. `U2` was right.

### A26: a rule that could not be calibrated from this corpus

`A26` (default name clusters) is in the scanner's WARN-ONLY tier, and it is the only rule
here whose evidence does not come from `corpus/elaina`. It cannot: the corpus is a Japanese
light novel, so it can neither confirm nor deny a list of Western given names, and a name is
not a defect the way a phrase is — a real surname, or a name with cultural grounding, can
legitimately hit the list. Language models, however, reliably sample names from probability
peaks, and that behaviour is documented per model family in published research.

What validated it here is the AI-written control rather than the human one. Hollow Bridge contains **Aiden ×19** and **Okafor ×7** — one from each of two documented model
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

**Correction, 2026-09-29 — this table is the origin of a wrong claim, and it is kept
because it shows how the wrong claim was made.** The `before` column is the drafting. The
`after` column is the *same prose* re-partitioned into more chapters, which is what the
sentence above the table already says. That was known here and not carried forward: the
`after` numbers were later cited in `DRAFTING_FRAMEWORK.md` as books "drafted with no
length targets," which inverts the cause.

The Merope manuscripts were drafted to a declared 7 × ~2,450 words. 97–99% of every
re-partitioned chapter is verbatim original prose and the totals hold to within 0.5%;
cutting the archived draft to the new chapter sizes reproduces 41.0% and 39.9% exactly
with nothing written. The re-chaptering was a legitimate repair of a real defect — the
`before` column shows genuine clumping — and it worked. What it does not show is that
drafting without targets produces spread. Full measurement in `ERRATA.md` 2026-09-29.

No threshold in this file derives from these three books, so nothing here is recalibrated.

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
| *fixture: published half + Hollow Bridge half* | **2.73 — FAIL** |
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

### The arc gate (`check-arc.py`, rows `A1`–`A4`)

`A1` is the only row in this directory calibrated on a **second, independent corpus**, and it
is the only one that earned its gate that way. The other three gating rows come from a
translated light novel; `A1` comes from the 140 public-domain English novels in
`vermillion-study/corpus`, measured with `check-arc.py`'s own code:

| reversals per bin | n | min | p25 | median | p75 | max | sd |
|---|---|---|---|---|---|---|---|
| human | 140 | 0.469 | 0.555 | 0.575 | 0.590 | 0.672 | 0.031 |
| machine | 83 of 153 | 0.256 | 0.433 | 0.502 | 0.577 | 0.768 | 0.105 |

The human row reproduces VERMILLION's published distribution **to three decimals** — min
0.469, p25 0.555, q75 0.590, max 0.672 against its published 0.469 / 0.555 / 0.588 / 0.672.
That agreement is the check that the tool computes the quantity its threshold was derived
from, and it is why the study's human figures are corroboration here rather than a borrowed
number.

`A1` gates at **fail under 0.45, warn under 0.50** — below the worst human novel measured,
with headroom. At 0.45 it flags 27% of the measurable machine corpus and **zero of the 140
human novels**.

**The null is 0.5, and that is the finding.** A curve of independent steps reverses direction
about half the time, so 0.5 is this metric's null, not its floor. Read against it:

    human prose    0.571   measurably ABOVE the null
    machine prose  0.501   on the null exactly

Human arcs change direction more often than noise would produce; machine arcs are
statistically indistinguishable from a random walk. That is a sharper claim than "machine
prose reverses less often" — the second compares two distributions, the first says what one of
them *is*. And a book below 0.45 is not merely flat, it is **smoother than noise**, which is
the failure no amount of sentence-level variation fixes.

Human reversal rate is also era-independent (VERMILLION's per-era means span 0.565–0.575, a
spread of 0.01 over five eras), which is what a threshold needs and what `U4` lacked.

**Four bugs, all found by measuring the implementation that ships rather than trusting a
published number.** Each is recorded because each would have shipped:

1. **The lexicon was silently truncated.** The valence word lists were transcribed by hand
   into `check-arc.py` and 53 of the 143 negative words were dropped — among them *cold*,
   *tired*, *hungry*, *war*, *fate*, *sick*, *danger*. That inflated the positive share,
   roughly doubled the measured arc range, and moved the human reversal mean by 0.077. The
   lists are now asserted at import (`len(POSITIVE) == 121`,
   `len(NEGATIVE) == 143`) so a re-transcription cannot pass silently. VERMILLION's line
   about the lexicons being the instrument is not a philosophical caution; it is a
   description of this bug.
2. **The tokenizer differed.** A naive `[a-z']+` splits `well-known` into `well` + `known`,
   and *well* is in the positive list, so every hyphenated compound became a false positive.
   The study's `WORD_RE` — a leading `[A-Za-z]` and a hyphen inside the class — is now used
   verbatim. Fixing this moved the mean by 0.001, which is worth knowing: the lexicon, not
   the tokenizer, was the real error.
3. **The measurement window was wrong, and this is the one that mattered.** `check-arc.py`
   originally computed ONE curve for a whole novel. VERMILLION computes the arc **per
   4,000-word window, on paragraph boundaries, and takes the mean over windows** —
   `engine.py` sets `WINDOW = 4000` and its `aggregate()` is documented as "Mean over
   windows". The single-curve version reads about **0.08 higher on every text**, which is
   enough to move a threshold while looking entirely plausible. The cause was isolated only
   after the lexicon and the tokenizer were both ruled out, and it was found by *reading
   `engine.py`* rather than by more measuring. Its `windows()`, `SENT_RE` and `ABBREV` are now
   copied verbatim and the result matches to three decimals. A gate whose calibration cannot
   be reproduced is a gate nobody can re-derive; the fact that this one could be is the only
   reason the discrepancy was chased down instead of documented away as a limitation.
4. **The study's machine figures are not comparable to ours.** That corpus passed through a
   Royal Road boilerplate filter (`strip_rr_notice`, removing anti-piracy notices injected at
   arbitrary positions mid-scene) that this directory has no equivalent of. The machine row
   above is therefore **our own measurement of 83 of 153 texts** — 70 are single-chapter
   serials with one window and are reported **unmeasured, not passing**. A short book gets no
   verdict from this row at all, which is a real coverage limit of a method whose unit is the
   window.

**What `A1` is not.** It is not a detector, and the evidence is this project's own control:
**Hollow Bridge, written by a model, scores 0.533 — inside the human range and above the
warn line.** A competent machine-assisted book passes. The machine corpus's maximum (0.768)
also exceeds the human maximum (0.672), so a high reversal rate is no defect either, and the
row is one-sided on purpose. Arc *range* separates the corpora more sharply (human median
0.084, machine 0.050) and is reported as `A2` but **not gated**, because range tracks how
adjective-dense a register is and 19th-century narration is far denser than commercial
fiction — gating it here would be measuring the century.

A synthetic monotone-arc fixture was built to confirm the gate can fail, because a gate that
never fires proves nothing. It fails, and `A3` correctly labels it *trending*.

## 13. The unit check, applied to the other two gates

§12 found the density caps calibrated on documents and enforced on chapters. The same
question asked of the other two gates gives one severe answer and one mild one — and both
are the same mistake, because in every case a threshold was derived on one unit and
enforced on another.

### `check-drift.py` — severe, and it inverts into false accusation

`DRIFT_FAIL` (1.40) was calibrated on three published volumes of **13, 17 and 18 chapters**.
The gate splits a book in half *by chapter count* and takes Cohen's *d* between the halves,
so the score is a function of how many chapters the estimate rests on. `drift-units.py`
holds the text, the author and the voice completely fixed and varies only the chapter
count, slicing 30 published novels into fixed numbers of chapters:

| chapters | median drift | over the 1.40 cap |
|---|---|---|
| 4 | **2.99** | **30 of 30 (100%)** |
| 6 | 1.54 | 20 of 30 (67%) |
| 8 | 1.23 | 6 of 30 (20%) |
| 10 | 0.98 | 2 of 30 (7%) |
| 12 | 0.92 | 2 of 30 (7%) |
| 16 | 0.79 | 0 of 30 (0%) |
| 20 | 0.69 | 0 of 30 (0%) |

Correlation between chapter count and score: **r = −0.777**. Four chapters read 2.30 higher
than twenty, on identical prose.

**A four-chapter published novel fails this gate 100% of the time.** `MIN_CHAPTERS = 4`
admits exactly the size that fails. And the failure is expensive rather than harmless: the
docstring's own remedy for a drift failure is *rewriting the book*, and this evidence is
thin — a reading of 1.2 is not a verdict, per the file itself.

The honest fix is a size-dependent floor, or a minimum chapter count above 4. Neither is
applied here, because both are decisions about published prose and `PRINTERS_COPY.md` §7
requires a person to make them. The measurement is what §7 asks for.

### `check-arc.py` — real, milder, and confined to short books

`A1`'s floor (0.45) comes from the **mean over ~15 windows** of a full novel. A short book
contributes one or two. `arc-units.py`, using the gate's own lexicons and windowing over
1,193 windows from 40 published novels:

| | mean | sd | min | median |
|---|---|---|---|---|
| per-novel mean | 0.569 | 0.035 | **0.469** | 0.577 |
| per-window | 0.574 | **0.104** | **0.000** | 0.579 |

The floor sits 0.019 below the worst novel mean and **0.450 above** the worst single
window. **12.7% of individual windows fall below the floor; 0 of 40 novel means do.** Of
those 151 windows, 147 are well-formed (10–19 bins) — genuinely monotone stretches of
published narration, not degenerate three-bin artefacts.

`arc-short-book.py` then runs the **actual gate** on real published prose written to real
chapter files, varying only book length:

| book length | windows | median A1 | below 0.45 |
|---|---|---|---|
| 2,000 words | — | unmeasured | gate declined all |
| 4,000 words | 2 | 0.486 | **3 of 15 (20%)** |
| 8,000 words | 3 | 0.539 | 1 of 20 (5%) |
| 16,000 words | 5 | 0.525 | 2 of 20 (10%) |
| 32,000 words | 12 | 0.536 | 0 of 10 (0%) |

So a novel-length book is clean and a 4,000-word book fails a fifth of the time. This is
the same defect the arc section already half-knew — it records that short books are
*unmeasured* — but the recorded limit was too generous. A short book is not unmeasured; it
is measured noisily, and it is measured wrongly. The null (0.500) is also crossed by 6.6%
of single windows, so the "smoother than noise" claim does not hold for a one-window book
either.

## 14. Size-dependent floors, and what they cost

§13 found three gates whose thresholds were derived on one unit and enforced on another.
The fix is a threshold that moves with the sample — and the first question is not "what
should the number be" but "can a size-dependent number be trusted at all", because a floor
that rises for short books can rise *above* a real defect and silently disable the gate.

### The positive control has to be measured too

`size-floors.py` therefore measures **both arms** at every size, on 40 published novels:
one voice sliced to N chapters (must never fail) against half novel A + half novel B (a
real voice change, must always fail).

**The 1.5× headroom convention cannot be used here.** The two arms *overlap at every
chapter count tested* — `neg max ≥ pos min` from 6 chapters to 20. So 1.5× the worst
clean book sits above the weakest real voice change, and a floor built that way stops the
gate firing. An intermediate 24-book run appeared to show separation at 10, 16 and 20
chapters; at 40 books it vanished. That earlier reading was small-sample noise and was not
acted on.

What separates the arms is the body, not the tail: `pos median ≈ 2× neg p95` at every
size. So the floor is set from the **negative arm alone** — worse than any published book
of this size — and the price is recorded rather than buried:

| chapters | floor | two-voice books caught |
|---|---|---|
| 4 | 3.41 | 12/12 |
| 6 | 3.41 | 10/12 |
| 8 | 2.47 | 11/12 |
| 10 | 1.94 | 11/12 |
| 12 | 1.73 | 11/12 |
| 16 | 1.60 | 11/12 |
| 20+ | 1.40 | 10/12 |

**92–95% detection, zero false failures on published books.** The guarantee bought is
*"never fails a clean book"*, not *"always catches real drift"*, and that is a weaker
guarantee than the rest of this directory's caps. It is labelled as such in the source.

### `WINDOW_FLOOR` for the arc gate

The lowest published mean at each window count, over the same corpus:

| windows | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|
| lowest published mean | 0.333 | 0.382 | 0.439 | 0.485 | 0.469 |

So the shipped 0.45 is correct **from 4 windows up** — exactly what the full-novel
derivation implied, and nobody had checked. Below that it was too high: a one-window
published book reads as low as 0.333. `WINDOW_FLOOR` is 0.30 / 0.35 / 0.41 / 0.45.

### A fixture that had never existed

`CALIBRATION.md` had claimed for some time that a synthetic monotone-arc fixture proved
the arc gate fires. It was built ad hoc and **never kept**, so the claim could not be
checked. Rebuilt from scratch it scored **0.566 and PASSED** — a fixture built to prove the
gate fires, passing.

The cause is worth recording because it is the same shape as every other bug in this
section: `curve()` bins at 200 words, so a monotone decline has to be monotone **across a
bin**. Spread over 420 sentences, each bin moves far less than its own sampling noise, and
every step changes sign at random. `make-arc-fixture.py` is now committed, seeded, and
documented at the constants that make a bin steeper than its noise. It fails at 2 windows,
which also demonstrates that the new low-window floor still catches a real monotone arc.

## 11. The hard tier did not survive a second corpus

**The corpus.** Three L.M. Montgomery novels — *Anne of Green Gables*, *Anne of Avonlea*,
*Anne of the Island*, 1923–27, **270,149 words** — were sitting unused in
`_archive/tests/book-genesis-anne-series/source/`. They are the first **native-English
commercial narrative** in this project: not a translation, not public-domain literary
prose, not one of our own books. They are now at `corpus/montgomery/`.

**What they are not.** One author, three books in a series, a century old, and L. Montgomery
is a lyrical stylist with a distinctive and unusually low rate of the things being measured.
n=1 author. This is a **cross-check**, not a re-derivation, and no cap below was moved on its
strength alone.

### What it confirmed

| row | Montgomery (270k words) | verdict |
|---|---|---|
| `D1` | 9.1/1k worst (cap 10) | passes |
| `D2` | 1.3/1k worst (cap 5) | passes |
| `D3` | 16.7/1k worst (cap 26) | passes |
| `A24`, `A25` | 0.0 and 0.1/1k | pass |
| `U5` | 97, 101, 105% (fail under 55) | third independent confirmation |
| `U4` | **31.7, 39.5, 41.0%** — all at or under the 35% fail line | see below |
| `A1` | 0.562, 0.607, 0.574 (floor 0.45) | third independent confirmation, on the human median |
| mean sentence | 20.7–26.0 words | squarely human (machine corpus: 13.0) |

**`U4` is the important one.** Native-English *commercial* fiction sits at 31.7–41.0%, the
same place the nineteenth-century canon did (median 33.2) and nowhere near Elaina's 50–62%.
Two corpora of completely different era and genre agree: **the 50–62% band belongs to
dialogue-heavy light-novel translation, not to commercial fiction.** That is independent
confirmation of the decision to make `U4` advisory, from a corpus that matches the target
market on register.

### What it broke: five hard rules, every hit a false positive

`A1a`, `A2a`, `A3a`, `A19` and `A21` were all HARD, justified in the source as "published
prose: 0". That justification came from **one** corpus. Here is every hit, in full:

| rule | hits | what it actually matched |
|---|---|---|
| `A3a` grandiose nouns | 5 | "an **intricate**, headlong brook" · "a **myriad** of bees" · "gold and silver brocade **tapestry**" (a literal wall hanging, twice) · "the **palpable** bids for favor" |
| `A2a` magic adverbs | 3 | "a soul **subtly** akin to her own" · "the **subtly** sweet voices of the night" · "creeping **subtly** and remorselessly" |
| `A1a` delve family | 1 | "her **robust**, matter-of-fact Scotch common sense" |
| `A19` listicle in prose | 1 | "I suppose the first thing is to give your hair a good washing" |
| `A21` chatbot artifact | 1 | "some one should ask her the great question" |

**11 hits in 270,149 words, and not one of them is slop.** `subtly` and `robust` are English.
A *tapestry* on a wall is a tapestry. "The great question" in a romance about a girl
imagining being asked is not a chatbot greeting.

The cause is uniform and it is the one VERMILLION names about its own instrument: **these
lists were assembled by reading modern machine output**, where the words are tics, and then
applied to fiction, where they are not. A word is a tell at a **rate**, not at a presence —
and 11 hits across 270k words is 0.04/1k. The project's own rule already says a hard rule
requires "literally zero hits across the whole corpus", and **one corpus cannot establish
that a word is never used in English fiction.**

**Action taken.** All five moved from `HARD` to a new `DEMOTED` tier at a rate cap, with the
rows tagged `[demoted from HARD]` in the output so the change is visible at the point of use.
Caps are ~50× the worst observed rate, which is loose on purpose: looseness is recoverable,
a gate that fails *Anne of Green Gables* is not. The ten hard rules that **did not** fire were
left alone — changing them would be unmeasured, which is the error this section is about.

The generalisable finding: **hard rules keyed to a word list are unsafe; position-based hard
rules survived.** `F1` (closing coda as a position) and `A8`, `A10a`, `A12`, `A13`, `A20` all
passed a second corpus untouched. It is the lists that were never safe, and one corpus hid it.

### Two bugs this work exposed in our own tooling

1. **`deslop-check.sh` did not strip Project Gutenberg boilerplate.** Licence header,
   transcriber's notes, contents list — 3,045 of the 105,546 "words" in *Anne of Green
   Gables*. `A3a` and `A19` fired inside the header before the strip existed. Any Gutenberg
   corpus was affected, and this project has repeatedly tried to use Gutenberg as a
   calibration source. Fixed at the top of `scan_file`; the displayed filename is unchanged.

2. **A decimal in a warn field silently disabled the whole demoted tier.** The density
   comparison is bash integer arithmetic; `0.5` as a warn numerator threw
   `arithmetic syntax error`, aborted the loop, and the five demoted rows **vanished from the
   report** — which briefly made both project books PASS the scanner. Caught only because the
   change was verified by asking whether a rule that had just been *weakened* still appeared
   in the output. It is the fifth bug in this directory that all pointed the same way, and the
   direction is consistent: **the gate reporting itself more capable than it was.** Numerators
   are integers now, and the reason is in the source.

### `P3` moved to warn-only, and why no cap can fix it

*Anne of Avonlea* carries a run of **29** consecutive fragments of three words or fewer — in
the body, not the front matter (its verse dedication reaches a run of 1, because undotted
lines merge into one long sentence). It is a deliberate technique: clipped beats at a
heightened moment.

It is a fair example of *justified inconsistency* — an anomaly a reader can recover because
a motive is available — and it is **not** an example of positional clustering. Those two
claims were conflated here when the run was first found, and the second one is refuted: Gini
across ten position bins is flat in every corpus (see "Justified inconsistency, and the axis
that was supposed to measure it" below). The 29-run is concentrated in *time*, and position
in the document is not time. The `P3` decision below stands on the cap argument alone.

The cap cannot simply be raised, because the slop fixture runs to **9**. A threshold passing
29 also passes 9, so **run length does not separate a deliberate clipped sequence from a
machine tic.** That is a limit of the measure, not a tuning problem, so `P3` now warns and a
person rules — which is how this directory already treats anaphora (*"Anaphora is kept;
accidental repetition is fixed"*). The fixture still fails on 17 other rows.

### A near-miss worth recording

While diagnosing this, a diagnostic script of mine reported that the scanner bans
`said Anne quietly`. **That was wrong** — the scanner's `A2a` is
`fundamentally|arguably|profoundly|subtly`, and I had written a different pattern into my own
probe. I nearly reported a false claim about the project's own rules, in a section whose whole
subject is claims that turned out to be false on contact with a second corpus. The pattern was
re-checked against `deslop-check.sh` before anything was written down. It is the reason the
table above quotes the scanner's verbatim patterns rather than paraphrases.

## 12. Three caps fail real published chapters (the document/chapter unit error)

Every control in this directory so far fed the scanner **whole documents**. The scanner
gates a **chapter**. Those are different units, and nothing in the recorded method
noticed, because a document-level maximum is a smaller rate than the worst stretch
inside it.

`chunk-pd-corpus.py` slices the 140-novel public-domain corpus into ~2,150-word chapters
(6,094 of them), and `chapter-rates.py` reads a scan back. A stride-sample of every 60th
chunk — 102 chapters spanning 84 distinct novels — was scanned:

| rule | cap now | worst published chapter | fails |
|---|---|---|---|
| `D2` rule of three | 5/1000 = 5.00/1k | **8.40/1k** | **19 chapters (18.6%), 19 novels** |
| `D1` em dash | 10/1000 = 10.00/1k | **33.52/1k** | **15 chapters (14.7%), 14 novels** |
| `A25` antithesis | 1/2000 = 0.50/1k | 0.93/1k | 1 chapter (1.0%) |

The other 15 rows pass every chapter. The D1 outlier was checked by hand before being
believed: `158-ch067.txt` is valid UTF-8 holding 71 genuine U+2014 characters in 2,195
words, not a decoding artifact. The failures spread across many novels rather than
concentrating in one, so this is a property of the caps and not of an outlier title.

**Why no cap was changed.** Applying §2's own rule — 1.5× the worst published document —
to the worst published *chapter* gives `D1` 51/1000 and `D2` 13/1000. That is a large
loosening, and the rule was written to give headroom to a *reference*, not to absorb the
maximum of a 19th-century outlier. `D1` additionally has the era confound already on
record: era medians run 2.8–8.7/1k against a cap of 10, and 45% of the corpus spells a
dash `--` rather than U+2014, so a chapter-level maximum in *this* corpus is a worse
basis for a cap than a document-level one.

So the honest state is that the choice — raise the caps, or demote these three to warn —
needs a current multi-author corpus to make, and that is the same procurement gap blocking
every other re-derivation here. Filed in **Open**; nothing gated changed.

## 15. `D1` and `D2` demoted, on the measurement that settles it

§12 left one question open and framed it as a preference: raise the caps to clear
published prose, or demote the rows. It is not a preference. It turns on a measurement
that had not been made — **does the AI control sit above the published distribution at
all?** If it does, a cap exists between them and should be raised to it. If it does not,
no cap can do the job the row exists for, and raising it only buys a row that passes
everything.

`d1d2-decision.py` answers it, from the same scanner, over 102 published chapters and 22
AI-control chapters:

| row | published p50 | published p95 | published max | control p50 | control max | cap | published failing |
|---|---|---|---|---|---|---|---|
| `D1` | 1.17 | 12.33 | **33.52** | 0.00 | **0.00** | 10 | 13.7% |
| `D2` | 3.23 | 6.92 | **8.40** | 4.00 | 5.80 | 5 | 18.6% |
| `D3` | 11.56 | 17.42 | 19.56 | 7.47 | 16.41 | 26 | 0.0% |

**`D1` reads 0.00/1k on every control chapter.** These books spell a dash `--`, so the row
measures the encoding, not the style — the tool's own note says as much, and here it is the
whole finding. `D2`'s control sits at the published median and below the 95th percentile.

So both rows are **report-only**: same caps, same warn bands, same numbers, no ability to
fail. Raising them was considered and **rejected rather than deferred** — a cap that
clears published prose (D1 51/1k, D2 13/1k) also clears every machine book, and a green
result read as evidence is worse than no row at all.

Verified: **0 failures across 31 published chapters**, with `D1` and `D2` still reporting
over-cap numbers (3 and 9 chapters). The slop fixture still FAILS, on 16 other rows.

**`D3` is in the same position and was deliberately not touched.** Its control also sits
inside the human distribution and its cap clears every published chapter, so its value as a
detector is unproven. But it fails 0 of 102 published chapters, so it accuses nobody, and
demoting a harmless rule would be tidying rather than correcting. The distinction is the
actual finding: a cap can be harmless *and* useless at once, and only one of those is worth
acting on.

**The first run of this was contaminated, and the way it was caught is worth recording.**
A full 6,094-chunk scan was started and abandoned on a tool timeout. The pipeline's `awk`
stage survived the kill and kept writing into the same output file for seven more minutes
while a second scan ran on a different sample. The result was a sparse file with
**249,590 NUL bytes**, and `grep -c '^== '` cheerfully reported 302 chapters for a
directory holding 204. The per-rule table it produced looked entirely plausible — and was
wrong in a way no amount of reading would have revealed. Only counting the NUL bytes
exposed it. `chapter-rates.py` now refuses any input containing NUL bytes, or any input
whose header count disagrees with its unique-file count, and both refusals are proven to
fire.

## 10. What is still not covered

- **The per-chapter scanner still fails all three project books**, on `A25` (antithesis
  density inside a chapter), `D1` (em dashes, 10–17/1k against a cap of 10), `D2` (rule of
  three), `D3` (-ly adverbs) and `P1` (anaphora). `U6` reduced the *cross-chapter* spread of
  the antithesis; it did not remove every instance, and inside a single dense chapter
  there are still more than 1 per 2,000 words. This is unfinished work, not a passed gate,
  and it is recorded here rather than quietly left out.- **`D1` measures typography as well as style, and cannot be re-derived from a
  public-domain corpus.** Measured over the 140 public-domain English novels:

  | dash spelling | files containing it | median /1k | max /1k |
  |---|---|---|---|
  | Unicode em dash (U+2014) — **what `D1` counts** | **45%** | 0.0 | 19.7 |
  | double hyphen `--` | 57% | 1.1 | 20.6 |
  | spaced hyphen ` - ` | 5% | 0.0 | 0.3 |
  | **any of the three — the habit** | 100% | **5.8** | **20.6** |

  **55% of the corpus contains no U+2014 at all**, so `D1` reads zero for more than half of
  native English novels that are heavily dash-punctuated. The file simply spells its dashes
  `--`. The record already knew this about one book — Hollow Bridge “writes its dashes as `--` …
  so it scores 0 em dashes as a *formatting* fact, not a style one” — and used it to exclude
  Hollow Bridge from calibrating `D1`. The measurement generalises the same fact to a majority of
  the corpus, and it means `D1` as implemented is partly a rule about how a file was typed.

  On the *habit* rather than the character, the corpus runs median 5.8 and max 20.6 per 1,000
  words, and **24% of native English novels exceed `D1`'s 10/1k cap** — by era: 10% pre-1830,
  14% in 1830–1869, 35% in 1870–1899, 14% in 1900–1939, 28% post-1939. The era spread (median
  2.8 to 8.7) is larger than the cap itself.

  **So the cap does not move, and cannot be re-derived here.** The per-era medians differ by
  more than the cap, which means a nineteenth-century corpus cannot supply a threshold for a
  twenty-first-century commercial target — the same era confound that made `U4` advisory, and
  the reason `README.md`'s “a density cap goes ~1.5× the worst single document” rule cannot
  be applied by borrowing a different century. What was added instead is a **note-only row**
  (`NOTE_DASHSPELL`) that counts any of the three spellings, so a `D1` reading of zero can be
  interpreted rather than believed. It never fails, exactly like the curly-quote row beside
  it and for the same reason: a typography fact is not a style defect, and reporting it as a
  gate would be a rule that cannot see prose.

  The remaining gap is unchanged and still real: **no native-English commercial narrative
  corpus exists in this project.** `epubs/` holds four of its own books. Until one is sourced,
  `D1` stands on a translated light novel, and the cap is documented as the loosest number in
  this file.

### `D2`, `D3` and `A25` were checked the same way, and they survive

`D1` turned out to be contaminated by typography, so the obvious next question was whether
its neighbours are contaminated too. Measured on the same 140 public-domain English novels,
using the scanner's own patterns verbatim:

| rule | cap | human median | human max | over cap | by era (pre-1830 → post-1939) |
|---|---|---|---|---|---|
| `D2` rule of three | 5/1k | 2.9 | 8.0 | **11%** | 21% → 14% → 14% → 4% → **0%** |
| `D3` `-ly` adverbs | 26/1k | 12.3 | 20.0 | **0%** | 0% throughout |
| `A25` antithesis | 1/2k | 0.0 | 0.4/1k | **0%** | 0% throughout |

**This is a negative result and it is worth as much as a positive one.** The light-novel
calibration is not universally broken. Specifically:

- **`D2` is well calibrated for the register this pipeline sells into, and arguably slightly
  loose.** The era trend runs the *opposite* way to the worry recorded elsewhere in this file:
  rule-of-three density **declines** across the corpus (median 3.4 pre-1830 → 1.8 post-1939),
  and not one of the 28 post-1939 novels exceeds the 5/1k cap — the modern human maximum is
  4.0. The cap already sits just above it. The record's standing worry that these caps are
  *too loose* for native English does not apply to `D2`; if anything the modern cap could come
  down, and that would be a re-derivation, not a correction.
- **`D3` and `A25` fail nothing at all.** Worst human `-ly` density is 20.0 against a cap of
  26, and worst antithesis is 0.8/2k against a fail line of 1/2k. Both are in the safe
  direction, and `A25` is tighter than the "1.5× the worst document" rule requires.
- `D3` runs *counter* to the general expectation that modern prose is leaner: post-1939 has
  the **highest** adverb density in the corpus (median 14.2 against 11.0 pre-1830). Any
  intuition that "-ly adverbs fell out of literary English" is wrong for this corpus.

So the contamination is specific to `D1`, and the reason is now clear: `D1` counts a single
Unicode character, while `D2`, `D3` and `A25` count patterns that have no encoding
ambiguity. **The lesson generalises past dashes: any rule keyed to a literal typographic
character is a measurement of the file's encoding as well as its prose.** That is worth
checking before trusting a new character-level rule, and it is the shape of bug the four
already recorded here all share.
- **`U4` and `U5` are scoped to narrative prose** (`positioning: nonfiction` in
  `PROJECT_STATE.yaml` downgrades them to advisory). The corpus they were derived from is
  narrative fiction, and paragraph shape is genre-dependent in a way the other rows are not:
  dialogue manufactures one-line paragraphs, and an argumentative chapter has no reason to.
  A non-fiction corpus would let the scope come off. None was sourced. An earlier attempt
  with three public-domain candidates was abandoned on the stated grounds that they "use a
  Gutenberg line-break format that makes paragraph structure unrecoverable" — **that
  diagnosis was wrong, and the attempt should not have been given up.** The VERMILLION
  corpus in this repository is public-domain English fiction whose paragraph structure
  recovers perfectly well; see "Measured: 59% of the 19th-century canon would fail `U4`"
  above and `calibration/measure-pd-corpus.py`, which runs over 13M words of it. The three
  earlier candidates most likely used line-wrapped prose with no blank line between
  paragraphs, which is unrecoverable, but that is a property of *those* files and not of
  Gutenberg. Non-fiction remains unsourced, and the scoping stays.
- **`check-surplus.py` (`S1`–`S4`) shipped with no corpus at all, deliberately.** It is the
  only tool in this directory that reports without gating, and the reason is that there was
  nothing to gate against: no surplus figure has been measured on published prose, so any
  threshold would have been invented. The rule this project already follows — never set a
  threshold from a number you have not measured — forbids inventing one here, and shipping a
  made-up FAIL line would be worse than shipping a report.

  What it measures, and why the three rows that matter are lexicon-free:

  | row | what it is | standing |
  |---|---|---|
  | `S1` | coefficient of variation of speech-turn word counts | report-only, uncalibrated |
  | `S2` | share of turns of 3 words or fewer | report-only, uncalibrated |
  | `S3` | share of turns of 25 words or more | report-only, uncalibrated |
  | `S4` | instrument / surplus marker ratio | NOTE tier, lexicon-dependent |

  The design constraint was set by VERMILLION's sharpest methodological finding about
  itself: *"the lexicons are the instrument"*, and a different list would give different
  numbers. A surplus measure built from a list of banter-words inherits that problem and
  arrives defended as if it did not have it. Turn-length distribution needs no list and
  measures the same underlying thing — surplus speech produces short exchanges *and* long
  digressions, so it widens the distribution. That is why `S1`–`S3` are the rows and the
  lexicon is not.

  `S1` is deliberately reported **per chapter and then as a spread across chapters**, and the
  spread is the headline. VERMILLION's central result is that machine prose's flattening is
  not local — within-window burstiness matches the human corpus at p = .72 — but
  *across* documents. A book whose chapters all land within a couple of points of one
  another has one tempo for its whole dialogue, which is `U2`'s finding in different
  clothes.

  Two things were got wrong on the first run and are recorded here rather than quietly
  fixed. `S1` was computed on chapters with as few as 8 turns, where the CV of a small
  count swings by tens of points on one long speech span; the floor is now `MIN_TURNS = 20`
  and thinner chapters print as unread. And `S4` originally counted proper nouns as
  instrument hits, which inflated it to 71% — a name in dialogue is far more often a
  vocative than a fact being reported, so the row was partly measuring the cast list.
  Names and digits are now counted and printed separately, and the narrow reading of the
  same book is 57%.

  To promote any of these to a gate: measure the calibration corpus, set the floor below the
  worst published document, and record the number here. Until then, a reader is entitled to
  treat these numbers as a prompt for judgement and nothing more.
- **Justified inconsistency, and the axis that was supposed to measure it.** This is the
  measure VERMILLION names as the one it most wishes it had, and the prototype
  (`calibration/proto-recoverable.py`, shipped tool `check-recoverable.py`) is the first
  attempt in this project to put a number on it. It produced one refutation and one result.

  **The positional axis is refuted.** The study's formulation is that human formal
  irregularity *clusters* — a passage breaks its own rules "at points where a motive can be
  supplied". Measured as the Gini coefficient of tic occurrences across ten equal position
  bins, every corpus is flat: 19th-century human novels 0.02 (em dash) to −0.02 (rule of
  three); Montgomery −0.10 to +0.01; machine texts −0.01 to +0.03. If a tic's position in a
  document carried any of the signal, a flat Gini would not be the result. Whatever "cluster
  where a motive can be supplied" means, it is not position in the text.

  **Register enrichment survives.** For each tic, enrichment = share of its occurrences
  inside quoted speech ÷ the text's own dialogue share, so a dialogue-heavy text is scored
  against its own baseline rather than the corpus's. Medians:

  | corpus | em dash | rule of three | −ly adverb |
  |---|---|---|---|
  | human, 19th c. (137 docs) | **1.75** | 0.78 | 0.67 |
  | Montgomery (3 docs) | **1.49** | 0.68 | 0.57 |
  | machine (120 docs) | 0.79 | 0.42 | 0.70 |

  The em dash is the one tic with a human/machine gap worth 0.7, and it is the one tic the
  human corpora carry in *dialogue* more than their own dialogue share would predict. That
  is a real, directionally-consistent result across three corpora written a century and a
  language apart.

  **The confound test is clean.** Cross-corpus differences are worthless if enrichment
  merely tracks dialogue share, since the machine corpus is 19% dialogue and the human
  corpus 19–31%. Within-corpus Pearson *r* between dialogue share and enrichment:
  human +0.029 (em dash), −0.213 (rule of three), +0.277 (−ly adverb); machine −0.059,
  +0.186, +0.177. Nothing near the ±0.8 that would make the cross-corpus gap an artefact of
  format. (Montgomery, n=3, produces no usable correlation and the tool says so rather than
  printing a number off three points.)

  **The tic list cannot be the criterion.** Tics with n=1–4 documents — *intricate/myriad*,
  *robust/seamless*, the *which-is-why* frame — have no measurable enrichment at all. Any
  rule expressed as "this tic must appear in dialogue" is therefore unimplementable for most
  of the candidate tics, which is a second, independent reason nothing here gates.

  Thresholds 1.15 and 0.85 in `check-recoverable.py` are the prototype's observed
  separation points, **not measured floors**, and the tool says so in its own output. Per the
  standing rule — a floor goes below the worst published document with headroom — no honest
  floor exists yet, so no row gates. This needs a corpus built for the measure, not one
  borrowed from a different question.
- **The brief audit: prohibition-style instructions were being handed to the drafting model,
  and the strongest one was in a file that told you to do it deliberately.** Scanning every
  model-facing skill for prohibition density (`never`, `no *`, `do not`, `avoid`, `ban`, `zero`)
  put `skills/deslopify/references/style_guide.md` far ahead of everything else — 70 hits in
  4,609 words against a median of around 12 — and its first line read *"Add this file to your
  AI assistant's system prompt or context."* Forty-one "Avoid patterns like" blocks, a title
  reading "AI Writing Tropes to Avoid", and an instruction to load the lot as context.

  That is VERMILLION §8.8's experiment, and §8.8 reports what it does: the constraint list
  leaks into the prose, the budget goes on compliance, and any good detail that appears is a
  side effect rather than the aim. The file was **reframed, not gutted** — it remains the
  project's best diagnostic, several of its rows carry this project's own measurements, and
  the diagnosis is worth more than the list. It now opens with the reason, carries the
  study's "ask for this instead" table, and states plainly that it is a review checklist
  rather than a generation brief.

  The second finding from the same scan was better than the first, because it was a **gap**
  rather than a fault. `skills/setting/SKILL.md` taught four jobs a line of dialogue can do:
  reveal character, advance conflict, carry information, create tension. All four are
  instrumental. The study's strongest generative lever — surplus, speech that advances
  nothing — had no representation anywhere in the system, in a pipeline whose entire reason
  for existing is better prose. It is now a fifth job, briefed as a scene rather than as a
  trim, because a chapter whose dialogue all carries information is not tight but dead.

  The third was a genuine internal contradiction. The humanising guidance strips canned
  connectives while `corrector`'s connective mode instructs the model to *add* transitional
  passages, and VERMILLION's single strongest cue is rigid canned transitions at AUC 0.930 —
  the highest of the ten, surviving both genre and period controls. Both behaviours are
  correct and they were pulling against each other with no resolution on file. The resolution
  is not a compromise on the join but a change in how one is made: open on the thing rather
  than on the logic for it.

  What the scan did **not** change: process prohibitions. "Never skip the checkpoint", "never
  touch scene middles in connective mode", "never guess" are scope rules for a pipeline and
  they stay. The distinction that survived the audit is **a prohibition on what prose may
  contain versus a prohibition on what the process may do**, and only the first kind is the
  failure mode VERMILLION describes. Roughly 40 of the 48 hits in `incunabula/SKILL.md` are
  the second kind.

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

# 5. cross-check U4/U5 against a public-domain novel corpus of another era
python measure-pd-corpus.py <dir-of-.txt-novels>       # reports only, proposes nothing
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

## 16. `A25` raised, and the test that told `A25` from `D1` and `D2`

`A25` also failed published chapters under its 1/2000 cap (1.0%), and the obvious reading
was that it belonged with `D1` and `D2` in the report tier. That reading is wrong, and the
wrongness is the most useful thing in this whole sequence.

**All three rows false-fail human prose. Only one of them should be demoted.** What
separates them is not the false-failure rate but whether the AI control sits *above* the
published distribution or *inside* it:

| row | published chapter max | control max | control inside or above? | decision |
|---|---|---|---|---|
| `D1` | 33.52/1k | **0.00** | far inside | report-only |
| `D2` | 8.40/1k | 5.80 | inside (p50 4.00 vs published 3.23) | report-only |
| `A25` | 0.93/1k | **3.13** | **above** | **raise the cap** |

`A25`'s cap went from 1/2000 to **3/2000** — 1.5× the worst published chapter, the one row
in this table where the usual headroom convention actually fits. Published failures
1 → **0 of 102**, while 2 of the 3 control chapters that exceeded the old cap still do.
Its warn band moved 1/4000 → 1/2000 so it sits at the published p95 rather than under it.

`A25` is now the only A-row in the directory with both a zero false-failure rate *and* a
control it can catch.

### Everything above is now enforced, not just recorded

Each decision here was a one-time measurement, and nothing re-checked them. Two controls
in `validate-controls.sh` close that:

- **Control 8** reads the `REPORT` block out of `deslop-check.sh` and fails if any id in
  it ever prints `FAIL`. A later edit that quietly promotes a demoted row is caught
  automatically, and newly added rows are covered without editing the test.
- **Control 9** regenerates the monotone-arc fixture and fails if `A1` passes it.

Both were proven to fire by tampering rather than assumed: removing the gate flag from the
`REPORT` loop makes control 8 fail with a named row.

**Regenerated artifact.** `pd-chapter-scan.txt` predated the `A25` raise and was reporting
a cap the gate no longer used — the same class of error as a stale threshold, wearing a
measurement's clothes. It has been rescanned (41 chapters, stride-sampled from the
140-novel corpus) and now shows **0 failures across every row**. Every density cap in
`chapter-rates.py` reads `ok`.

## 17. The missing corpus was half procurable, and four controls now run

This file has recorded, for a long time, that the binding constraint on the whole
calibration is a current multi-author native-English commercial corpus. That is true, and
it is also the reason controls 4–7 have never executed. Both of those facts came from
conflating two different problems.

**The multi-volume half is a format requirement, and it is free.** `check-uniformity.py`
and `check-drift.py` compare chapters *inside* a book, so a control needs several VOLUMES
already split into chapter files, named `<stem>-vNN__chapter-NN.txt`. That is a layout, and
Project Gutenberg serves the content. `fetch-multivolume.py` fetches published English
fiction, splits it on chapter headings (several heading shapes, because no single pattern
covers two centuries of publishing, and a book split at the wrong places is not a corpus),
and stages it. Six volumes, six authors, 1813–97, 303 chapter files.

**The recency half is a copyright wall.** Nothing commercially published recently is freely
available. That half stays open, and §6 already records that a stylometric finding about
period prose measures the period as much as the prose.

### What running them actually proved

All nine controls now pass, `validate-controls.sh` exits 0, and control 4 is the first real
validation of `U1`–`U6` against published prose:

| control | result |
|---|---|
| 4 — published volumes pass uniformity | **ok** (Pride and Prejudice 61 ch, Jane Eyre 38, Tess 60) |
| 5 — a uniform manuscript fails | **ok**, `U1` CV 0.8% and `U5` CV 0% |
| 6 — published volumes hold one voice | **ok** |
| 7 — a book that changes voice fails | **ok**, 4.53 against the 10-chapter `SIZE_FLOOR` of 1.94 |

Control 7 matters more than it looks: it is the size-dependent drift floor from §14 firing
on real prose, at a size the old flat 1.40 was never calibrated for.

### The bug that nearly sent a settled floor back for revision

The first fetch produced paragraph-length CV of **32%**, where the 140-novel corpus gives
80–223% (median 110). U5's floor is 55%, so this read as *U5 failing real published
prose* — a third instance of the unit error, on a row already treated as settled. It was
not. Some Gutenberg files end lines `\r\r\n`, and opening them in **text mode** applies
universal-newline translation, turning the stray `\r` into an extra `\n` — a blank line
between every hard-wrapped display line. Every wrapped line became its own paragraph, the
paragraph count tripled, and the metric collapsed.

The catch was arithmetic, not statistical: a 316,000-word novel reported 28,242
paragraphs. Post-fix, CVs are 116–162% across three volumes, in line with the existing
corpus, and U5's 55% floor is confirmed rather than revised.

This is the third file-handle-class bug in this section's history and the second to produce
a confident wrong number. `fetch-multivolume.py` now decodes bytes and normalises `\r\r\n`
explicitly, asserting no `\r` survives normalisation.

## 18. `U1` does not transfer to non-fiction, and the genre sweep cost one download

The open question was which gates stop working outside fiction. The cheap way to answer it
is not to generate a book - it is to run the fiction-calibrated rows over **published
non-fiction** and see which ones accuse it. Six volumes, five authors, 143 chapters:
Darwin *Beagle* / *Origin* / *Journal of Researches*, Douglass *Narrative*, Dana *Two
Years Before the Mast*, Smith *The Wealth of Nations*.

| row | published fiction | published non-fiction | verdict |
|---|---|---|---|
| U1 chapter-length CV | 48.4-70.6% | **28.2-113.7%** | fails 1 of 6 |
| U2 sentence-length variance | clean | clean | transfers |
| U3 coda distribution | clean | clean | transfers |
| U6 signature-frame spread | clean | clean | transfers |

Darwin's *Journal of Researches* sits at **28.2% CV** against a 30% floor. Two more sit
in the warn band. This is **not** a third instance of the unit error from section 12 -
whole-book and per-chapter figures agree here (~32%, ~31%, ~28% on the Beagle). It is a
different shape of thing: a chapter in a novel runs as long as its scene does, and a
chapter on a species runs as long as the argument does. The measure is sound and the
population it was calibrated on does not include this one.

So `U1` is now **advisory on a book declaring `positioning: nonfiction`**, through the
convention mechanism that already carries U4 and U5. Enforced everywhere else, number
still printed, measurement quoted in the row's own output.

What I did not do is derive a separate non-fiction floor. Six volumes from five authors
is enough to *refute* a floor and not enough to *set* one - the same asymmetry that made
Montgomery a refuter rather than a calibrator, and the reason `PRINTERS_COPY.md` section 7
reserves threshold-setting to a person.

This also corrected the plan it replaced. The genre sweep was going to cost three
generated books of ~28,000 words; it cost one download, and it produced a finding the
sweep would only have produced after all the prose existed.

Control 10 in `validate-controls.sh` stages all six volumes and fails if any of them is
accused. It was proven by removing the scoping: the suite exits 1 and names
`darwin-beagle-v01`. The first version of that control tested only the first volume,
which passes comfortably - a guard that cannot be made to fail is not a guard.

## 19. `U1`'s published band was a light novel, and it warned on the human canon

The genre probe was supposed to answer "which rows are at risk across genres". Running the
uniformity gate over six staged published **fiction** volumes produced something else
first: **five of six warned on `U1`**, and every one of them sat below the 48.4% the tool
prints as the published minimum.

| volume | chapters | chapter-length CV | under the old 45% warn line |
|---|---|---|---|
| *Tess of the d'Urbervilles* | 60 | **33.4%** | warn |
| *Jane Eyre* | 38 | 39.7% | warn |
| *Dracula* | 25 | 42.2% | warn |
| *Pride and Prejudice* | 61 | 43.0% | warn |
| *Middlemarch* | 86 | 43.5% | warn |
| *Wuthering Heights* | 33 | 45.1% | ok |

Two separate defects, both pointing the same way.

**The band came from the wrong register.** The original derivation is a three-volume
corpus: *Wandering Witch* (Yen Press) - a **translated Japanese light novel**, with
chapters running 466 to 9,184 words inside one volume. Its 48.4 / 68.1 / 70.6% figures are
real measurements of real books; they are measurements of a register this pipeline does not
write. A light novel's short interludes are not English novel chapters. This is the same
error that put `D1`'s cap under a translated text, and the two now share a registry row.

**The floor had no headroom.** Against the worst English novel measured (33.4%), the
shipped 30% floor gives **1.11x** - this project's own convention is 1.5x. The floor was
close enough to the human canon that ordinary variation could cross it.

I checked the obvious innocent explanation first: sample size. The original corpus had
n = 17, 18, 13; these have 25 to 86. Resampling each book's real chapter lengths down to
n = 17 / 13 / 11 moves CV by at most 4 points (Pride 43.0 -> 38.7), which cannot account
for a 15-point gap. Nor is it a segmentation artifact - splitting a novel into N equal
segments gives CV ~0% at every N, so the signal is entirely in the real chapter
boundaries.

So: `U1` FAIL 30% -> **22%**, warn 45% -> **28%**. Detection is preserved, which is the
only thing that matters for a loosening: **Hollow Bridge still FAILs at 13.7% CV**,
and the uniform-manuscript control still FAILs at 0.8%. All six published volumes now read
`ok` with no warnings.

The generalisable lesson, and the reason this is in the Rejected registry rather than only
here: **a threshold band is only as good as the register it was measured in.** Two
thresholds in this directory have now been derived from a light novel, and both are
load-bearing. Whenever a cap is quoted as "the human range", the first question is which
corpus produced it.
