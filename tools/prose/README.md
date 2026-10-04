# prose — the mechanical half of the prose gate

The tools that check a manuscript mechanically, so that a human review can spend its
attention on the parts no scanner can see. They ship with the pipeline because every
book built by it was checked with them, and the numbers behind their thresholds are
recorded rather than remembered.

```
deslop-check.sh        one chapter at a time, against per-1k caps
check-uniformity.py    a whole manuscript, comparing chapters to each other
check-drift.py         a whole manuscript, comparing its first half to its second
check-arc.py           does the emotional direction ever change   (A1 gates)
check-surplus.py       how much of the dialogue carries no plot    (reports, never gates)
check-recoverable.py   which tics a character could plausibly own (reports, never gates)
check-length.py        did the book deliver the length it declared (gates; L1)
check-errata.py        the guard on this system's own guidance    (reads no prose)
validate-controls.sh   re-runs the control suite (16 controls)
```

And the narrative class (Freeze 13), which measures the shape of story rather than the
surface of prose:

```
check-narrative.py     what the book owes: debt, beat arcs, scene functions
                       (N1/N4 gate on declared contracts - reads no prose, L1's class)
check-figurative.py    where the images pile up on one referent   (reports, never gates)
check-dialogue-tags.py per-character speech-tag register          (reports, never gates)
check-quantities.py    do the numbers agree with each other       (reports, never gates)
```

`calibration/` holds four more, all report-only:

```
audit-slack.py         is any threshold looser than its derivation
chunk-pd-corpus.py     slices published novels into chapter-sized chunks
chapter-rates.py       derives density caps from chapters, not documents
arc-units.py           is A1's floor below the worst window, or only the worst novel?
arc-short-book.py      runs the real gate on published prose at four book lengths
drift-units.py         does the voice-step score depend on chapter count?
size-floors.py         both arms per size: can a size-dependent floor catch real drift?
d1d2-decision.py       does a cap separate the AI control from published prose at all?
make-arc-fixture.py    builds the monotone-arc control A1 must fail
measure-pd-corpus.py   U4/U5 over a public-domain novel corpus
proto-recoverable.py   the recoverable-inconsistency prototype (scratch)
fetch-multivolume.py   downloads a multi-volume Gutenberg corpus for controls 4-7
```

**Every threshold in this directory is wrong for some book, and it is known why.** Each
was derived on one unit and is enforced on another:

- the density caps were derived from the worst published **document** and enforced per
  **chapter** — on 102 published chapters, `D2` failed human prose 18.6% of the time and
  `D1` 14.7%. **Fixed**: `D1` and `D2` are now report-only, because the AI control sits
  *inside* the published distribution on both rows, so no cap separates them. `A25` failed
  too but was **raised** rather than demoted — its control clears the human distribution, so
  a cap between them exists. All three now fail **0 of 41** published chapters.
- `DRIFT_FAIL` was calibrated on 13–18-chapter volumes — the same published prose sliced
  to 4 chapters scored 2.99 against a 1.40 cap and failed 30 of 30 times. **Fixed**: the
  floor is now `SIZE_FLOOR`, measured per chapter count.
- `A1` comes from a ~15-window mean — a single window of published prose falls below the
  floor 12.7% of the time. **Fixed**: the floor is now `WINDOW_FLOOR`, measured per window
  count, and 0.45 turns out to be correct from 4 windows up.

The two fixed gates no longer use the directory's usual 1.5× headroom, because their two
arms overlap and that convention would put the floor above a real defect. The drift floor
catches **92–95%** of genuine voice changes rather than all of them: the guarantee is
*"never fails a clean book"*, not *"always catches real drift"*. Both thresholds print
their own basis on every run. See `CALIBRATION.md` §14.

None of the gating tools subsumes another. `deslop-check.sh` never holds two chapters at once, so
it cannot see a book's shape. The two cross-chapter gates answer opposite questions —
`check-uniformity.py` fails a book whose chapters are too alike, `check-drift.py` fails a
book that stops being like itself — and `check-arc.py` fails a book whose emotional direction
never reverses. None of them can see a bad sentence. A book passes the prose gate only when
all four are green, and even then all four are only the mechanical half. Read it aloud.

Three rows are reported rather than gated, and none can become a gate without a corpus
first. `check-surplus.py` measures speech-turn length distribution and a lexicon-dependent
instrument ratio; the reason it exists at all is in its own docstring, and the short version
is that a chapter in which every line of dialogue moves the plot is not badly written, it is
dead, and no per-1k cap in this directory can see the difference. `check-arc.py` reports arc
*range*, net drift and volatility alongside its one gated row. `check-recoverable.py` reports
where tics sit relative to the text's own dialogue share, which is the only version of
"justified inconsistency" that survived measurement.

`check-arc.py` is the newest gate here and the one most likely to be oversold, so its own
output says the opposite of what a marketing pass would say: **it does not catch
Hollow Bridge**, this project's AI-written control, which scores 0.533 — inside the human
range and above the warn line. It has zero false failures across 140 human novels and flags
27% of the *measurable* machine corpus. That is a real floor on a real failure mode, and it
is not a detector.

Read against its null and it is a sharper tool than that. A curve of independent steps
reverses about half the time, so **0.5 is the null**: human prose sits at 0.571, measurably
above it, and machine prose at 0.501, on it exactly. Human arcs change direction more often
than noise produces; machine arcs are indistinguishable from a random walk. A book under 0.45
is not merely flat — it is smoother than noise.

Its unit is a 4,000-word window, so single-chapter serials cannot be measured at all: 70 of
the 153 machine texts, and any short book. They are reported **unmeasured**, never as passing.

`check-recoverable.py` asks one question: is a tic in a place the text has licensed it? A tic
that sits inside dialogue can be a character's voice; the same tic in narration is an author
slipping. The tool reports each tic's **enrichment** — its share inside speech ÷ the text's
own dialogue share — so a dialogue-heavy book is not rewarded for being dialogue-heavy. It
cannot tell a *deliberate* irregularity from an accidental one, and the positional axis that
would have tried was measured flat (Gini 0.00–0.07 in every corpus, see
`calibration/CALIBRATION.md`). What it reports is register, not intent. Nothing in it gates:
there is no corpus from which a floor could honestly be derived.

`check-errata.py` is the odd one out: it reads no manuscript and judges no prose. It checks
`PRINTERS_COPY.md` and `ERRATA.md` — the system's standing brief and its append-only ledger —
so that a rule cannot enter the pipeline because it was written down confidently. Every entry
must carry a date, all seven fields, a motive (`aesthetic` or `privacy`) and a state; a
`privacy` rule is not allowed to appear in the confirmed registry; and **the rejected-measures
registry may not shrink**, because a deleted rejection is a rule that gets quietly reinvented
after being disproven. It never mutates anything — it reports what the current promotion mode
would permit. See `PRINTERS_COPY.md` §7.

## Usage

```bash
bash deslop-check.sh manuscript/chapters/chapter-01.md      # one file
bash deslop-check.sh manuscript/chapters/                    # a directory
bash deslop-check.sh --caps                                  # print the calibration table

python check-uniformity.py manuscript/                       # a book, or several
python check-drift.py manuscript/
python check-arc.py manuscript/                             # A1 gates
python check-surplus.py manuscript/                         # report only, always exits 0
python check-length.py <book>/                              # L1; 0 ok, 1 short/long, 2 not run
python check-recoverable.py manuscript/                     # report only, always exits 0
python check-errata.py                                      # the pipeline's own protocol

python check-narrative.py <book>/                           # N1/N4 gate; N2/N3 report
python check-figurative.py <book>/                          # report only, cannot fail
python check-dialogue-tags.py <book>/                       # report only, cannot fail
python check-quantities.py <book>/                          # report only, cannot fail

bash validate-controls.sh   # exits 2 if no corpus installed; 0 if all controls pass
```

**Point the scanner at the chapters directory, not the book.** `deslop-check.sh` on a
book directory reads every `.md` in it, so it fails `RUN_REPORT.md`, `foundation.md` and
`voice-matrix.md` on prose caps those documents are *supposed* to exceed — and prints
"fix the rows above before this chapter counts as drafted" about a file that is not a
chapter. Use `<book>/manuscript/chapters`. The Python gates resolve the chapters
directory for you and are safe either way.

All of them take either a book directory (`<book>/manuscript/chapters` is found for you),
a manuscript directory, or a chapter directory. Called with no arguments the Python gates
sweep every `*/manuscript/chapters` under the project root.

### Running all eleven controls

The controls need published prose, which is not shipped. Fetch it once:

```bash
cd tools/prose/calibration
python fetch-multivolume.py corpus/multivolume --limit 6   # 6 books, ~300 chapter files
python fetch-multivolume.py corpus/nonfiction --nonfiction  # 6 volumes, 5 authors
```

Then run the suite, pointing each control group at the corpus it needs:

```bash
cd tools/prose
HUMAN_CORPUS="calibration/corpus/montgomery" \
VOLUME_CORPUS="calibration/corpus/multivolume" \
AI_CONTROL="/path/to/an-ai-written-control/chapters" \
bash validate-controls.sh      # exits 0 when every control passes
```

`HUMAN_CORPUS` is scanned file-by-file by the per-chapter scanner and wants a handful of
documents. `VOLUME_CORPUS` must be staged as `<stem>-vNN__chapter-NN.txt` and is hundreds
of files, which takes minutes to scan — conflating the two is why controls 4–7 could not
previously run at all.

## The corpus is not shipped, and that is deliberate

Every threshold here was measured against published commercial prose, and that prose is
somebody else's copyright. What ships is the **derivation**: `calibration/CALIBRATION.md`
holds the corpus description, every number, the method, what was measured and rejected,
and each bug found while validating. `calibration/measure.py` re-measures a corpus you
supply. `calibration/slop-fixture.md` is the one control small enough and ours enough to
ship — a positive control that must always fail.

`validate-controls.sh` therefore exits **2** when no corpus is installed, and 2 means
*not run*. It never means pass. A control that reads nothing proves nothing, and this
directory's own history contains three separate bugs that all pointed the same way: the
gate reporting itself more capable than it was.

One corpus is enough to re-run the scanner and both cross-chapter gates. Two are better:
a positive control built from two books joined at the spine is a stronger test than a
synthesised one, and the script uses it automatically when a second book is available.

## Calibrating to your register

The caps are tuned to **narrative fiction**. They are derived from a translated
light-novel series, which the calibration record concedes makes the em-dash cap looser
than native-English prose would justify. Non-fiction, thriller or literary fiction should
be re-derived from a corpus in that register before the caps are trusted:

```bash
cd calibration
python extract.py "<book>.epub" corpus/<name> <tag>     # epub -> one text file per document
python measure.py corpus/<name> "<native control dir>" > calibration-report.txt
bash ../validate-controls.sh                            # all seven controls must behave
```

Two rules apply when setting any cap, and they exist because both were broken once:

1. **A rule may be zero-tolerance only if published prose never does it** — literally zero
   hits across the whole corpus. If published prose does it, it can be capped, never banned.
2. **A density cap goes roughly 1.5× above the worst single corpus document**, so the
   reference passes with headroom instead of squeaking by.

Never set a threshold from a number you have not measured. The drift gate in this
directory shipped its first cap from an assumption, and all three published volumes blew
past it — which is what a bad metric looks like from the inside.

## What these tools cannot do

- They cannot see voice, rhythm, dead metaphor, or one argument restated ten ways.
- `deslop-check.sh`'s `A26` (default name clusters) is a heuristic and warns only: the
  corpus cannot confirm or deny a list of names, and a name is not a defect the way a
  phrase is.
- `check-uniformity.py`'s paragraph rows (`U4`, `U5`) are scoped to narrative prose. A book
  declaring `positioning: nonfiction` in `PROJECT_STATE.yaml` carries them as advisory,
  because a narrative corpus cannot calibrate the paragraph shape of an argument.
  `U4` is scoped more narrowly still, and by default **does not fail anything**: it is a
  market convention rather than a law of prose, and across 140 public-domain English novels
  its median (33.2%) sits *below* its own failure line, with 59% of the corpus below it. The
  number is printed with both known conventions and a person judges it. Declare
  `paragraph_convention: commercial-dialogue` to hold the book to the market gate. `U5` is
  enforced, and 0 of those 140 novels fail it. See `calibration/CALIBRATION.md`,
  "U4 is advisory by default".
- `check-uniformity.py`'s `U1` (chapter-length variance) is a statement about **scenes**. It
  measures **33.4–45.1%** across six published English fiction volumes, and 28.2–113.7%
  across six published non-fiction volumes, which straddles the fiction band. So `U1` is
  advisory on a book declaring `positioning: nonfiction`, and enforced everywhere else at
  22% fail / 28% warn. No separate non-fiction floor exists: six volumes from five
  authors can refute a floor, not set one. Note the fiction band itself had to be
  re-derived — the previously shipped 48.4–70.6% came from a *translated light novel*
  and warned on five of those six novels. See `calibration/CALIBRATION.md` §18, §19.
- `check-drift.py`'s cap sits above the worst published book **at that book's chapter count**
  and is expected to warn on books that are merely uneven. It misses roughly 1 real voice
  change in 8, and says so on every run. A false accusation of voice drift costs a
  rewrite, and the evidence behind one is thin — a reading of 1.2 is not a verdict.
- `check-length.py` (`L1`) is the only row here that is **not** a corpus measurement. It
  compares a book to the length that book declared for itself in `PROJECT_STATE.yaml`, so
  there is no population it can false-fail. It exists because every other row is a rate,
  and a rate is satisfied by a book that is shorter than intended: `U1` is a CV and is
  therefore scale-invariant, so cutting the two longest chapters by 40% *raises* it. That
  makes deletion the cheapest way to pass the chapter-shape row, and `L1` is the only
  check that moves the other way.
  - Declare `target_floor_words` and `target_ceiling_words` for it to be **enforced**.
  - A lone `word_count_target` makes it **advisory** — failing a single figure would mean
    inventing a tolerance, and this project does not set a threshold from an unmeasured
    number.
  - The schema default is `target_range_words: [0, 0]`, which counts as *not declared* and
    exits 2. Exit 2 is not run; it never means pass.
- `check-surplus.py` cannot tell surplus from padding, and it reads speech out of quotation
  marks, so a quoted letter or a sign is counted as dialogue. Both limitations are the
  study's own (`vermillion-study/` §9.6) and neither is fixable without a parser.
- `check-arc.py` measures the rhythm of surface valence, not feeling. Its lexicon cannot see
  irony, it was transcribed by hand and truncated once already (asserted at import, 121/143
  words), and it originally computed one curve per novel where the study computes per
  4,000-word window and averages — a 0.08 error that looked entirely plausible. It now
  reproduces the study's published human distribution to three decimals, and its machine
  figures are our own measurement rather than the study's, because that corpus passed through
  a boilerplate filter this directory cannot reproduce. It misses Hollow Bridge. A pass
  is not a clearance. Its floor is **also sample-size dependent** and is now measured per
  window count (`WINDOW_FLOOR`); 0.45 is correct from 4 windows up and drops below that. A
  pass on a short book is not a clearance either.
- `check-recoverable.py` cannot distinguish a deliberate clipped sequence from an accidental
  one. That is the case that sent `P3` to warn-only, and the positional axis that would have
  separated them measured flat in every corpus tried, so recoverability here is a statement
  about **register**, not about intent. It also reads speech out of quotation marks (as
  `check-surplus.py` does), and a book can score well on it while being poor — dialogue is the
  easiest place in a manuscript to hide a tic, and concentrated slop is still slop. Treat it
  as a question, not a score.
- `check-narrative.py` **cannot see a setup nobody recorded.** It reads no prose; it
  verifies `NARRATIVE_LEDGER.yaml` against the book's chapter files. The extraction is
  `case-keeper`'s job and the audit is `collator`'s; a clean ledger over a careless
  extraction is invisible here, which is why collator's full pass runs before this row
  is consulted at delivery. It gates with no corpus for `check-length.py`'s reason: it
  compares a book to the obligations *that book declared for itself*, and there is no
  population it can false-fail. N2/N3 report repetition and duplication and fail
  nothing: a repeated circuit is sometimes deliberate, and no corpus of published beat
  maps exists from which a floor could be derived.
- `check-figurative.py` counts figurative *markers* and coordinated image clauses, not
  meaning. It cannot see a metaphor without a marker, it counts `like` in comparisons
  that are not figurative, and it cannot attribute an image to a referent — the
  "two images, one sensation" judgment is `proof-panel`'s Critic, and the tool says so
  on every run. A dense good passage lights it up.
- `check-dialogue-tags.py` attributes by name within a short window of the quote;
  pronoun-tagged lines count as unattributed, so a chapter that tags every line with
  "she" reports few attributed lines. It reads speech out of quotation marks (a quoted
  letter counts), and a name that is also a lowercase common word in the book is
  filtered out as a false positive — occasionally over-filtering a real one.
- `check-quantities.py` cannot see what a number applies to, so two same-unit values can
  be correct in two situations and Q2's spreads are observations. Ranges collapse to
  their first number. Q3's g-force notes come from physiology, not from a corpus: they
  are notes for a reader, not a threshold, and dimensional coherence stays an evaluator
  judgment. Q4 (counted nouns carrying conflicting values, RECONCILE on values restated
  across chapters) **never sums**: parts of a stock add up (four taken plus thirty-six
  left), so it names candidates and the reader reconciles. A listed candidate is not a
  finding.
- The **density caps** in `deslop-check.sh` are calibrated on documents and applied to
  chapters. All three offenders are now resolved: `D1` and `D2` are report-only because the
  AI control sits *inside* the published distribution on both (`D1` reads 0.00/1k on all 22
  control chapters because these books write `--` rather than U+2014), and `A25`'s cap was
  raised to 3/2000 because its control *clears* the published maximum. See
  `CALIBRATION.md` §12, §15 and §16.
- `calibration/chapter-rates.py` cannot tell you whether a *cap* is right, only how far
  from the measured worst it sits, and it trusts its input: it refuses a scan output
  containing NUL bytes or whose header count disagrees with its file count, because a
  killed scan that kept writing produces a file that still prints a plausible table.
- `check-errata.py` cannot tell a good motive from a bad one, and does not try. It forces the
  question to be written down where someone has to answer it; the answer is still a human's.
  It also cannot check that a corpus named in an `evidence` line exists, because that line is
  prose.

Passing is necessary and never sufficient. The scanners exist so that the things a human
should be reading for are the only things left to read for.

---

# Known tool defects (2026-09-28)

Interim operational rules, in the same spirit as "always pass the chapters directory"
above. Neither is fixed: `validate-controls.sh` is a frozen gate, and `GATE_FREEZE.md`
plus `PRINTERS_COPY.md` §7 reserve changes to it. These are recorded, not repaired.

## 1. `validate-controls.sh` reports "no corpus installed" when 2.5M words are on disk

The script defaults `HUMAN_CORPUS` to `calibration/corpus/elaina`, which does not
exist. `calibration/corpus/` actually holds:

| directory | files | words |
|---|---|---|
| `montgomery` | 3 | 279,281 |
| `multivolume` | 303 | 945,622 |
| `nonfiction` | 143 | 1,337,146 |

So an un-overridden run prints `NOT VALIDATED - no calibration corpus installed` and
returns **0** — a confident "your caps are unverified" while the measurements are sitting
in the next directory. That is the same failure shape the rest of this file exists to
prevent, pointed the other way: a gate reporting itself *less* capable than it is.

**Interim rule:** pass the corpus explicitly.

```bash
HUMAN_CORPUS="$PWD/calibration/corpus/multivolume" \
AI_CONTROL="/path/to/machine-written/chapters" \
  bash validate-controls.sh
```

**Correct fix (not applied):** default to the newest installed corpus directory and
print which one it chose, or fail loudly listing the directories it did find. A default
pointing at a directory that has never existed in this repo is the whole defect.

## 0. A chapter filename the gates do not recognise is a whole book silently unchecked

All six cross-chapter Python gates match `chapter[-_ ]?0*(\d+)\.(md|txt)`. A book whose
chapters are named `ch-01.md` matches **none** of that, so every one of them reports
`no chapters found under ...` and exits non-zero.

This bit `the-origin-point`, which was written with `ch-NN.md`. Every gate run against it
before 2026-09-28 was reading zero files. `deslop-check.sh` was unaffected — it is a shell
script with its own glob — which is why the book had a clean-looking `PASS with warnings`
while the six gates that check cross-chapter structure had never executed. The book's
first genuine `check-uniformity` run found a **U6 FAIL** (antithesis in 6/13 chapters, 46%
against a 40% cap) that had been sitting in the manuscript the whole time.

**The gates behaved correctly.** They exit 1 (or 2 for `check-length`) rather than reporting
a pass on an empty read, and `validate-controls.sh` already states the rule in a comment: a
control that scans zero files is a failure, not a pass. The defect is the near-miss of
shape — `check-length: no chapters found under <path>` reads like the tool being broken
rather than the book being uncheckable, and `rc` is easy to lose behind a pipe.

**Operational rules:**

- Name chapters `chapter-NN.md`. If a book already uses another convention, the fix is to
  rename the files, **not** to loosen the six patterns: those are frozen and they are the
  only thing making a gate result attributable.
- When checking exit codes, do not pipe into `head`/`tail` and read `$?` from the pipe -
  that is the pipe's status. Capture the output, then check `rc` (`out=$(...); rc=$?`).
- Sanity check that a gate saw the book at all: its header prints a chapter count. A count
  of 0 means nothing was measured, whatever the verdict line says.

## 2. The control suite cannot complete inside a synchronous tool call

With a valid corpus the full run exceeded 590s and was killed twice (at 180s and 590s).
Measured individually:

| control | input | time |
|---|---|---|
| slop fixture | 1 file | 4.5s |
| human corpus | 279,281 words | 13s |
| AI control | 132,270 words | 2m 15s |

The cost is **corpus volume, not the scanner** — `deslop-check.sh` on the fixture is 4.5s.
Run it somewhere it can take ten minutes. A timeout is not a failure of the caps.

**The three substantive control properties do reproduce individually**, which is the part
that matters:

- published fiction → `PASS with warnings` (human prose is not falsely accused)
- synthetic slop fixture → `FAIL` (slop is caught)
- machine-written control → `FAIL` (machine prose is separated, not waved through)

So the freeze manifest's "all ten controls pass" is a claim with current supporting
evidence at the level of its individual properties, but not a single reproducible
end-to-end run. Treat it that way rather than as a green light.

**Discharged 2026-10-04.** The single end-to-end run now exists: all sixteen controls,
corpus and AI control supplied, `ALL CONTROLS PASS`, exit 0, zero skips — including
control 3 (6 of 11 chapters fail, 5 pass, unchanged from the last figure). The timing
refines the paragraph above: the 590s blowup is the **conflated** configuration
(`HUMAN_CORPUS` pointed at the 303-file multi-volume corpus). With the recommended
split — `HUMAN_CORPUS=corpus/montgomery`, `VOLUME_CORPUS=corpus/multivolume` — the full
suite completes in **about three minutes**. "Run it somewhere it can take ten minutes"
stands as belt-and-braces; the ten-minute figure measures the mistake, not the suite.
The run is recorded in `GATE_FREEZE.md` under the Freeze 13 entries.
