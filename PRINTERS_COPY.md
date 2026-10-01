# The Printer's Copy

The authoritative brief for this system. Every skill, gate and pass answers to it.

In the letterpress shop, the printer's copy is the manuscript the type is actually set from.
The standing forme is the locked assembly kept for reuse. This file is the copy; the skills
are the forme. When they disagree, this file is right and the skill has drifted.

It exists because nothing in this repository used to say what the whole system is optimising
for. Each skill knew its own craft, each gate knew its own thresholds, and the calibration
record knew its own numbers — and the question *what is a good book, and what is this
pipeline for* had no file at all. It does now.

---

## 1. What this system is for

**A novel that a reader cannot put down, written by a person who changed their mind.**

Not: a text that scores well on a stylometric measure. Not: a text that avoids tripping a
detector. Those are different targets and the difference is not academic.

VERMILLION (`vermillion-study/`, 140 public-domain English novels against 185 machine texts,
controlled for genre, period and length) tested the standard humanising advice and found what
it costs. The advice is a list of cosmetic repairs — replace em dashes with commas, drop
*Moreover*, add a one-line paragraph, vary sentence length, swap buzzwords for concrete
words. Every one of those would reduce a text's score on the framework that produced them.
**Not one of them would make a text more like a novel.** The framework's own author is honest
that it is a table for "reducing the synthetic feel of machine-generated prose" in the sense
of not tripping a detector — a legitimate goal for a student avoiding an academic-integrity
flag, and a poor goal for anyone trying to write.

And the failure compounds. VERMILLION's closing argument is that a detection framework built
without a critical theory of what it is detecting for will, over time, optimise against the
wrong target — "which is, in the end, what Sood's humanising table has done." A system that
learns from humanising scores is a system on that path.

So the test every rule in this system must pass, from here on:

> **If this rule only lowers a score, and does not make the book better, it is a privacy
> measure — and it must say so in its own text.**

Rules that make books better are aesthetic and are marked `aesthetic`. Rules that only lower
a number are marked `privacy` and are never allowed to stand in for quality. There are
currently **zero** `privacy` rules in the confirmed registry, which is a fact worth
preserving rather than a coincidence worth assuming.

## 2. How to read the rest of this file

Four registries, and the second is the most valuable one in the repository:

| registry | what it holds | why it earns its place |
|---|---|---|
| **Confirmed** | measures with a corpus, an n, and a threshold | the only things permitted to gate |
| **Rejected** | measures that were tried and did not survive | negatives stop being re-derived |
| **Load-bearing but unmeasured** | what matters and no surface measure reaches | the honest limit of the gates |
| **Open** | loose ends, including ones of our own making | so they are not quietly dropped |

Every entry carries a **motive** (`aesthetic` or `privacy`) and, where a gate exists, the
corpus and n behind the number. `tools/prose/check-errata.py` enforces both fields and fails
if an entry arrives without them. That validator is the mechanism of this file: without it,
"improves over time" means "accumulates confident opinions."

---

## 3. Confirmed — permitted to gate

Motive `aesthetic` throughout. Thresholds live in `tools/prose/`; the derivation, the corpus
description, the rejected candidates and the bugs found while validating live in
`tools/prose/calibration/CALIBRATION.md`. This table says *what is known*, not *how*.

| row | what it holds | evidence | standing |
|---|---|---|---|
| `U1` | chapter-length CV 48.4–70.6% | 3 published volumes; project books ran 3.2% | enforced |
| `U2` | spread of per-chapter mean sentence length ≥ 4.32 | as above; **corroborated independently** by VERMILLION, whose within-window burstiness is identical across corpora (p = .72) | enforced |
| `U3` | chapters closing on the coda formula | **0 of 50** published chapters | hard, zero tolerance |
| `U5` | paragraph-length CV ≥ 55% | 3 published volumes **and 140 public-domain English novels, 13.04M words, five eras — 0 failures** | enforced |
| `U6` | signature-frame spread | 3 published volumes; worst single frame in 23% of chapters | enforced |
| `A1` | emotional reversals per bin ≥ 0.45 | 140 novels, 13.04M words: min 0.469, **0 failures**; flags 27% of the measurable machine corpus. **The null is 0.5** — human prose sits above it, machine prose sits on it | enforced, see §5 |
| `D1`–`D3`, `A24`, `A25` | em-dash cap, rule-of-three, adverb density, coda density, antithesis density | Elaina corpus 175k/48 docs **+ Montgomery 270k** — both pass | enforced, **register caveat in CALIBRATION §10** |
| `F1` | closing coda as a *position* | 0 of 50 chapters — categorical, not a rate. **Survived a second corpus** | hard |
| `P1` | opener repetition | Elaina corpus | enforced |
| `P3` | fragment run | Elaina corpus; **Montgomery carries a legitimate run of 29** | **warn only** — a cap passing 29 also passes the slop fixture's 9 |
| `A1a`, `A2a`, `A3a`, `A19`, `A21` | word-list rules | **all five false-positived on Montgomery** | **demoted from hard to a rate cap**, tagged in output |
| `A26` | default name clusters | **the AI-written control only** — the human corpus cannot confirm or deny a list of names | warn only |

Two of these deserve their reasons repeated, because they are the ones that were nearly
wrong:

**`U5` is the row that travels; `U4` is not.** `U4` (one-line paragraph share) measures 50–62%
on the calibration corpus and a **median of 33.2% across 140 public-domain English novels —
below its own failure line, with 59% of that corpus below it.** It is a market convention for
dialogue-dense commercial fiction and nothing more. It is now advisory unless a book declares
`paragraph_convention: commercial-dialogue`. Five real novels at 11–14% would have been
failed. `U5` returns 0 failures on the same corpus. Same measurement method, same 13M words,
opposite verdicts — and the one that travels is the one about *variation*, which is the same
conclusion VERMILLION reaches independently from a different direction.

**`U1` is a statement about scenes, not about arguments.** Chapter-length CV measures
**33.4–45.1%** across six published English fiction volumes — a band that had to be
re-derived, because the one previously shipped (48.4–70.6%) came from a translated
light novel and warned on five of those six. Measured over six published **non-fiction**
volumes from five authors it gives 28.2–113.7%, straddling the fiction band. So `U1` is
advisory on a book declaring `positioning: nonfiction`, alongside `U4` and `U5`, and
enforced everywhere else at 22% fail / 28% warn. No separate non-fiction floor was
derived: six volumes can refute one, not set one.

**`A1` does not catch our own AI control.** Hollow Bridge, written by a model, scores
0.533 — inside the human range and above the warn line. See §5.

## 4. Rejected — must not be re-derived without new evidence

This registry is the reason the file exists. Each entry cost a measurement, and the cost is
the only thing that makes the entry worth keeping.

| measure | verdict | why |
|---|---|---|
| **within-document burstiness** (sentence-length SD) | no discrimination | published 9.5/10.1/10.4, project 13.2–14.5 — machine prose is *more* varied. VERMILLION: identical across corpora, p = .72. The usable form is the **spread across chapters**, which is `U2` |
| **type-token ratio** | confounded | falls as a document grows; chapters here are 2,150 words against the corpus's 3,557 |
| **"machine prose is lexically impoverished"** | **backwards** | VERMILLION: machine prose is *more* varied — MATTR AUC 0.739, Yule's *K* 0.615, and the most diverse machine text out-varied all 140 novels. Never add a lexical-variety rule |
| **"vary your vocabulary"** | unsupported | follows from the above, and is still in the inherited humanising advice |
| **sensory density as a machine tell** | inverted | VERMILLION AUC 0.672 for the **machine** side. Machine prose is more sensory-laden, not less |
| **imprecise abstraction** (cue I) | no signal | VERMILLION p = .16 |
| **vague attribution, hedging openers, *utterly*/*entirely*/*absolutely*** | ≤ 0.02 per 1k in **both** corpora | already covered by `A1`–`A25`; project books do not trip them |
| **`U4` as a law of human prose** | refuted | 59% of the human canon fails it |
| **scoping `U4` by dialogue density** | no relationship | r = 0.234 between speech-paragraph share and one-line share across the same 140 novels. The stated mechanism for `U4`'s band is **wrong** — see §6 |
| **prohibition-style generation briefs** | backfires | VERMILLION §8.8: *no em dashes, no rule of three* leaked its own constraint list into the prose, spent the budget on compliance, and produced detail only as a side effect |
| **zero-tolerance status for any word-list rule** | unsafe | `A1a`/`A2a`/`A3a`/`A19`/`A21` were all "published prose: 0" against **one** corpus. On 270k words of Montgomery, 11 hits — every one ordinary English (*subtly*, *robust*, a literal *tapestry* on a wall). The lists were built by reading machine output; a word is a tell at a **rate**, not a presence |
| **any hard rule validated on n=1 corpus** | method error | `README.md` requires *literally zero across the corpus* for a ban. One corpus cannot show a word is absent from English fiction. Position-based hard rules (`F1`, `A8`, `A20`) survived a second corpus; **every** word-list rule that was tested did not |
| **`P3` fragment-run as a hard gate** | not separable | Montgomery's deliberate 29-run vs the slop fixture's 9: a cap passing one passes the other. A limit of the measure, so it warns |
| **inconsistency clusters where a motive can be supplied** | refuted positionally | Gini across ten position bins is flat in every corpus: human 0.02 to −0.02, Montgomery −0.10 to +0.01, machine −0.01 to +0.03. Whatever the claim means, it is not position in the document. Register enrichment replaces it — see §5 |
| **hard rules as a category** | reduced 15 → 10 | the remaining ten are the position-based and non-fictional-register ones |
| **the document/chapter distinction being immaterial** | refuted | the density caps are derived from a whole published *document* and enforced per *chapter*. On 102 published chapters, `D2` failed **18.6%** of human prose and `D1` **14.7%**; both are now report-only. See §6 and `CALIBRATION.md` §12, §15 |
| **`U1`'s shipped "published 48.4–70.6%" band** | wrong corpus | that band is a **translated Japanese light novel** (Wandering Witch, Yen Press) with 466-word interludes, not English fiction. Six published English novels give **33.4–45.1%**, so the old 45% warn line warned on five of six and the 30% floor had only 1.11x headroom. Re-derived to 22/28. See §6 and `CALIBRATION.md` §19 |
| **a light novel as the reference register for an English-fiction pipeline** | wrong register | the same choice put `D1`'s cap under a translated text (see §6) and produced `U1`'s band. A reference corpus has to be the register the pipeline writes, not merely prose |
| **sequential ranks for tied values in a rank correlation** | manufactures signal | sorting a constant series gives 1,2,3..n, a perfect ramp that correlates perfectly with position by construction. `check-drift.py` reported dialogue share at rho +1.00 for a book with zero quoted speech. Ties take average ranks; a zero-variance series is unmeasurable, not maximally correlated |
| **"vary your chapters" as a rule with no word floor beneath it** | satisfiable by deletion | `U1` is a CV, so it is scale-invariant — truncating every chapter proportionally changes nothing. But cutting the two longest chapters by 40% takes a 30.3% CV to 22.5% and still passes. Five skill instructions push variation; the only word target in the pipeline is `target_range_words: [0, 0]`. **The cheapest way to pass the one chapter-shape row is to delete prose.** The finding is correct and is also gameable, which is the prohibition-brief shape arriving from inside |
| **a filename blocklist to exempt planning documents from the scanner** | wrong axis | `deslop-check.sh <book>/` fails `RUN_REPORT.md`, `foundation.md`, `voice-matrix.md` on prose caps they are meant to exceed. The tempting fix is to skip those names — but a chapter could legitimately be called `foundation.md`, so the blocklist exempts a chapter to save a document. The axis is *is this a chapter*, not *is this filename known*; the tool should name what it read |
| **a corpus of other people's books as the only test input** | cannot reach the generator's own input space | 446 chapter files across 12 published volumes did not produce one degenerate feature. A book this pipeline wrote did, on its first run: a feature that is constant because the pipeline never uses it. Human prose varies in every feature; generated prose skips the ones it does not use, and no human corpus will ever exercise them. See `ERRATA.md`, "a gate's own defect found by a book" |
| **"the gate was cleared once"** | not evidence the habit is gone | the antithesis tic was caught at 91%, revised to 18%, then reintroduced by the expansion pass to 2.04/1k and caught again. **Subtractive revision removes a tic; additive revision restores it.** Any pass that adds text re-runs every construction row |
| **a separate non-fiction floor for `U1`** | not derivable from n=6 | six published non-fiction volumes from five authors are enough to refute the fiction floor and not enough to set its own. Deriving one would repeat the n=1-corpus error that demoted five word-list rules |
| **the genre sweep as a way to find transfer failures** | superseded | it was going to cost three generated books. Running the fiction-calibrated rows over *published* non-fiction cost one download and found the `U1` failure immediately, before any prose existed |
| **`D1` and `D2` as detectors of machine prose** | refuted | the AI control sits *inside* the published distribution on both. `D1` reads 0.00/1k on all 22 control chapters — these books write `--`, so the row measures the encoding. `D2` control p50 4.00 vs published median 3.23. No cap separates them; report-only, and re-raising was rejected rather than deferred |
| **"a false failure means demote the row"** | refuted | `D1`, `D2` **and** `A25` all failed published chapters. `D1`/`D2` were demoted; `A25` was **raised** to 3/2000 and now fails 0 of 102. The difference is whether the control clears the human distribution (A25: 3.13 vs 0.93 — yes) or sits inside it (D1, D2 — no). Never decide this from the false-failure rate alone |
| **one fixed threshold per metric, whatever the sample size** | refuted twice | `DRIFT_FAIL` 1.40 was calibrated on 13–18-chapter volumes; the same published prose sliced to **4 chapters scores 2.99 and fails 100%** of the time (r = −0.777). `A1` 0.45 comes from a ~15-window mean; a **single** window of published prose falls below it **12.7%** of the time, and a 4,000-word book fails **20%**. See §6 and `CALIBRATION.md` §13 |
| **cached popular metrics generally** | see the pattern | the measures that survive are about local syntax; the measures that fail are about register convention. Any new rule must say which it is |
| **"the missing corpus is a procurement problem"** | half wrong | it was two problems wearing one name. The *multi-volume* half was a **format** requirement, free from Project Gutenberg, and controls 4-7 now run and pass. Only the *recency* half is a copyright wall. Conflating them meant four controls sat permanently unrun behind a constraint that only applied to part of it |

The last row is the generalisation, and it is the one to carry into any future proposal:
**a rule that depends on a register convention is a measurement of that register.** Before
adding one, ask what else besides the defect it would also be measuring.

## 5. Load-bearing but unmeasured

What this system knows matters and cannot see. The gates are silent on all of it, and a
clean gate report means nothing about any of it.

- **Whether a book is the length it was asked to be.** The first `sons-of-heaven-v2` draft
  came in at 11,839 words against a 28,000-32,000 target, and **no gate noticed**, because
  the only row that measures chapter length is `U1`, and `U1` is advisory for a declared
  nonfiction book. This is the advisory mechanism working correctly and still concealing a
  real failure. It cannot be fixed by tightening `U1` — that reintroduces the false failure
  on published non-fiction — so it needs a *target* check rather than a *variance* check, or
  an explicit waiver. A green report on a book half its intended length is the clearest
  possible demonstration that these gates are necessary and nowhere near sufficient.

- **Moral ambiguity.** VERMILLION's clearest statement of its own limit: ambiguity is an
  *architecture*, not a property of any sentence. A measure counting hedges finds more
  hedging in a novel built from incompatible testimony, and the finding is coincidental.
  Producing it requires tracking who knows what and when — plot analysis, not authorship
  forensics.
- **Justified inconsistency.** The distinguishing feature of human formal irregularity is that
  a reader can infer its motive: *Fantazius Mallare*'s narrator cannot hold a register for a
  paragraph, and the reader recovers why. Machine inconsistencies are accidents of assembly
  and recover as nothing. This is the measure VERMILLION most wishes it had, and this system
  has no proxy for it either. **Partly measured, and the part is smaller than the phrase.**
  `check-recoverable.py` reports each tic's *register enrichment* — its share inside quoted
  speech ÷ the text's own dialogue share. The em dash enriches 1.75× in the 19th-century
  human corpus and 1.49× in Montgomery against 0.79× in machine texts, and the within-corpus
  confound test is clean (r = −0.06 to +0.28). What it cannot do is read *intent*, which is
  the actual claim, and it cannot be applied to rare tics at all (n=1–4 documents, no
  measurable enrichment). It is a question, not a score, and nothing in it gates.
- **Surplus.** Now partly measured — `check-surplus.py` reports speech-turn distribution and
  its spread across chapters — but the *value* of a digression is invisible to any of it. The
  study's strongest generative instruction has a report and no gate. Same shape as
  justified inconsistency: the thing that matters is the reader's, and neither tool sees it.
- **Rhythm that changes because something in the scene changed.** The revised humanising
  table's first row. `U1`/`U2` measure that a book's chapters differ; nothing measures that
  they differ *for a reason*, and that reason is the whole of the study's claim about wonder.
- **A narrating self.** VERMILLION: the presence of an authorial presence is measurable, and
  its one canonical counter-example (`Clotelle`, at 0.085) is the lowest of eight case
  studies precisely because that author's presence is dramatised rather than stated. The
  measure found a canon artefact, not a defect.

## 6. Open — including one of our own making

- **A non-fiction corpus — PARTIALLY RESOLVED.** `U1` failed 1 of 6 published non-fiction
  volumes and is now advisory there, but six volumes from five authors can refute a floor
  and not calibrate one, so no non-fiction thresholds exist. `D1`'s cap is governed by a
  translated light novel and is probably too loose; `U4`/`U5` remain narrative-scoped. The
  earlier attempt to source public-domain nonfiction was abandoned on a **wrong
  diagnosis** — that Gutenberg files make paragraph structure unrecoverable is false, and
  the 140-novel corpus proves it. The files that did break it ended lines `\r\r\n`, which
  a text-mode read turns into a paragraph break. Recorded so the attempt is not given up a
  second time.
- **Recency.** The staged corpora are 1813–1905. Nothing commercially published recently is
  freely available; that is a copyright wall, not a research problem, and no tool here
  climbs it. The rejection registry already notes that a stylometric finding about period
  prose measures the period.
- **The canon as a variable.** A stylometric finding about human prose is a finding about
  the sampled humans, and the sample is somebody's canon.
- **Whether `D1` and `D2` are gates at all.** **RESOLVED — they are not.** The deciding
  measurement was never made until now: the AI control sits *inside* the published
  distribution on both rows. `D1` reads 0.00/1k on all 22 control chapters (these books
  spell a dash `--`, so the row measures the encoding) against a published maximum of
  33.52/1k. `D2`'s control runs p50 4.00, max 5.80, against a published median of 3.23.
  Neither separates machine prose from human prose at any cap, so they are **report-only**.
  Raising them was considered and rejected rather than deferred: a cap that clears
  published prose also clears every machine book, and a green row read as evidence is
  worse than no row. `A25` false-failed too and was **RAISED rather than demoted**, because
  its control reaches 3.13/1k against a published chapter maximum of 0.93 — the arms
  separate there, so a cap between them exists. That contrast is the generalisation: the
  test is not "does the row false-fail human prose" (true of D1, D2 and A25 alike) but
  "does the AI control sit above the human distribution, or inside it".
- **A measurement is not a number until the file is checked.** A scan abandoned on a
  timeout left an `awk` stage writing into its output for seven more minutes, producing a
  sparse file with 249,590 NUL bytes that reported 302 chapters for 204 files — with a
  completely plausible per-rule table attached. The count of headers agreeing with the
  count of files, and the byte-level absence of NULs, are now standing preconditions for
  believing any corpus figure here. See `CALIBRATION.md` §12.
- **Co-authorship.** The assisted tier is the most interesting corpus and the least studied:
  human-edited machine prose recovers 45% of the excess template reuse and only 12% of the
  sentence-length gap. Editing removes what the cues name, not what they miss.
- **The corpus that is still missing.** `corpus/montgomery/` is native English and commercial
  but is **one author, three books, a century old, and a lyrical stylist** — a corpus that can
  refute a rule and cannot set one. It is enough to demote five rules and is not enough to
  re-derive a single cap. `fetch-multivolume.py` adds breadth — six Gutenberg authors,
  1813–97, staged in the multi-volume layout controls 4–7 need — and those four controls now
  run and pass, so `U1`–`U6` and the drift floor have a first real validation against
  published prose. **What it does not fix is recency.** These books are 19th century, and this
  file already records that a stylometric finding about period prose measures the period. A
  *current* multi-author commercial corpus is a copyright wall, not a research problem, and
  no tool in this directory climbs it.
- **A corpus for surplus and for recoverability.** Both tools shipped report-only *because*
  there is nothing to gate against, and both now have numbers from the corpora this project
  happens to hold. Those numbers are enough to build the tools and not enough to set a
  floor: the tic list is unmeasurable at n=1–4 documents for most candidate tics, and no
  published-commercial surplus figure exists. Until a corpus is built for each measure rather
  than borrowed, `S1`–`S4` and every row of `check-recoverable.py` stay uncalibrated.
- **What `A1` cannot see in a short book.** Its unit is a 4,000-word window, so 70 of the 153
  machine texts — single-chapter serials — are unmeasurable and reported as such. **This
  entry understated the problem and is corrected here:** a short book is not unmeasured, it
  is measured noisily. 12.7% of individual published windows fall below the floor against 0
  of 40 novel means, and a 4,000-word book built from published prose fails `A1` 3 times in
  15.  The floor now scales with window count (`WINDOW_FLOOR`), so this entry is superseded on
  the mechanism — see `CALIBRATION.md` §14. What is still open is the 92–95% detection
  cost, and the fact that the guarantee is "never fails a clean book" rather than
  "always catches a monotone one".
- **Whether `DRIFT_FAIL` should exist at all below ~10 chapters.** RESOLVED in §14: the
  floor is now `SIZE_FLOOR`, measured per chapter count, and the two-voice control still
  fires at every size. What remains open is the **detection cost** — 92–95%, not 100% —
  and whether a gate that misses one real voice change in eight is worth more than the
  false accusations it removes. That is a judgement about this pipeline, not a
  measurement, and nobody has made it yet.
- **Why the 1.5x headroom convention is not used on the drift step.** A convention that
  cannot be applied without disabling the gate is a convention that does not apply. The
  two arms overlap at every chapter count, so 1.5x the worst clean book sits *above* the
  weakest real voice change. Recorded because the convention is written into the method
  section as though it were universal, and this is the first case where following it would
  have produced a gate that never fires.
- **What `A1` cannot see in a short book** — see the corrected entry above.
- **Why the study's machine corpus is not comparable to ours.** It passed through a Royal Road
  boilerplate filter this directory cannot reproduce, so its machine-side figures are
  evidence about *that* corpus and not about machine prose in general. Our own measurement of
  83 of those texts is in `CALIBRATION.md`; it agrees on the shape (median 0.502) and
  disagreeing on the extremes is expected.

---

## 7. How this file changes

Three tiers, and the default is the most cautious one. Configured by `errata.mode` in
`PROJECT_STATE.yaml`; the shipped default is `hand`.

### Tier 1 — `hand` (default)

`ERRATA.md` appends observations. **Nothing in this file changes without a person changing
it**, and a change is proposed as a diff, in the errata, with its evidence attached. A
threshold never moves on one book's failure — that is how a convention becomes a constant and
a period confound gets laundered into a permanent law.

### Tier 2 — `bulk`

For the case that motivated it: a lot of books, and a person who does not want to read every
proposal. An observation auto-promotes into the **project's local** copy of this file when
**three or more independent books** support it and the supporting corpus is named. Local only
— never the shipped pipeline, never a threshold. This is the safe half of "hands off", and it
is safe because the blast radius is one book.

### Tier 3 — `auto`

Thresholds re-derive themselves from accumulated book data, with diffs printed and a dated
changelog. This is the mode the project's own record argues against, and it is here because
deleting the option is a way of losing the argument. If it is ever used:

- it may promote **observations**, never invent a corpus;
- a threshold moves only on a **corpus change**, and the corpus is named and measured;
- every rule carries a date and a **re-check horizon**, because cue validity erodes as models
  change and a rule with no date silently encodes one generation's behaviour as law;
- it prints what it changed, every run, forever.

### What no mode may do

1. **Promote a `privacy` rule to `aesthetic`,** or create one without the §1 test written next
   to it.
2. **Move a threshold on a single book,** or on a threshold's own failure being inconvenient.
3. **Write the motive field.** A machine may propose; the motive is a human's account of why
   a rule exists and it is not machine-generated.
4. **Learn from humanising scores.** Panel verdicts, reader reactions and swarm sentiment are
   evidence about the book. A detector score is evidence about the detector. These are
   different inputs and only the first is allowed to move anything.

### The self-check, from the study's own central claim

VERMILLION's finding is that a model has a mode and a writer has a distribution; variation
across documents is the human signature, and within-document variation is not. **Run that
check on this file.** If the same intervention starts appearing on every book — the same cut,
the same rhythm fix, the same paragraph advice — the guidance has become a mode, and every
book built through it will inherit the same setting. Uniform guidance produces uniform books
with a great deal more confidence than the originals had.

The tell is a `Rejected` registry that stops growing. A system that only ever confirms itself
is not learning; it is ossifying, and it will do so while every gate stays green.
