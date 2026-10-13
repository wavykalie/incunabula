# Collation: pre-draft (plan audit)

**Date:** 2026-09-27 · **Scope:** `premise.md` + `outline.md` + `CANON_LEDGER.yaml` +
`ENTITY_STATE.yaml` · **Chapters reviewed:** none (0 of 30 written)
**Total issues found: 9** — **Critical: 4 | Warning: 3 | Minor: 2**

> **This is an unusual run and the reason is the point.** `/collator` normally audits
> text. There is no text, so it audits the *plan* instead. A plan audit catches
> contradictions that would otherwise be written into 30 chapters and then had to be
> chased back out of all of them. Every finding below is cheap now and expensive later.

**All 4 criticals are load-bearing.** Two of them would have invalidated the book's
ending, and one would have invalidated its protagonist's entire arc. The cost of
running this before Phase 3 rather than after was the whole day's remaining work.

---

## CRITICAL

### [CRIT-001] Rusk's age is impossible in two places at once

- **Audit:** 2d (age tracking) × 1b (character consistency)
- **Location:** `premise.md` §2 · `CANON_LEDGER.yaml` P-001 · `ENTITY_STATE.yaml`
- **Description:** Rusk is **37** in 2025 (born 1988, `ENTITY_STATE.yaml`
  `delphine-rusk.physical.age`). `premise.md` §2 states she was **twenty** in 2019.
  Those cannot both be true — at 37/1988 she was **31** in 2019, not 20. The error is
  an eleven-year contradiction in the protagonist's age at the event that defines her.
- **Compounding:** `premise.md` §2 also says she is "away at university," and
  `CANON_LEDGER.yaml` P-001 says she has "been professionally looking at fires for
  eleven years" — which from 2025 means starting at ~26, i.e. 2014. If she were 20 in
  2019 she would have been 26 in 2025 and could not have eleven years' experience. So
  the age contradiction is not isolated: it drags the career line with it.
- **Suggested fix:** **37 and 31 is correct; "twenty" is the error.** Change
  `premise.md` §2 "she was twenty" → "she was thirty-one", and reframe "nobody asked
  her" to fit a junior investigator rather than a student. This also makes CRIT-002
  coherent (see cascade) and is stronger: a 31-year-old signing a determination about
  a fire in her own mother's street, unsupervised, is *more* damning than a student
  being ignored.
- **Cascade risk:** touches the ch 4 retrospective interior, ch 23, ch 30, and the
  voice matrix's "eleven years" line. All are consistent with 31/37; none is
  consistent with 20.

### [CRIT-002] "She signed nothing" contradicts her being the last name on the file

- **Audit:** 5d (contradictory plot points) × 3b (information flow)
- **Location:** `premise.md` §2 · `outline.md` ch 23, ch 30 · ledger item 14
- **Description:** `premise.md` §2 says, of the 2019 determination: *"She signed
  nothing — she was twenty and nobody asked her."* But the outline ends the book with
  **"the name on it is hers"** (ch 30, on the reopened homicide file), ch 23 has her
  *"sign her own complicity out loud,"* and clue-ledger item 14 is *"Rusk's own 2019
  signature on a determination she never read."* Three artifacts say she signed; the
  premise says she didn't. **This is the book's ending.** It cannot be both.
- **Suggested fix:** **she signed it.** Rewrite `premise.md` §2 to: she was 31, a
  junior investigator, she signed the 2019 determination because the circuit reference
  was on the form and nobody asked her to check it, and nobody asked her because
  nobody asks the person whose mother's street it is. This makes CRIT-001 resolve
  cleanly, gives ch 23 and ch 30 a foundation instead of a gesture, and *strengthens*
  the A8 concession — closure on the protagonist requires her to have done something
  on the page, and "signed nothing" gives a reader nothing to close.
- **Cascade risk:** fixes CRIT-001 at the same time. Must re-check ch 4 (she has read
  it four hundred times) — which only makes sense if she signed it.

### [CRIT-003] The Friday deadline passes six days in; the outline spends sixteen

- **Audit:** 2b (logical sequence)
- **Location:** `outline.md` ch 9, ch 18, ch 22, ch 26
- **Description:** Ch 9 establishes the county wants it closed **"Friday. Six
  days."** From ch 1 that puts the deadline at **day 6**. But the book's centre of
  gravity is much later: all 15 ledger items are planted by **ch 18** and **the name
  is stated at ch 22**. Ch 26 then says the investigation *"reopens"* and that *"there
  is no deadline."* The outline therefore runs roughly sixteen days of story past a
  deadline that was the engine of the first act — **and never shows the deadline
  arriving or being missed.** The reader is given a countdown in ch 9 and it silently
  evaporates.
- **Why this is critical and not a warning:** F5 is the finding that A8 was conceded
  over — the trade reporting says readers want closure, and the Tudor comp failed at
  the 80% mark. A reader who was given a six-day clock in ch 9 and is still reading
  at ch 22 without being told what happened on Friday has been actively taught not to
  trust the book. This is precisely the "great premise, underwhelming execution"
  failure mode the research identified.
- **Suggested fix:** **make the deadline land, and make its failure a scene.** Insert
  the deadline *passing* as the event that ends Act II and opens Act III — ch 13/14
  boundary. The county closes the file without it; Rusk loses the case's official
  standing; from ch 14 the investigation is unofficial, which is exactly why the
  ensemble hands over their own copies of things in ch 18. **This converts a
  structural gap into the book's best turn**: the town stops pretending the question
  is open and Rusk is the only one still asking. Then ch 26's *"no deadline"* is not a
  quiet change, it is the resolution of ch 13.
- **Cascade risk:** touches ch 9 (extend the beat), ch 13, ch 14, ch 18, ch 26. Recompute
  the day numbers; the `ENTITY_STATE.yaml` timeline entries for ch 9/18/22 must be
  updated. No chapter boundary moves and no word count changes.

### [CRIT-004] The 2019 death count is never stated, and CONF-004 depends on it

- **Audit:** 5b (Chekhov audit — setup with no payoff) × 5a (thread inventory)
- **Location:** `premise.md` §2, §3 · `outline.md` ch 22, 24 · `CANON_LEDGER.yaml`
  FACT-008
- **Description:** `CONF-004` sets Terrell as *"responsible but not the killer"* — but
  **for 2019 only**, on the explicit ground that he lit a fire he did not know was
  occupied. That reasoning requires that **people died in 2019**. The outline never
  says how many. It establishes that the 2019 cause of death was not smoke inhalation
  (FACT-008) and that the file becomes a *homicide* file at ch 30, so a death is
  implied — but no chapter states the number, and no chapter shows Terrell learning
  it. The `CANON_LEDGER.yaml` entry for his knowledge flags this as `critical:` and it
  is flagged with no plan behind it.
- **Consequence if undrafted:** the leniency has no basis on the page. Rusk's ch 23
  closure plus an unearned ch 24 softening is exactly the "author protecting the
  antagonist" reading that **R-04 (the Deception Reader) is defined by rejecting** —
  that segment's hard deal-breaker. `CONF-004` would be resolved by the prose instead
  of by the plan, which is the failure mode `A8` was just corrected to avoid.
- **Suggested fix:** state the number explicitly and early, and give Terrell the
  learning as a scene. Recommend **one death in 2019** — it keeps the arithmetic
  small enough to stay with the reader, it makes a *single* death the thing a whole
  town agreed to bury, and it makes Terrell's ch 24 realisation land as a specific
  human being rather than a statistic. Plant the count in ch 4 (Rusk already knows —
  she lived on that street) and put the learning in ch 24, where the motive is laid
  out whole.
- **Cascade risk:** ch 4 (add the fact), ch 10 (Adela's determination becomes a
  specific death, not a category), ch 22 (the charge), ch 24 (the realisation), ch 30
  (homicide file, singular, now earned). No boundary moves.

---

## WARNING

### [WARN-001] Terrell is one year older than his aunt

- **Audit:** 1b · **Location:** `CANON_LEDGER.yaml` P-003, P-004
- **Description:** Cora is 74, Rusk 37 (so Cora had Rusk at 37), Terrell 38. Terrell
  is therefore older than Rusk by a year while being her nephew. It works — Cora's son
  would be ~29 years older than Rusk, and Terrell grew up alongside her — but a reader
  will stumble on it, and it is the kind of detail that gets flagged in a review.
- **Suggested fix:** either age Terrell to 35–36, or make the 1-year gap a stated
  family fact ("he was born ten months before me, which is the sort of thing this
  family mentions"). The second is better: it converts an oddity into characterisation
  and reinforces the entanglement that is the book's whole engine.
- **Cascade risk:** none. Terrell's age appears in one place.

### [WARN-002] Ch 6's "records room" is both ambiguous and the ghost of premise 1

- **Audit:** 5a · **Location:** `outline.md` ch 6 · `premise.md` §2
- **Description:** Ch 6's pull reads *"The room is a **records room**. The one room in
  that house nobody sleeps in. First sight of the 2019 signature."* Two problems.
  First, ambiguity: it is unclear whether this is the 2025 house's room (matching the
  2019 house's room — the signature) or the 2019 house itself. Second, and more
  seriously, **"records room" is premise 1's vocabulary.** Premise 1 was a book about
  filing systems, it was abandoned, and a reader of the *archive* would see the ghost
  of it in the one place the two books' mechanics nearly touch. The thematic point
  survives — a room nobody sleeps in is a room where a decision is *kept* rather than
  lived in — but the noun is wrong.
- **Suggested fix:** rename to a domestic noun with no premise-1 resonance — a
  **study**, a **front room**, a **sealed parlour** — chosen so the room reads as *the
  room where the family kept its paperwork and nobody sat*. Then state explicitly that
  the 2025 house has the same room, which is the actual signature.
- **Cascade risk:** ch 6 only, plus the `ENTITY_STATE.yaml` location fact. Wording
  only; no structural change.

### [WARN-003] Rusk's knowledge of the 2019 determination is assumed at ch 5, established at ch 4

- **Audit:** 3b (forward reference) — pre-flagged by `case-keeper` in SEED mode
- **Location:** `ENTITY_STATE.yaml` `delphine-rusk.knowledge_gap`
- **Description:** Ch 5 has Rusk reason about the 2019 fuel purchase with the intimate
  knowledge of a woman who has read the 2019 determination four hundred times. That
  habit is established by ch 4's retrospective interior. The order is correct **in the
  outline** — but ch 4 is 3,900 words of interior and the beat is load-bearing, so if
  ch 4 runs short or gets cut in revision, ch 5 becomes a forward reference with no
  setup.
- **Suggested fix:** no change to the outline. Carried as a **drafting note on ch 4**:
  the "four hundred times" detail must land, because two later chapters lean on it.
- **Cascade risk:** none if ch 4 is written as planned. Recorded so it is not lost.

---

## MINOR

### [MINOR-001] "Records room" also echoes the working title's ghost

Folded into WARN-002. The directory was renamed away from "A Matter of Record" for
exactly this reason; the outline should not reintroduce the noun in a different room.

### [MINOR-002] Ch 3 covers seven people, ch 14 covers five

- **Audit:** 1e · **Location:** `outline.md` ch 3, ch 14
- **Description:** Ch 3 is an ensemble scatter of seven; ch 14 is five conversations.
  Not a contradiction — different days, different settings, and ch 3's point is the
  *full* roster while ch 14's is the *institution*. But the two chapters carry the same
  structural job (the helpful-togetherness plant, ledger item 13) and a reader may
  notice the echo.
- **Suggested fix:** differentiate their function explicitly in the drafts — ch 3 is
  *faces*, ch 14 is *consequences*. Ch 14's added beat (the independent solve's fix:
  Rusk notices nobody refused her) already does this work. No structural change.

---

## What the plan gets right

Recorded because a collation that only lists faults misrepresents the artifact.

- **The information-flow design is sound.** Rusk's knowledge chain runs in strict
  order: origin pattern (ch 2) → no beds (ch 6) → signature match (ch 8) → cause of
  death (ch 10) → alibi gap (ch 15) → same perpetrator (ch 20) → name (ch 22). No
  character acts on anything they have not been shown. **This is the audit that
  matters most and it passes.**
- **The 15 ledger items are planted before they are paid off, all of them, by ch 18.**
  Independently solved and verified in `research/clue-ledger-solve.md`.
- **No character is in two places at once.** Location logs are clean.
- **Cora/Terrell voice separation is specified before the first line is written**,
  which is the right time and is unusual. `/collator` will re-test it on the text.

---

## Verdict

**Do not draft until CRIT-001 through CRIT-004 are fixed.** All four are in
`premise.md` and `outline.md`; none requires a chapter boundary to move and none
requires a word-count change, so the cost of fixing them is minutes and the cost of
*not* fixing them is a rewrite of Act IV.

**No boundary moves. No target changes. CV stays 38.01%.**

---

## RESOLVED — 2026-09-27, all 9 findings fixed pre-draft

| id | fix | boundary moved? | words changed? |
|---|---|---|---|
| CRIT-001 | `premise.md` §2: "she was twenty… away at university" → "thirty-one, a junior investigator four months into the post." Reframed "nobody asked her" as institutional, not age-based. | no | no |
| CRIT-002 | `premise.md` §2: "She signed nothing" → **"Rusk signed it."** She signs a determination citing a circuit nobody asked her to check. Makes ch 23 and ch 30 *earned* and makes the A8 closure real. | no | no |
| CRIT-003 | The Friday deadline now **lands and fails on the page** at ch 13 (4:40pm, day six). Rusk loses standing. Ch 14's pull becomes "Rusk has no badge for any of this now." Ch 26 reframed: a closed file is not reopened, it is simply *worked* — resolving ch 13 twenty chapters later. | no | no |
| CRIT-004 | **One person died in 2019.** Count planted in ch 4, carried in Adela's canon and FACT-008, and Terrell **learns it on the page at ch 24** — which is what gives CONF-004 its basis. | no | no |
| WARN-001 | Terrell aged 38 → **36**. Two years younger than his aunt, which reads as entanglement rather than error. | no | no |
| WARN-002 | "records room" → **"the study."** Premise 1's ghost noun removed from the one place the two books' mechanics touch. | no | no |
| WARN-003 | No outline change. Carried as a drafting note on ch 4: the "four hundred times" beat is load-bearing for ch 5 and must land. | no | no |
| MINOR-001 | Folded into WARN-002. | no | no |
| MINOR-002 | Differentiated in principle: ch 3 is *faces*, ch 14 is *consequences*. Ch 14's added beat already carries it. | no | no |

**Post-fix verification — `verify_outline.py`, all 8 checks PASS:**

```
30 chapter rows · contiguous 1-30 · sum 91,580 (inside 80,000-95,000)
CV 38.01% (band 33.4-45.1) · min 1,300 (>=1,200 for catchword) ·
0 adjacent-identical structures of 29 boundaries · 17 distinct structures ·
ledger items 1-15 contiguous
```

**The verifier is now a file, not a command I retyped.** `verify_outline.py` was
written because the ad-hoc regex I had been using to check the CV parsed the clue
ledger as chapter rows and reported 77% and a false adjacency failure. A check whose
implementation changes between runs is not a check. It parses only the Act tables by
splitting on the ledger heading, and it exits non-zero on failure.

**Chapters may now be drafted.** CV is unchanged at 38.01% because no chapter moved.
