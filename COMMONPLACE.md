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

**No entries yet.** Taste starts empty and fills from your own choices; a preference
written before the decisions that earn it is a preference nobody tested.

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
