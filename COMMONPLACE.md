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

## Seeded from the record so far

### 2026-09-28 — decision — rewrite the prose, not the instrument
- **book:**  validation-series (Merope)
- **chose:** rewrote a sentence to be unambiguous after A18 flagged a genuine non-gerund as a gerund litany
- **over:**  waiving the row, or relaxing the gate to accommodate the author's rhythm
- **reason:** frozen instruments do not accommodate one author's rhythm; the false positive had a real cause and the prose could carry the meaning without the ambiguity
- **source:** agent proposed, author accepted (recorded as KF-003)

### 2026-09-28 — decision — names are chosen at planning and fixed before prose
- **book:**  demo-galactic (naming phase), then marrow-light
- **chose:** hand-derived thematic names (St Swithin's Day, *hesper*, *parr*, *anstice*, one deliberately plain), and at cast declaration renamed Wren and Delphine at planning time to clear the name gate
- **over:**  letting the model name characters in the draft and filtering afterwards
- **reason:** names should carry meaning, and the right place for that judgment is planning — where a rename costs a line, not a chapter
- **source:** author's declared preference, exercised by the agent

### 2026-09-28 — preference — the gate filters defaults; meaning is not its question
- **status:** declared (see `USER_PREFERENCES.md` §1 and `GATE_FREEZE.md`, Freeze 4)
- **from:**  the demo-galactic naming run, where a filtered set and a judged set produced the same verdict by different mechanisms
- **reason:** "did the model reach for this?" and "did someone choose this?" are different questions and neither can answer the other's
- **limit:**  a character who needs a plain name gets one; thematic naming is never a program rule

### 2026-09-30 — outcome — Hollow Bridge: no prediction was recorded
- **predicted:** none. First Impression and Standing Type were not recorded before publication.
- **actual:** published, live on Amazon 2026-09-22. No sales or review data has been entered here.
- **error:** the prediction channel did not exist when this book shipped. That is the data the loop most needs and cannot recover.
- **lesson:** from the next book onward, both indices are recorded here at delivery, before publication. This entry stays as the reminder of what skipping it costs.

---

## Reading order at intake

1. `SELF_IMPROVEMENT.md` §2 — the firewall, so nothing here is mistaken for a rule.
2. This file, newest first — what has been chosen, and what the readers have said.
3. `USER_PREFERENCES.md` if present — declared taste, held as guidance.

At check-out, append `decision` and `outcome` entries; distill `emergent` preferences
only at three agreeing decisions; write `promotion` entries only through the verifier
stack. The loop's own bookkeeping is subject to the same rule as everything else here:
a record that was never seen being written is not evidence.

### 2026-09-30 — decision — chapter-end Guidance is apparatus, not prose
- **book:**  sons-of-heaven-v2
- **chose:** each chapter closes with a `## Guidance` block distilled from that chapter's own material, written to be quiet to every frozen row (no coda formula, no signature frame, no listicle pattern)
- **over:** weaving the counsel into the narrative; a book-end summary chapter; formulaic "takeaways" lists
- **reason:** the nonfiction reader wants the usable thing at the chapter's edge, and the narrative earns it first; keeping it as visibly separate apparatus preserves both the prose and the instrument's meaning
- **source:** author directed the apparatus, agent designed the quiet form

### 2026-09-30 — decision — reader-facing lines must unpack their own reference
- **book:**  sons-of-heaven-v2
- **chose:** rewrote "Read the Tuesday / an unfiled Tuesday" as "Judge by the paperwork", with the reference spelled out
- **over:** keeping the compressed insider phrasing
- **reason:** the author asked what it meant; a guidance line that needs the chapter remembered has failed at the one job it has. Compression is for the narrative, where the referent is in the reader's hands
- **source:** author, by asking the question

### 2026-09-30 — decision — a contract breach is carried, not padded
- **book:**  marrow-light
- **chose:** resolved the 21,931-word L1 shortfall by the author's option 3: carry the failure in FINISHED.md as fact, floor unmoved
- **over:** expanding short chapters to the number (the named padding failure), or quietly re-declaring the floor after the result was visible
- **reason:** the outline records all 45 rows written, so no genuine material is missing; the author delegated the decision but did not authorise a lie about why the book is short. A recorded miss is evidence; a padded pass is contamination
- **source:** author delegated 2026-09-30; agent resolved within the author's own three options

### 2026-09-30 — decision — the pilot's numbers are the evidence, not a defect to edit
- **book:**  muzzle-and-marrow
- **chose:** left the chapter lengths untouched; U1 (CV 12.1%) and L1 (5,314 short) carried as the pilot's findings in FINISHED.md
- **over:** expanding or compressing chapters to land in the U1 band, or padding to the floor
- **reason:** this is the only book drafted from scratch under the framework; its measured result is what it exists to produce. Editing the before-state destroys the measurement, which is the maintenance-protocol lesson wearing a different hat
- **source:** agent proposed, framework's own recorded position ("recorded, not repaired") confirms

### 2026-09-30 — preference — spoken formulas are voice; narrative formulas are tic
- **status:** emergent
- **from:** marrow-light ch07 ("which is why I need to be—", left), muzzle-and-marrow ch07 ("a door to/of the centre", left), muzzle-and-marrow ch08 ("it is not closed because of me", left); against 23 narrative formulas rewritten across both books
- **reason:** a character is allowed the antithesis; the narrator reaching for it is the machine's habit. The gate cannot tell the speakers apart, so the reader has to, and the fix is applied at the narrator's desk only
- **limit:** when a character hammers the formula repeatedly, or the formula sits in free indirect discourse where the narrator's voice is the character's, it counts as narrative and gets rewritten
