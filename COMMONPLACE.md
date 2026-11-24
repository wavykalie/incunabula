# COMMONPLACE — the taste ledger

A writer's commonplace book: what was chosen, why, and what the readers said. This is the
taste channel's ledger (`SELF_IMPROVEMENT.md` §2). Like `ERRATA.md` it is **append-only**;
an entry that turns out wrong gets a `WRONG` line under it and the wrongness stays visible.

The distinction that keeps this file from becoming a rule book: **nothing here is
enforced.** `decisions` and `emergent` preferences are guidance the next book reads at
intake and may decline with a reason — and that decline is itself an entry. A gate reads
nothing in this file. The moment something here returns non-zero, it has become a
threshold and belongs in `ERRATA.md` instead, behind the corpus rule.

## Entry types

### `decision` — the atomic unit of taste

One real editorial choice, made between named alternatives, with the reason. Not
"the chapter went well" — a fork where another road was visible.

```
### YYYY-MM-DD — decision — one line naming the choice
- **book:**    which project
- **chose:**   what was done
- **over:**    what was declined, as specifically as possible
- **reason:**  why, in the author's terms
- **source:**  who decided — author | agent | prompted by the author
```

### `preference` — distilled taste

```
### YYYY-MM-DD — preference — one line stating the preference
- **status:**  emergent | declared
- **from:**    the decision entries it was distilled from (>= 3), or the author's hand
- **reason:**  why it generalises past the cases seen so far
- **limit:**   the case where it should be declined — every preference needs one
```

`declared` preferences live in `USER_PREFERENCES.md`, are written only by the author, and
are immutable to the loop. `emergent` preferences are distilled here from three agreeing
decisions, never enforced, and may be revised by later entries.

### `outcome` — what the readers did

```
### YYYY-MM-DD — outcome — book and signal
- **predicted:** the First Impression / Standing Type claim, verbatim, as recorded before publication
- **actual:**    sales, reviews, blind-read verdicts — verbatim where possible
- **error:**     where the prediction was wrong, stated plainly
- **lesson:**    what this falsifies, or "none yet"
```

Bad reviews are entered verbatim. Paraphrase is how evidence becomes flattering.

### `promotion` — a change the loop adopted

```
### YYYY-MM-DD — promotion — what changed and on which surface
- **surface:**  craft | measurement | taste
- **hypothesis:** what it was supposed to improve
- **verifiers:** each stack result, including SKIPPED and failures
- **reverts:**  how to undo it, and what monitor would trigger the undo
```


---

## The ledger

### 2026-11-06 — promotion — the editor-guide candidate set, adopted in hand mode

- **surface:**  craft — `skills/incunabula/SKILL.md`, `skills/quoin`, `skills/setting`,
  `skills/voice-matrix`, `skills/forme`, `skills/collator`, `skills/case-keeper`,
  `skills/composing`, `skills/reader-swarm`, `skills/bestseller-studio`,
  `DRAFTING_FRAMEWORK.md`, `PROGRAM_MAP.md`, `tools/phase-map.yaml`
- **hypothesis:** the 2026-11-06 editor guide's candidates — a diagnostic quoin instead of a
  per-chapter quota, disorder assigned as devices rather than carried as a checklist, one
  variety rule, banded scores, a tic list that marks which rows are measurements, open
  exposition carriers, multi-scene chapters, a story spine, and a declared profile for layered
  books. Each candidate's own hypothesis and expected effect are in `EDITOR_GUIDE.md`.
- **verifiers:** freeze — no frozen tool was edited, so `verify-freeze.sh` was not re-run;
  controls — not run; catalogue regression — **SKIPPED**; held-out comparison — **SKIPPED**;
  proof-panel — **SKIPPED**. Adopted on the editor's instruction, which is a `hand`-mode act
  under §3, not a stack that passed.
- **reverts:** `git revert` of the rollout commit restores the previous text. No attribution
  record, freeze manifest, `BOOKS.yaml` entry or archived skill was touched.

**No taste entries yet.** The promotion above is a change record, not taste: taste starts
empty and fills from your own choices, and a preference written before the decisions that
earn it is a preference nobody tested.

Three things to know before the first entry:

- A `decision` is recorded every time a real fork was visible, with the reason.
- A `preference` is distilled only at **three agreeing decisions**, and it is written
  `emergent` — guidance a later book may decline with a reason, never a rule.
- An `outcome` is recorded when readers land, against a prediction made **before**
  publication. Prediction error is the only signal here that comes from outside.

`tools/press-ledger` appends to this file at the end of a session. If a book is
drafted under a ductus, its decisions go to that voice's own ledger instead
(`ductus/<slug>/COMMONPLACE.md`), and nothing crosses except a dated merge in
`ductus/PROMOTIONS.md`.

### 2026-11-24 — decision — scrap The Down, the world engine under it, and the hand that grew from it

- **book:**    the-down/book-1 (*A Thousand Terms*). Scrapped by the author 2026-11-24; the
  book tree, its canon ledger and its voice layers are deleted. The framework built while
  diagnosing it is in commit `cb30ad9` and still stands.
- **chose:**   scrap the world, the book, and the series layer; keep the Game Master hand,
  unassigned, for a book that does not exist yet.
- **over:**    rebuilding the world on the same engine; keeping the debt engine and repairing
  the prose; renaming the engine and continuing.
- **reason:**  the author's verdict, *"I want to scrap this idea"*, arrived after the
  diagnosis and is consistent with it. Nothing about the prose was fixable at the line
  level, and the author had already paid for that lesson twice.
- **source:**  author, prompted by the agent's report that the voice had been authored inside
  the rejected world.

**What the diagnosis was.** Three world engines were built before the author saw one they
wanted: the Dig, the Arena, and the Hunger — all three of them replacements for a fourth, the
debt-and-asset engine the book was first founded on, in which the family were collateral on a
surety their ancestor signed, and cleared terms were standing that bought shares that bought a
charter. The author rejected that engine and the clerk narrator built to carry it, on the
grounds that *"the author should not take the shape of a device the story casts."* The
replacement hand was written while the old engine was still canon, and inherited it in three
different places: a reason-for-being sentence about obligation, a ladder of standing to
charter to seat, and five abstract stats with a Writ for an epigraph. The register could not be
repaired by tuning it, because the defect was upstream of the sentence: the vocabulary of a
world about documents becomes the syntax of anyone who narrates it.

**What survives.** The world gate (W1–W4: three candidate engines, each with three concrete
costs, before any artifact is written), the blind packet, `fresh-eyes.md`, the rename of
*contract* to *specification* across every skill and `ductus.py`, and the hand itself. Of the
hand, the rules that were never about the Kasks: no fudged roll; two tells before a trap; at a
death the sentence gets shorter; a class is shown before it is named; no device inside the
story speaking for the author.

**Do not rebuild.** The debt/market engine — collateral, surety, yield, charter, Concord,
Assay, the Writ — and the Clerk narrator (`sabel-rook`, removed 2026-11-23). Both are recorded
as discarded in `ductus/game-master/COMMONPLACE.md`. A future intake that proposes a LitRPG
about inherited obligation owes this record a reason why it is wrong.

**What would have caught it.** Nothing at the line level; a gate at the world, before any
prose. It exists now, and it is why this cost one session instead of a manuscript.
