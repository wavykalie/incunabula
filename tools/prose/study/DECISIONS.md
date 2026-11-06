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

---

## 2026-11-02 — the route does not report a model version (O3)

Measured on A-01's first call through the Antigravity CLI (`agy` 1.4.12), which is the
route §12.1 names. Facts as found, not assumed:

| question | answer | how it was measured |
|---|---|---|
| temperature / top-p settable | no | `--settings '{"temperature":0.7,"topP":0.95}'` returns `Error: --settings: unknown setting "temperature"` |
| system prompt settable | no | the harness supplies one: a 10-token prompt reports 8,732 input tokens |
| the response reports a modelVersion | **no** | `--output-format json` returns only conversation_id, status, response, duration_seconds, num_turns and usage; `stream-json`'s `init.model` echoes the id we sent, which is intent rather than a measurement; nothing is written under `%LOCALAPPDATA%/agy` to consult afterwards |

Consequence, by this file's own §1 rule: **no Arm A or Arm B row can be filed on this
route.** `model_id` would be the id we sent rather than the version that wrote, and H3 is a
claim about the latter. `run/harness.json` records `model_returned: null` and
`run/harness.py --check` refuses it — intended behaviour, not a bug to patch around.

A second, independent blocker surfaced on the same call: headless mode auto-denies tools,
and the model asked for a command instead of answering in text, so `response` came back
empty with `denied_actions: [{"action": "command"}]`. Producing text needs either an
allow-rule under `permissions.allow` or `--dangerously-skip-permissions`, which auto-approves
every tool on this machine. That is a decision for the author, not for the study agent.

`premises/frozen/premises-v1-review.md` was signed off in session on 2026-11-02 before this
call; the premises themselves are unchanged and still hash to `e227039a981d8683…`, so the
sign-off is not invalidated by either finding.

### 2026-11-02 (later) — the author's ruling on the above

Kalie's answer: `gemini-3.8-flash` and `gemini-3.8-flash-high` **are the same model** —
Flash 3.8, with `-high` the effort tier the alias resolves to. So the alias is not a silent
model swap, and the run proceeds. How a row records it:

- `model_sent` stays the frozen literal `gemini-3.8-flash` (the plan's `model_id`, unchanged).
- `model_returned` is the id the route's own resolver logs, `gemini-3.8-flash-high`, with
  `version_source` naming `model_resolver.go:155` and this ruling.
- The report carries one limitation sentence: model identity is the CLI resolver's id, not
  an API-returned `modelVersion`, because the tier is what actually ran.

A mid-run change still surfaces: the resolver logs per call, and `dispatch.py` refuses a
`--model-returned` that disagrees with the probe record unless the change is filed as a
separate sub-cohort. H3 is therefore measured at "Flash 3.8" granularity, not build
granularity, and the report must say so.

Tool access for the drafting call, same ruling: `--dangerously-skip-permissions`, chosen by
the author, because headless auto-denial returns an empty response rather than a text
answer. The grant is for one call in the book's own empty directory.

---

## 2026-11-02 — Arm A filed: 20 books, one row that cannot be re-derived

All twenty Arm A rows are filed: 20 of 20 inside the 54,000–66,000 band (54,198–59,027,
median 55,473), 35–74 chapters, 120 continuations in total, one model id on every row
(`gemini-3.8-flash-high`, per the ruling above), and `manifest.py --check books/manifest.csv`
reports `20 row(s), 0 problem(s), 0 band note(s)`. Two rows need saying out loud.

### A-11 — interrupted, resumed, and filed with a recorded passage collision

A-11's stream died mid-book with two calls on disk and only the opening filed (26,531 words).
It was **resumed, not re-opened**: `run/out/agy/A-11/conversation.txt` holds the opening
call's `conversation_id`, so the book continued its own conversation — a fresh opening would
be a re-roll (§7). Call 02 was then filed after the fact through `dispatch.py`, which refused
it: it shares a 24-word verbatim run with A-14,

> drizzle that had no weight to it the sort of rain that did not fall so much as hang in the
> air until your

Diverging at the next word (`eyebrows` in A-14, `eyelashes` in A-11), one sentence of stock
weather prose, in books that ran in separate conversations with separate working directories.
Filed with `--deviation`, as §8.4 requires: the pair is now a logged event the analysis can
exclude or flag, not a silent one. A-11 finished at 57,193 words in 6 calls.

### A-20 — the filed text is not the concatenation of its responses

Measured after the run, while auditing every row against its own response files:

- `run/out/responses/A-20/01.txt` — the opening — is a **36-word Gemini filter notice**, and
  that is what the log records (`kind: opening`, `response_words: 36`).
- The filed manuscript of 55,570 words opens with prose that **appears in no response file**:
  `# The Tell` / `The dog did not look at the door. He looked at the baseboard four inches to
  the left of the strike plate…`.
- Two passages inside `02.txt` are truncated mid-sentence by the same filter (`…would heat the
  wire to seven hundred degrees Fahrenheit in eight-tenths of a second.` → notice). The
  manuscript carries **different prose at both points** (`thick, stretched taut between the
  threaded terminals like a single, dull strand of copper hair`; `unit, its green pilot lamp
  unlit, its antenna lead coiled neatly around a cardboard core`), and that prose is in no
  response file either.
- Every response file still hashes to the `response_sha256` its log entry recorded, so this is
  not hash drift: the manuscript simply is not what the pipeline appended.
  `dispatch.append_text()` appends verbatim and nothing in `run/` strips a filter notice, and
  no artifact in the repo carries the replacement text.

A reproduction audit now runs over the corpus: each manuscript compared, whitespace-normalised,
against the concatenation of its own filed responses. **19 of 20 reproduce exactly. A-20 does
not** (net 66 words, plus the absent 36-word opening). Its row therefore cannot be re-derived
from the record, which is the one thing every other row can do.

**Ruling (Kalie, 2026-11-02): withdraw it and re-dispatch the frozen payload as a fresh book.**
A row whose text cannot be re-derived from its own responses is not a row, whatever its word
count; the replacement is cheap and the defect is not.

Done, in this order:

1. The attempt was archived, not deleted: `run/out/attempts/A-20-filtered/` holds the book dir,
   the ten response files and the `agy` work dirs, so the finding above stays checkable.
2. Its row was dropped from `books/manifest.csv`, leaving 19 — a withdrawal has to be reflected
   in the record or the record is wrong. This is the only row ever removed, and it is here.
3. Re-dispatched through `run/drive.py` from the **same frozen payload** (`payload_sha256`
   unchanged), which is what keeps the premise pairing intact: the book is new, the input is not.
4. `drive.py` gained a guard, because the cause was not the filter — it was the driver having no
   idea a refusal had arrived. A response containing the filter notice now stops the book:
   as an **opening** it raises `Stop` and files nothing; as a **continuation** it becomes a stall
   note on the row. `--deviation` also passes through to `finalize`, so a replacement row can
   carry its own provenance instead of needing a hand edit of the manifest afterwards.

Outcome: the fresh opening came back as 17,268 words of prose with no notice, and A-20 filed at
**55,948 words, 49 chapters, 7 calls**, its row carrying the withdrawal as its `deviations` text.
Corpus state: **20 rows, 0 problems, 0 band notes; 20 of 20 manuscripts reproduce exactly from
their own response files** (54,198–59,027 words, median 55,473).

---

## 2026-11-03 — `init-book` writes a registry that does not parse, on a fresh tree

The frozen tree's `BOOKS.yaml` declares `books: []`, because books live in `test-books/` and
a clone of this repo has none. `init-book.py` appends each new book as an indented block
item without converting that flow sequence, so the first scaffold produces

```yaml
books: []
  - path: B-01
```

which is not YAML. The registry then holds the book and cannot be read: `ductus.py contract`
answers `BOOKS.yaml is missing or does not parse — the assignment cannot be resolved`, which
is the first thing §3 step 3 asks for, so the run stops before phase 1 with no voice and no
`ductus_id`.

Found on **B-01's scaffold, 2026-11-03** — the first command of the first Arm B book, so
every Arm B book would have met it.

**Fixed as data, not code.** `books: []` → `books:` in the run's worktree leaves the pipeline
byte-identical to `8265c48`; `git status` in that worktree shows only `BOOKS.yaml` and
`books-armb/`, which is what running a book is supposed to change. Patching `init-book.py`
would alter the artifact this arm exists to measure, before a word is drafted, and every B
row's `pipeline_commit` would name a tree that did not write it. The defect is recorded here
and belongs in the fix list for the arm after this one — along with the reason it was not
fixed in place.

The registry now holds one block item, so later books append to a sequence and do not hit
it again; it is a first-book defect, confirmed by B-02 scaffolding cleanly if it does.

---

## 2026-11-03 — the premise ledger ships empty, so phase 1 cannot clear

`check-premise-distinct.py` does the right thing with an empty ledger — it refuses with
exit 2 rather than passing every premise it is shown — and that is exactly what happened on
B-01: `ledger is empty. An empty ledger makes this gate silently pass everything, which is
worse than it not existing.`

Nothing is broken. `PREMISE_LEDGER.tsv` ships empty **by design**: the de-identification pass
removed the author's own unpublished-book premises, because "a public template should not
carry them" (`GATE_FREEZE.md`). The seed survives outside the public tree at
`.private/record/PREMISE_LEDGER.seed.tsv` — three rows, six tab-separated columns, ignored by
`.gitignore`.

Phase 1's exit gates are `comps` and `premise`, so **no Arm B book can clear phase 1 while
the ledger is empty.** The rows were restored into the run's copy only:
`run/out/armb-wt/tools/prose/calibration/PREMISE_LEDGER.tsv` now carries the public file's
comment header unchanged plus the three seed rows. The private premises stay inside
`run/out/`, which is gitignored, and outside git.

It is the same class as `BOOKS.yaml` — **data the pipeline reads, not the pipeline** — but
with a consequence the registry fix did not have. `verify-freeze.sh` **does** hash this
file (manifest row `tools/prose/calibration/PREMISE_LEDGER.tsv`, Freeze 5), so seeding it
turns the verifier from `ok` to

```
calibration/PREMISE_LEDGER.tsv f06f9c4baabc47d5  CHANGED (frozen f4c03a83537f0270)
```

and `preflight.sh` fails on that row — `results would not be attributable`. The committed
blob hashes to `f4c03a83537f0270`, which is what the manifest says; only the run's copy
differs, and only in its data rows.

The empty file is an artifact of de-identification, not a property of the author's
instrument: the hash was recorded against a public template that deliberately carries none
of the author's premises. So the repair is to re-record that **one row** with a dated note
and re-run the verifier — a deliberate, recorded freeze change, not a bypass, and nothing
like switching a gate off. That is the author's ruling to give, so the worktree is left
seeded and no phase has been walked. The alternative, leaving the file empty, means Arm B
has no book that can clear phase 1, because `comps` and `premise` are phase 1's only gates
and one of them refuses by design.

Consequence for the analysis: the distinctness gate compares against three premises, not
against a catalogue. That is the instrument as designed, and every B row's `deviations`
should not need to say anything about it — but a report claiming Arm B was checked for
premise redundancy against a *frozen list* should say the list has three rows in it.

## 2026-11-06 — drafting route moves to the executing agent (cohort `B-deepseek`)

**This changes an answered decision, so it is a dated note rather than a rewrite** (this
file's own rule). Decision 1's answer and decision 7's division of labour are superseded for
`B-16`…`B-20` only. `A-01`…`A-20` and `B-01`…`B-15` keep the route they were drafted on and
are not re-run.

**What forced it.** The Antigravity route is exhausted. Measured on 2026-11-06: the account
served one substantive call (112 s, 11,656 output tokens for a 400-word file), then returned
`429 … Resets in 73h58m` on every further call, on all three Flash tiers. A 60,000-word book
needs at least seven calls of that size, so the route cannot draft one book inside its own
reset window. On the owner's instruction the remaining five premises are drafted by **the
executing agent — DeepSeek V4.1 Flash — in this context**, through the same Incunabula
pipeline at the same frozen commit. Measurement: `ARM_B_SUB_AMENDMENT.md`, 2026-11-06.

**What a `B-deepseek` row can and cannot claim.** It is a new cohort, reported as one. Four
differences, none cosmetic:

1. **Operator and drafter are one context.** The arm's validity rested on their separation: a
   `prose` row was a stop condition precisely because a rescued book measures the rescuer.
   Under this cohort every chapter is a `prose` row by construction, declared in the book's
   `logs/operator.md` rather than hidden. So the cohort cannot support "the pipeline, not a
   person, wrote this". It measures the pipeline's **instructions, gates and repair loop**
   applied by an agent that is also writing the prose — and the report must say exactly that.
2. **No API `modelVersion` exists to record.** O3's rule was "no returned version, no
   filing". The executing agent has no response envelope naming a version, so `model_id`
   records the session's identity string and the row's H3 claim is weaker than a Flash 3.8
   row's. Filed with that written down, not with a version invented to satisfy a check.
3. **`operator_interventions` is not comparable.** It keeps its meaning — counted gate
   answers in the book's log — but nobody outside the drafting context makes them. Recorded,
   never pooled with the fifteen human-operated rows.
4. **Pairing is confounded.** `B-16`…`B-20` against `A-16`…`A-20` compares pipeline-plus-
   DeepSeek against a naive Gemini conversation, so any difference is pipeline **and**
   drafter. The primary result stays n = 15 Flash-high pairs; this cohort is separate and
   never folded into it.

**What did not change.** The frozen commit, the pipeline code, every gate and threshold, the
payload bytes, one-book-at-a-time, and the filing checks. `preflight.py` still validates the
Flash-high probe record and says nothing about this cohort, so each `B-deepseek` row carries
its own probe record (`run/harness-deepseek.json`) and a `deviations` token naming the
cohort — otherwise the manifest would attribute the wrong harness to the text.

**Filing command for these rows:**

```bash
python run/dispatch.py --ingest B-17 --response <final.txt> \
    --sent-model deepseek-v4.1-flash --model-returned deepseek-v4.1-flash \
    --harness run/harness-deepseek.json \
    --pipeline-commit 8265c48d12962ca233ed98bd10083edb072ec7f0 \
    --interventions <counted rows> --finalize \
    --deviation "cohort B-deepseek: operator=drafter (authorised 2026-11-06); model is the executing agent, no API modelVersion"
```
