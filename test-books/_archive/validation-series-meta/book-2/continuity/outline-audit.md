# Outline continuity audit — Book 2 (Phase 2.8)

**Run:** 2026-09-24. **Scope:** `foundation.md`, `outline.md`, `ENTITY_STATE.yaml` (`R-013`–`R-021`), and
the Book 2 additions appended to `../book-1/voice-dna.md`.

**Authority loaded before auditing:** `../CANON_LEDGER.yaml` (series facts, `series_persistent_elements`)
· `../book-1/CANON_LEDGER.yaml` (cl.7 ending state, `achird.speech_budget`, the hand-count) ·
`../book-1/voice-dna.md` · `../book-1/foundation.md` (exclusion rule, writer warnings) ·
`../book-1/continuity/manuscript-audit.md` (what Book 1's own audit found).

**Method:** every claim the outline makes about a Book 1 fact was checked against Book 1's text or
ledger. Every rule marked "inherited" was checked against its **scope**.

**Result: 3 CRITICAL, 4 WARNING, 3 MINOR, 6 CLEARED.** All three CRITICALs are applied below.

---

## CRITICAL

### [CRIT-101] Merope has *already* noticed by the end of Book 1 — the delta as drafted re-runs Book 1

- **Audit:** 3a (knowledge database) · **Location:** `foundation.md → Characters → MEROPE`,
  `outline.md → Movement I`
- **Defect.** Book 1's ch.7 ends with Merope **finally looking at Achird and realising Achird loves
  her** (`../book-1/CANON_LEDGER.yaml → merope.arc`; the arc was rewritten precisely so that the growth
  lives in that realisation). Book 2's foundation as first drafted said she *"notices"* — which reads as
  the same event happening a second time, and would make Book 2's opening a re-run of Book 1's ending.
- **Fix applied.** The delta is restated so that the **noticing is already spent**: what Book 2 adds is
  that knowing it has stopped being something she can leave alone. She noticed; she cannot stop noticing;
  she **tests**. The author's words — *"notices and starts testing her in subtle ways"* — are honoured,
  and the Book 1 ending is honoured at the same time.
- **Applied to:** `foundation.md` (Merope's arc), `outline.md` (Movement I summary, ch.2 beat),
  `ENTITY_STATE.yaml → inherited.CHR-001.book_2_delta`.

### [CRIT-102] Achird's silence timeline is book-1-scoped and was about to be inherited

- **Audit:** 3c (scope discipline) · **Location:** `foundation.md → Characters → ACHIRD`
- **Defect.** Book 1 specifies a per-chapter speech budget — normal through ch.4, stops arguing after
  ch.5, **one sentence** in ch.6, **nothing** in ch.7 (`../book-1/CANON_LEDGER.yaml →
  achird.silence-timeline`; `CONF-002`). That is a **Book 1 outline** artefact, and **`CONF-011` is
  exactly what happens when a book-1 artefact is read as a series rule.** If Book 2 silently inherits
  "she stops speaking," Book 2's ch.6 one-sentence moment and ch.7 silence would be pre-committed by the
  previous book, not by this one.
- **Fix applied.** Book 2 states its own position explicitly, and states what it is **not**: Achird's
  **voice card** is inherited (clipped, attending, no modifiers, escalates quieter never louder);
  the **timeline** is not. Book 2 does not have a silence chapter, and ch.7 is not a silent chapter for
  her — she is quiet, which is not the same thing.
- **Applied to:** `foundation.md → Characters → ACHIRD` (new paragraph), writer warning 9.

### [CRIT-103] `CONF-011`'s corrected rule must actually reach the drafting instructions

- **Audit:** 3d (provenance) · **Location:** `foundation.md`, the voice-dna additions, `outline.md`
- **Defect.** The correction exists in the ledger, but a ledger correction that never reaches the
  drafting contract is a bookkeeping fix, not a canon fix — and `foundation.md`'s writer warnings are what
  the drafting pass obeys. As first drafted, nothing in the drafting instructions said the plain sentence
  was **permitted**; only the ledger did.
- **Fix applied.** The permission is written into the contract in three places: `foundation.md` (delta
  section and warning 9), the Book 2 additions to `voice-dna.md` (Merope's register section), and
  `outline.md` ch.7 (the plain thing is said, once). **Ch.7 now makes a drafting decision** rather than
  obeying a prohibition.
- **Applied to:** all three files.

---

## WARNING

### [WARN-101] The tool's continuity across six chapters is not specified

- **Location:** `outline.md` ch.1–6. The tool is handed over in ch.1 and given back in ch.7; ch.3 says it
  has become heavy and that she never puts it down. **Nothing constrains where it is in ch.4, 5 and 6.**
  A drafting pass could put it down by accident and break ch.3's line.
- **Deferred with rationale, not fixed:** this is a scene-packet-level constraint, and Book 2 is drafting
  without a separate scene-packet pass (Book 1 used one). It is therefore recorded as a standing check in
  `PROJECT_STATE.yaml → decisions` and re-checked by the Phase 5.6 manuscript audit across all seven
  chapters, which is where Book 1's equivalent defect (`CONT-001`) was actually caught.

### [WARN-102] The hand-taking count must not be contradicted

- **Location:** Book 2's draft, wherever a hand is taken. Book 1's ch.7 **states the count** — Achird
  takes Merope's hand four times across Book 1 — so the count is load-bearing
  (`../book-1/CANON_LEDGER.yaml → achird.takes_meropes_hand`, `CONT-002`).
- **Status:** no Book 2 chapter currently plans a hand-take. Recorded so that if one is written, it is
  the fifth and is not narrated as a first or a second. Not a defect yet.

### [WARN-103] "The work" and "the workers" are labels, and the naming rule is narrow

- **Location:** `foundation.md → Naming`, `ENTITY_STATE.yaml → new_in_book_2`.
- **Judgement:** the series rule forbids **naming anything on the planet** — place names, names for the
  beings. It does not forbid ordinary English nouns. "The beings" was Book 1's narration term, and "the
  workers" is the same kind of term. **The rule holds as long as the prose describes rather than names**:
  no proper noun, no title, no name for the work.
- **Action:** recorded as a drafting check. The internal labels `LOC-006`/`COL-002`/`ITM-005` are
  identifiers for us; none of them may appear as a name in prose.

### [WARN-104] The handover must not read as an authority assigning roles

- **Location:** `outline.md` ch.1. `R-018` says **no one directs the work**, but ch.1 has a worker hand
  Merope a tool.
- **Judgement:** intake is not direction. The distinction must survive on the page, and it is easy to lose
  in a line like *"you'll be on this."* **Deferred to drafting with the constraint recorded:** the worker
  hands her the tool because the work needs it held, not because they have decided anything about her.

---

## MINOR

### [MINOR-101] Book 1's `R-001` "no competence cascade" is book-1-scoped, but the spirit applies

`outline.md` ch.2 says Merope is "good at holding." That is not a cascade — she solves nothing — and it
is deliberate. Recorded so a later pass does not flag it as a violation of an inherited rule that was
never series-scoped.

### [MINOR-102] Merope's wrong explanation (ch.5) must be the only explicit reading offered

Book 1's `foundation.md` requires exactly this of ch.5's wrong reading. Book 2 has the same structure, so
the same constraint is restated in `foundation.md → Movement II`. No fix needed; recorded for the
manuscript audit.

### [MINOR-103] `book-2.interval` must not leak into narration

The gap between the books is not dated. Any incidental time reference in Book 2's prose (a season, a
duration, "since then") would be a continuity defect against an author decision. Recorded as a
manuscript-audit check.

---

## CLEARED

| # | Check | Verdict |
|---|---|---|
| 1 | **Exclusion rule** — is Book 2 a trap book? | **CLEARED.** `R-015` is load-bearing and `foundation.md` checks every chapter against it. The place does not take, keep or absorb anyone, and no chapter turns leaving into a rescue. |
| 2 | **`COL-001` does not appear** | **CLEARED.** No chapter references the beings, and the voice-dna additions explicitly quarantine their card. |
| 3 | **No host / no spokesperson** (`R-018`) | **CLEARED.** The workers are explicitly barred from being spokespeople in `R-019` and in the new anti-pattern list. |
| 4 | **Naming rule** | **CLEARED** (see WARN-103). |
| 5 | **Vehicle continuity** — the sleigh's steed is `Scorpius` from Book 1's ending, Achird pilots, Merope narrates as though she does | **CLEARED.** Restated in `foundation.md`. |
| 6 | **Theme never stated** | **CLEARED.** Six separate drafting instructions say so, including one aimed at the workers, who are the likeliest leakers. |

---

## Gate

**Phase 2.8: GATE CLEARED.** Three CRITICALs found and applied; four warnings and three minors recorded
with owners. Nothing blocks Phase 3.

The count is not a compliment to the outline. It is the same finding as Book 1's: **the outline stage is
where book-scope rules get mistaken for series rules**, and it is cheaper to catch here than in prose.
Book 1's own Phase 2.8 audit found `CRIT-001` (Achird's silence specified four incompatible ways) and
Book 2's has found `CRIT-102`, which is the same rule mis-scoped *in the other direction*.
