# Protocol decisions (design §12)

**Recorded:** 2026-10-31, from Kalie. Design §13's first checklist item is to confirm §12
decisions 1–7 *in writing* before any generation; this file is that confirmation, and it is
the only place the answers live. A row marked **OPEN** blocks whatever it names and nothing
else. A change to an answered row is a protocol deviation, not an edit — append a dated
note here rather than rewriting the answer.

| # | decision | status | answer |
|---|---|---|---|
| 1 | drafting model | **answered** | Gemini 3.8 Flash (`gemini-3.8-flash`), drafted by subagents on Kalie's Google Antigravity subscription |
| 2 | target length + band | **answered** | 60,000 words primary; a long-form set at 200,000, reported separately |
| 3 | ductus | **answered** | none — primary Arm B runs UNASSIGNED; one voice on 3 premises as a sensitivity arm |
| 4 | the human ten | **deferred** (by decision: "after") | assemble after generation |
| 5 | blind raters | **answered** | none — mechanical measures only |
| 6 | "both" (fourth arm) | **open, default stands** | three arms unless Kalie says otherwise |
| 7 | executing AI and route | **answered** | DeepSeek runs the study; Gemini 3.8 Flash via subagents drafts |

## 1. Drafting model — Gemini 3.8 Flash

Freeze the literal ID `gemini-3.8-flash`. **Do not** use `gemini-flash-latest` or any
floating alias: Google deprecated `gemini-3.7-flash` on 2026-10-08 and redirected its
requests to 3.8 Flash, so an alias is a silent model swap — which §7 and §13 both list as a
stop condition. Record, per book, the `modelVersion` string the API *returns*, not only the
ID we sent. A subagent that does not surface its responding model version cannot file an
Arm A or B row, because the manifest's `model_id` would be our intent rather than the
measurement, and H3 (model fingerprint) is a claim about the model that actually wrote.

If the Incunabula pipeline uses a different model for a non-drafting phase, §7 still holds:
hold the *drafting* model constant with Arm A, put the drafting model in `model_id`, and
name the other phase models in `deviations` as text. Temperature, top-p and system prompts
are still unfrozen (see open items below).

## 2. Target length — 60,000 words, plus a long-form set at 200,000

Read as **words**, not pages: a page is roughly 275 words, so 60,000 pages would be ~16M
words and neither arm could produce one. Say if that reading is wrong.

| stratum | target | accepted band | books |
|---|---|---|---|
| primary | 60,000 | 54,000–66,000 | 20 pairs (A+B), the frozen premises |
| long-form | 200,000 | 180,000–220,000 | 3 pairs (A+B), premises drawn from the unselected 20 |

The ±10% band width is my choice; §7 only says to record the band.

**The long books are a separate stratum, not four of the twenty made longer.** At 20 pairs
the study is already at its power floor (§9.8). Splitting 20 into 16 short + 4 long leaves
four pairs per stratum, which cannot separate a pipeline effect from noise, and it would put
length into the primary comparison without any design to estimate it. Two strata keep a clean
20-pair primary and still yield the long-form data.

Consequences recorded now rather than discovered later:

- §7's "one target for both arms" survives *inside* each stratum and is violated *between*
them. Any comparison that pools the strata is a protocol error; the long-form rows are
labelled exploratory in every table and never enter the residual-tell classification.- The long premises come from the pool's unselected 20, so no premise appears at two
  lengths and the frozen twenty stay untouched. Selecting three of them is a second freeze
  (`premises-v2`), to be done before Arm A starts, not during. **Frozen 2026-10-31:**
  `premises/frozen/premises-v2.json`, sha256 `a0439cd1…`, three premises — `adv-03`
  (adventure), `hor-01` (horror), `sf-03` (science fiction). Genres were shuffled under the
  seed and one premise drawn per genre from the twenty v1 did not take, so the selection is
  rerunnable rather than chosen. `run/dispatch.py --plan` numbers them `A-L01`…`B-L03`.
- 200,000 words is far past any single response, so both arms are multi-call by necessity.
Arm A uses §3's continuation wording only, and the count lands in `naive_continuations`.
A naive book that stalls at 60k of 200k is an outcome to log, not a book to rescue.
- The long books stress the pipeline's calibration: the arc windows, the chapter-spread
checks and the gates were measured on ordinary novel lengths. A gate that misfires at 200k
is a finding about the gate, and goes in `deviations`, not silently turned off.
- Scale: 20 pairs × 60k ≈ 2.4M words, 3 pairs × 200k ≈ 1.2M. ~3.6M words generated in
total. That is the cost of this answer and it is worth stating before the run starts.

## 3. Ductus — none for the primary arm; one voice as a sensitivity arm

The design's default (one shared neutral test ductus for all 20 Arm B books) is **dropped**,
and the evidence is in this repo rather than in a preference:

- `ductus.yaml`: *"No book carries one yet."* `skills/incunabula/SKILL.md` resolves the
  unassigned case as "the state every book in the catalogue was drafted in".
- §4 requires Arm B to run the pipeline *as it actually exists*. A shared test ductus is a
  voice no production book has ever run under, so it would make Arm B "the pipeline plus a
  voice nobody authored" — the arm would stop being the pipeline.
- REDTEAM M7 worried that a neutral ductus might sit outside the register the gates were
  calibrated on. That worry inverts here: the calibration corpus is catalogue books, and
  catalogue books are UNASSIGNED, so the no-ductus register *is* the calibrated one.
  Authoring a ductus is the move that would leave it.

So `ductus_id` is the literal `UNASSIGNED` on every primary Arm B row — the tool's own word,
recorded as a fact rather than left blank. `manifest.py` still requires the field non-empty,
so a blank cell is still rejected; `UNASSIGNED` is an assertion that can be checked.

**Sensitivity arm (3 books, exploratory).** Same pipeline, one input changed:
`python tools/ductus.py contract <book-root> --ductus study-voice-a`. The three premises were
chosen by hash (`sha256("study-voice-a|" + premise_id)`, first pick per genre, so no hand
pick and no genre clustering):

| book | premise | genre | voice | UNASSIGNED twin |
|---|---|---|---|---|
| `B-02V` | `adv-02` | adventure | `study-voice-a` | `B-02` |
| `B-03V` | `com-01` | comedy | `study-voice-a` | `B-03` |
| `B-09V` | `his-01` | historical | `study-voice-a` | `B-09` |
| `B-02W` | `adv-02` | adventure | `study-voice-b` | `B-02` |
| `B-03W` | `com-01` | comedy | `study-voice-b` | `B-03` |
| `B-09W` | `his-01` | historical | `study-voice-b` | `B-09` |

Each voice book is compared to **its own twin**, not to the other twenty: the difference is
the ductus's effect with the pipeline, the premise and the model all held constant. That is
a far cleaner estimator than three voice books against twenty strangers, and it is why three
books are enough to answer "does a voice move these numbers".

**Two voices now, on the same three premises**, which is what makes the arm able to answer
the question it was built for: whether a movement is *this hand* or *voice-ness in general*.

- Both voices move a feature the **same way** → voice-ness; a ductus tends to do that to
  that feature whatever the contract says.
- The voices move it in **opposite directions**, or by clearly different magnitudes → the
  hand; the contract is the lever, and its content is worth writing deliberately.
- Only one voice moves it → that voice's idiosyncrasy, reported as such and not generalised.

Six books, three premises, two contracts. It is still reported as "these two voices, on
these three premises" — two is a contrast, not a population — and never as "the ductus
effect". `analysis/voices.py` is the reading: per feature, each voice's median delta from
its own twin in Arm C SDs, the sign agreement across the three premises, and the verdict —
`voice-ness`, `hand`, `one-hand`, `inert`, or `unstable` when the three premises cannot
agree on a sign. A voice that does not move a row is reported as `inert`, not as zero.

The voice books are kept out of the primary analysis by `analyze.py --exclude-books
V,W`: their ids (`B-02V`, `B-02W`, …) would otherwise enter Arm B's per-feature medians and
inflate the arm to 26 books. Their premise ids (`02V`, `02W`) do not collide with `02`, so
they never enter the 20-pair A-vs-B comparison either — the exclusion makes that explicit
rather than accidental.

The contract (`ductus/study-voice-a/ductus.md`, digest in the sidecar beside it) is authored
for *reach*, not merit: it differs from the pipeline's default on axes the study measures
(sentence length, semicolon and colon density, paragraph length, dialogue share). So any
movement it produces is an upper bound on what a typical voice would do — and its long
uniform sentences may well trip `check-uniformity`'s spread gate, which is M7's risk made
visible and gets logged in `deviations` rather than tuned away.

Cost: 3 × 60,000 = 180,000 words, about 5% of the primary run.

## 4. The human ten — deferred until after generation

Deferring does **not** block generation, and this is worth stating precisely because the
design implies otherwise:

- Every distribution, IQR, band and false-positive rate already comes from **C-dist (109
  public-domain novels)**, per REDTEAM.md B1. n=10 was never enough to set a threshold.
- With decision 5 answering "no raters", the ten's excerpt layer has no consumer. What
  remains is ten filed exemplars at §5's selection criteria, which is a citation and
  provenance task, not a measurement one.

So C-deep leaves the critical path. One operational step follows: when Arms A and B are
analysed, the C-dist feature files must be in the same feature tree the analyzer reads, or
Arm C is empty and every row comes back `unclear` with a `C=0` warning. Extract
`books/C-dist-NNN` alongside the run books, not only into `corpus/dist-features`.

§5's *criteria* still need a yes eventually (they are
what the ten are selected against), but nothing in the generation or A-vs-B analysis waits
for it. If the ten are never assembled, the report is complete except for the "human ten"
listing, and that gap is stated rather than papered over.

## 5. Blind raters — none

Design §8.6 is dropped as a layer. Consequences, which go in the report in plain words:

- The study rests on mechanical measures alone. No human-likeness, readability or
  voice-consistency ratings exist, and no LLM judge substitutes for them (§8.6 forbids the
  substitution explicitly).
- Every quantitative claim is a statement about counted features, not about quality. §10's
  "not a substitute for reading the books" now applies to the whole study, not to a footnote.
- Prompt logging is unaffected, but the report must say the prose was never rated by a reader.

This also removes C-deep's only job (3 excerpts per book for raters). See decision 4.

## 6. "Both" — the default stands until told otherwise

The October 30 note ("with Incunabula, without, and with both") is read as describing the
three-arm comparison, not a fourth arm. Generation proceeds on 20 A + 20 B + 10 C = 50. A
fourth arm after generation would change the book count and the premise pairing, so if it is
wanted it has to arrive before Arm A starts, not midway.

## 7. Executing AI — DeepSeek runs the study

This agent runs: premise freeze and sign-off, model and settings freeze, manifest,
extraction, analysis, candidate checks, report. Drafting is delegated to subagents running
Gemini 3.8 Flash on Kalie's Google Antigravity subscription.

The subagent layer, not the raw Gemini API, is what the study talks to. Two properties of it
must be confirmed before the first Arm A book, because decisions 1 and O3 depend on them:
whether sampling parameters (temperature, top-p) can be set per call or are fixed by the
harness, and whether each response returns the responding `modelVersion`. If either is
unavailable, the answer is to record what is actually applied and label the rows accordingly
— not to write the value we wished for. Two consequences the route imposes, both of which are protocol, not
preference:

1. **DeepSeek cannot log prompts it did not see.** §3 requires the exact opening prompt and
   every continuation prompt per Arm A book, and §4 requires the pipeline's phase log per
   Arm B book. The dispatch layer must write those logs at call time and hand them back with
   the text. Reconstructed prompts are not logs, and a book filed without them fails
   `manifest.py --check`.
2. **One fresh subagent per book, no shared context across books or arms.** Subagents that
   inherit a conversation share vocabulary — names, similes, openings — which is precisely
   what §8.4 and §8.5 measure. A shared context would manufacture the cross-book reuse the
   study is trying to detect, in either direction (inflating it in Arm A, suppressing it in
   Arm B). Arm A additionally must be a single naive conversation per book: continuations
   only in the §3 wording, no reminders, no restated premise, no style notes.

   Enforcement rather than trust, because a rule kept by memory fails silently: at filing
   time `run/dispatch.py` compares each book's opening sentence with every book already
   filed in the same arm (skipping a pair that shares a premise, where a shared opener is
   ambiguous) and refuses the filing when they match.   An inherited context hands over
   openings first and openings are the least premise-determined sentence in a book, so a
   match across different premises is the cheapest detectable sign of the leak. The first
   measurement found the gate reading a chapter marker (`CHAPTER I.`) as an opening; 215 of
   5,886 pairs collided on it, and skipping bare heading lines took it to zero. It refuses
   rather than scores, and `--deviation` still files the book — with `opening collides with
   <id>` written into the manifest, so a collision that exists is a logged protocol event
   instead of a silent one.

   A second check covers the reworded opener, since a rule the operator can see is a rule an
   operator can route around: every response is also compared for a **24-word verbatim run
   carrying at least three content words**, against the same arm on a different premise.
   Continuations are checked too; the leak does not wait for the first sentence.

   Both numbers were measured before anything was generated, on C-dist itself — 109
   unrelated human novels, 5,886 pairs, `analysis/check-fp.py`, report in
   `analysis/filing-checks-fp.md`. The measurement changed both gates:

   | gate | first form | measured | shipped | measured |
   |---|---|---|---|---|
   | opening | first sentence, markdown headings skipped | 215 pairs, all `CHAPTER I.` | bare headings skipped too | 0 pairs |
   | passage | 8-word run, ≥3 content words | 435 pairs (7.4%) | 24-word run | 1 pair |

   Eight words was not a defensible threshold: "and for the first time in her life" clears
   it, and 102 of 109 books would have been refused at least once.   At 24 the single survivor
   is a long scripture quotation shared by two novels — a real coincidence, of the kind
   `--deviation` exists for. A leaked context reproduces paragraphs, so the longer bar costs
   almost no sensitivity. It prints the passages and never scores them, because the decision
   it forces takes a human one glance.

   The human corpus cannot see the second channel — two premises that already share wording
   give their books a legitimate reason to share it — so that is measured on the inputs
   themselves (`analysis/filing-checks-premises.md`): **0 of 780** premise pairs collide on
   an opening or on an 8-word run, let alone a 24-word one, and a duplicated premise is
   flagged by the same loop, so the zero is a measurement rather than an untested blank. No
   book pair is seeded with text the gate would refuse.


Sequence is unchanged: §12.1–7 confirmed (this file) → premises signed off → model and
settings frozen → feature list frozen → Arm A → Arm B → extraction → analysis. Arm C is
already built at n=109; the ten come later per decision 4.

## Open items not among the seven

| id | item | blocks |
|---|---|---|
| O3 | temperature / top-p / system prompt per arm (likely harness-fixed on Antigravity: record what is applied, not what was requested) | the §7 freeze |
| O4 | fourth arm, if "both" meant something | book count and premise pairing |
| O5 | review-sheet deviations D6 (66–91-word premises vs §6's 100–200), D7a (no person names), D7b (no tone/ending fields) | premise sign-off only |

No §12 answer is now outstanding. What is left before the first Arm A word is the premise
sign-off (O5), and the two facts about the Antigravity harness (O3) that decide what gets
recorded on each row.
