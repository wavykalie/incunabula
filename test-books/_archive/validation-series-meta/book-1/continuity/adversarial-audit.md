# Phase 4 — Adversarial Audit

**Run:** 2026-09-22
**Manuscript:** all seven chapters. 15,543 words when this audit ran; 15,531 after the `AUTH` pass that closed `AUTH-1` and `AUTH-2` (see Part 4).
**Inputs:** `continuity/manuscript-audit.md` (Phase 5.6, 2 CRITICAL fixed), `reader-personas.md`
(Phase 1.5, run late this session), the prose gate result (7/7 PASS), `CANON_LEDGER.yaml` (no open
conflicts), `voice-dna.md`, `foundation.md`.
**Mandate:** structural criticism before score; cut, merge, reorder or rewrite when needed.

**Gate compliance:**
- **MAINTENANCE GATE — met.** Zero unresolved ledger conflicts. Both ledgers parse. No canon was
  rewritten to make this audit pass.
- **PROSE GATE — met and correctly weighted.** All seven chapters pass the scanner. Per the phase
  definition, *"a passing scan is never evidence that the prose is good"* — so the pass is recorded
  as an input, not as a finding.

---

## Part 1 — Structural criticism

Ordered by how much they would change the book if acted on. The first three are the audit's actual
positions; the last three are recorded disagreements with the foundation that the audit does not
recommend acting on.

### S-1 — The book's arc sits on two beats, and both are in the last chapter. **Accepted risk, not a defect.**

`CRIT-002`/`D-1` moved the growth out of a decision and into an *act of looking*. The consequence,
flagged at the time, is that ch.7's two small acknowledgement beats now carry the entire arc, and
with no decision the book can read as fatalism.

Reading the drafted ch.7 against that worry: **the risk is real but smaller than predicted, and the
reason is a beat nobody planned.** Ch.7 contains an unplanned counterweight — Merope's admission
that she has been narrating the piloting as hers for the whole book (*"she flies it, she has always
flown it, and I narrate as though I do… you have had the whole of it from me in the wrong voice"*).
That is a **second** act of looking, aimed at herself rather than at Achird, and it is the thing that
stops the ending from being fatalism: she was carried, yes, but she *notices* she was carried, and
she says so out loud instead of performing. Passive protagonist, active narrator.

**Disposition: no change.** The counterweight is load-bearing; the audit's recommendation is that it
is protected through any further revision, not trimmed as a digression. Flagged here so a future
editor does not cut it as self-indulgence.

### S-2 — Movement II is three consecutive chapters of the same discovery. **Accepted, with one merge considered and rejected.**

Ch.3 (the happiness, with the dismissed stone), ch.4 (the belongings), ch.5 (what the beings are)
each end with Merope not understanding something Achird has correctly identified. That is the design —
*"the middle of the book is her unable to be heard"* — but it means three chapters in a row where the
protagonist's function is to be wrong.

Considered: **merging ch.3's discovery into ch.4**, which would compress the refusal-to-look into the
shelf scene and raise the pace. **Rejected** on two grounds. First, `CRIT-003` established that
Merope must look at and dismiss the stone *before* she can recognise it on the shelf; merging the two
would make the recognition self-evident and kill it. Second, ch.3 is the book's only genuinely happy
chapter, and the happiness is the mechanism — a reader who is not enjoying the stay has not been
placed where the horror needs them.

**Disposition: no change.** Recorded because the merge is the most plausible structural cut anyone
will propose, and it is wrong for a reason that is now written down.

### S-3 — Ch.3 is the sag risk and it is the chapter with the least margin. **Watch item.**

Deliberately the most pleasant chapter, and therefore the one that fails if the dread is not visible
*to the reader* while invisible to the narrator. Re-reading it: the dread surfaces three times —
the stone dismissed, *"I forgot about it within the hour"*, and Achird's *"There is something in the
growth that did not grow"* narrated over. That is sufficient, and it is the minimum sufficient. This
is the chapter most likely to lose the primary reader (Nadia) if read as sincere, and it has no slack.

**Disposition: no change.** Recorded as the chapter to protect in any future line-level pass.

### S-4 — *Recorded disagreement, not recommended:* the beings are never individualised.

The audit's honest objection is that a collective with no individual member and no spokesperson
(`R-006`, decision C) is the book's most original choice *and* its biggest commercial tax: no being
can ever have a line that lands, so the middle of the book has no secondary character to love.

**Recommendation: do not fix.** Decision C is a user decision and the reason the book does not
resemble its reference. The objection is recorded because it is the most likely note from a
professional editor, and the answer is a deliberate one rather than an oversight.

### S-5 — *Recorded disagreement, not recommended:* Merope's physical appearance was unestablished.

> **CLOSED 2026-09-22.** The author supplied both leads' appearance, so this is no longer an objection.
> See `character-design-brief.md` and the `AUTH-5` row in Part 4. Left in place as the record of what
> the audit found at the time.

`ENTITY_STATE.open_questions` carries this. A first-person narrator who is described by nobody never
gets a body. This is defensible in the register and it is a blocker for any cover or illustration
brief — which is why it is carried as an open question into Phase 7 rather than resolved by invention.

### S-6 — *Recorded disagreement, not recommended:* the title set is still empty.

Titles remain `deferred`; the author has selected a working title for the validation build. Recorded
as an open item, not a finding.

---

## Part 2 — Four-reader simulation

Each persona from `reader-personas.md` simulated against the finished manuscript, answering that
persona's own diagnostic question. The hostile reader is reported first because it is the one that
decides whether the book survives.

### HOSTILE READER — Priya, 33 — **converted, at ch.4, exactly where predicted**

- **Objection on entry:** "short quiet-SF novella from an AI pipeline, coasting on register."
- **Abandonment point:** she did not abandon. She came closest at **ch.2**, which she reports as the
  weakest chapter for her — *"two pleasant days in a row where the point is that it's pleasant"* —
  and stayed because the being's *"We are glad you came"* reads to her as a non-answer rather than
  as warmth, which told her the book was in control.
- **Conversion:** ch.4 at *"I was happy that my things were on the shelf with the others."* Her note:
  *"It lets her be awful with no comment. I did not expect that from a book this gentle."*
- **Test question — what would she screenshot?** Two things, and the second is the important one.
  The shelf line. And then — after finishing — she re-read ch.2 to check, found the being's pause-free
  *"Not ours"* and Achird's *"the same each time"* measurement, and screenshotted **the reveal's
  receipt in ch.2**. That retroactive verification is the highest-value share this book can generate
  and it is the thing that converts a hostile reviewer into a recommender.
- **Verdict:** converted. **This persona is the book's best evidence, and it is the persona most at
  risk from the pipeline's own vocabulary — `CONT-004` ("packet") was removed in part for her.**

### PRIMARY READER — Nadia, 27 — **engaged; the trust never breaks; two craft irritants**

- **Test question — where does she stop trusting the narrator?** She does not, and the audit can name
  why: the narrator's untrustworthiness is **structural, not teased**. Ch.1 opens with *"I have been
  looked at before"* and immediately admits the agenda (*"accuracy is one of the few things I have
  that nobody gave me"*). Nadia's deal-breaker is a reliable-and-nice narrator; this one announces
  her own performance in the first three paragraphs.
- **Emotional engagement:** high, and concentrated on Achird's silence. Her highest-rated moment is
  ch.5's *"She said nothing at all"* rather than any Merope line.
- **Irritant 1:** ch.1's *"I have never yet missed anything I wanted to see"* reads to her as a writer's
  flourish rather than a character's thought — the one line she flagged as performing.
- **Irritant 2:** the metafictional frame (*"this chapter"*, *"this book"*) is inconsistent in
  pressure — used for jokes in ch.1 and seriously in ch.7. She likes it and wants it either committed
  to or rationed.
- **Verdict:** finishes, recomends by passage screenshot, and will notice the structure
  (*"it's told backwards and you never notice"*). **Serviced.**

### STRETCH READER — Marcus, 41 — **does not finish. The book is not for him, and the packaging has to admit it.**

- **Test question — would he finish it?** No. He bails in **ch.3**.
- **Why, precisely:** he needs escalation and ch.3 is deliberately the flat chapter. He reports that
  the counting (Achird, ch.2) is the only thing holding him, and then ch.3 gives him *"the same
  morning happening twice"* with no new information for 2,354 words. A horror reader will read that
  as a structural pause, not as suspense.
- **The bridge failed, and this is the audit's most useful commercial finding:** he was pulled in by
  the *premise* and held by *Achird*, which means **he would finish a book whose POV was Achird's**.
  Merope is his obstacle. That is not a defect in the manuscript — it is a fact about who can be
  sold this book, and it means marketing it to horror readers on the *Annihilation* promise will
  produce DNFs at ch.3.
- **Verdict:** DNF at ch.3. **Do not target this persona in packaging.** Recorded in Phase 7.

### CASUAL READER — Tom, 38 — **finishes in one sitting; the ending is his problem, not the middle**

- (Simulated as the reader who reads once, fast, without analysing: ~8 books a year, bought on the
  blurb and the short length, no interest in structure.)
- **Test question — did he understand what happened?** Yes, and this is a stronger result than
  expected given the reverse-structured ch.5 and the never-stated reveal. He assembled the fact from
  Achird's one sentence (*"Everyone who came here died here. The growth is them"*) and did not need
  the mechanism restated. **The reveal's indirection is not a comprehension risk.**
- **What he did not get:** the sleigh's agency. He read the ending as *"she decided to leave because
  she loved her"*, missing that Merope never chose. That is the exact failure `D-1` predicted.
- **Where he struggled:** ch.5's reverse order. He reports re-reading the first paragraph twice.
- **Verdict:** finishes, enjoys it, mildly misreads the ending. **Acceptable** — the misreading is a
  *warmer* reading than the text, not a colder one, and a cold ending is the greater commercial risk.

### Simulation summary

| Reader | Finishes | Abandons at | Conversion / verdict |
|---|---|---|---|
| **Hostile** (Priya) | **yes** | — (closest: ch.2) | converted at ch.4; best advocate |
| **Primary** (Nadia) | **yes** | — | serviced; two craft irritants |
| **Stretch** (Marcus) | **no** | **ch.3** | not this book; do not target |
| **Casual** (Tom) | yes | — | enjoys it; misreads the sleigh's agency |

**One of four personas does not finish, and the failure is a *targeting* failure rather than a
craft failure** — the book does exactly what it promises and the promise is what repels him.

---

## Part 3 — Anti-AI audit

The scanner's limits are documented in its own output: *mechanical patterns only — cannot see voice,
rhythm, dead metaphor, or one-point dilution.* This section is the part the scanner cannot do.

**Worst three AI tells found by reading, not scanning:**

1. **Pipeline vocabulary in narration** — ch.3's *"the packet of my life"*. Fixed (CONT-004). It is
   ranked first because it is the only finding in the whole audit that a reader could trace back to
   the process rather than to the page.
2. **The one-performing line** — ch.1's *"I have never yet missed anything I wanted to see"*. It is
   the single sentence the primary reader flagged as the writer rather than the character. Reported,
   not changed: it is grammatically in voice and cutting it would cost a beat in the opening.
3. **Symmetry in the closing image** — ch.7's final paragraph returns the bench and *"facing the
   middle of the clearing, where it had always faced, which is where a bench should face if the point
   of a bench is watching whatever comes."* The ch.1 callback is deliberate and good; the trailing
   subordinate clause explains the callback rather than trusting it. The most editorially likely trim
   in the book.

**Systematic patterns searched for and not found:** no "it was not X, it was Y"; no rule-of-three in
the narration outside the capped rate; no adverb clusters; no em-dash appositives beyond the
calibrated density; no summarising closing paragraphs that restate a theme; no narrator-winks; no
metaphor stacking in the horror passages. **The horror is consistently rendered by withholding rather
than by description, which is the hardest version of this to fake and the manuscript does it
throughout.**

---

## Part 4 — Findings that require the author, not the pipeline

| ID | Finding | Why it is not the audit's to decide |
|---|---|---|
| ~~**AUTH-1**~~ | ~~`CONT-010` — ch.6's cruelty line is longer than its speech budget~~ | **CLOSED 2026-09-22.** The contract won on arithmetic, not taste: the budget asks for the *shortest* thing Merope says and the draft gave her the *longest*. Rewritten to 20 words in two clipped sentences; ch.6 re-gated PASS |
| ~~**AUTH-2**~~ | ~~`CONT-001` — restore Achird's shelf act as a shown beat in ch.6, or leave it removed~~ | **CLOSED 2026-09-22 as left removed.** The restore option was investigated and produced a *stronger* answer than the original finding: the shelf is in the camp, over a rise from the clearing, and ch.6 holds Achird in place throughout the confrontation. The act was **impossible** where ch.7 asserted it |
| **AUTH-3** | `CONT-006`, `CONT-011` — ch.5's reverse frame; the two straps | Prose judgement in chapters that would need another pass |
| **AUTH-4** | Book title, chapter titles, series name | Deferred by the author since Phase 2 |
| ~~**AUTH-5**~~ | ~~Merope's and Achird's physical appearance~~ | **CLOSED 2026-09-22** — author-decided. `character-design-brief.md`. Four sub-items were left openly unresolved rather than guessed at; three (`APPEAR-1` busty/full-figured, `APPEAR-2` scorpion-tail braid, `APPEAR-3` a coincidence the author likes) were then **closed by the author** without a word of prose changing. Only `APPEAR-4` is still this pipeline's reading. |
| **AUTH-6** | `CONT-007` — the stay is *weeks* by manuscript implication | Scale of the story's timeline |

---

## Phase 4 gate verdict

**PASSES.** No CRITICAL findings open. Structural criticism completed with no cuts recommended and
three recorded disagreements. Four-reader simulation completed with one non-finisher, whose failure
is a targeting fact. Anti-AI audit completed by reading, with one tell fixed and two reported.

**Handed to Phase 5:** no quality target has been set by the author, which is the phase's activation
condition — see `artifacts/05-barrier-note.md`.
