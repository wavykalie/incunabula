# Phase 5.6 — Manuscript Continuity Audit

**Run:** 2026-09-22
**Scope:** all seven drafted chapters, read end to end against `ENTITY_STATE.yaml` (including its
knowledge states and per-chapter speech budgets), `CANON_LEDGER.yaml` (book + series),
`foundation.md`, and the twelve world rules `R-001..R-012`.
**Trigger:** `continuity.manuscript_check` had been `false` since the project began. It had never run.
**Method:** every claim verified by grep against the files, not from memory. Counts and line numbers
are reproducible.

---

## Headline

**Phase 5.6 had never run. Running it found 2 CRITICAL defects in prose that had already passed the
prose gate on all seven chapters.**

That is the finding that matters most for the run this project exists to perform. The deslop gate is
a *mechanical* check — sentence shape, adverb density, anaphora, negative litany. It cannot see
whether a character was in the room when something happened. A manuscript can be 7-for-7 on the
scanner and still contain a chapter that asserts an act no chapter shows, and a chapter that gets a
character's history wrong by one retelling. This manuscript was, and did.

Both CRITICALs were fixed. Every finding below is recorded with its evidence and its disposition.

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| **CONT-001** | **CRITICAL** | ch.7 asserts an act (`she had put the objects back on the shelf`) that no chapter shows, and it mis-assigns the act away from the beings who performed it | **fixed** — clause removed, original wording preserved |
| **CONT-002** | **CRITICAL** | ch.7 says Achird took Merope's hand "for the second time in her life"; the manuscript shows it three times before that | **fixed** — `second` → `fourth` |
| CONT-003 | MINOR | ch.5 places the curve-discovery "on the first morning" while its own next paragraph says "her first week", and ch.3 places it on day three or later | **fixed** |
| CONT-004 | MINOR (craft) | ch.3 used the word **"packet"** in narration — pipeline vocabulary in the prose | **fixed** |
| CONT-005 | MINOR | ch.1 `WARN-003`, an open warning whose named trigger was "the ch.1 polish pass" — that pass is this one | **fixed** |
| CONT-006 | MINOR | ch.5's reverse-frame says the palm-wipe was "described already" before the description arrives | **reported** |
| CONT-007 | MINOR | `weeks` in ch.5/6/7 closes an open question (`T-008`) by implication rather than by decision | **reported, recorded** |
| CONT-008 | STATE | `ITM-001`'s recorded form is stale and contradicted by three chapters | **fixed in ENTITY_STATE** |
| CONT-009 | STATE | the ch.3 curve → ch.5 buried strap-end has no entity ID at all | **fixed in ENTITY_STATE — new `ITM-004`** |
| CONT-010 | WARNING | ch.6's cruelty line does not match its own speech budget | **fixed 2026-09-22 — the line was rewritten** |
| CONT-011 | MINOR | ch.4's shelf holds "a strap"; ch.5's buried object is "the end of a strap" — two different straps, one word | **reported** |

**Gate verdict: FAILED on discovery (2 CRITICAL), PASSES after the applied fixes.**

---

## CONT-001 — CRITICAL — the shelf act has no author

**Location:** `chapter-07.md:65`

> She had just done the thing. That is what I was looking at. **She had put the objects back on the
> shelf** and taken me by the hand for the second time in her life and walked me to a sleigh…

**Why it is a defect, not a style choice.** Three independent problems, all verifiable:

1. **The act is nowhere in the manuscript.** `grep -ni objects` across all seven chapters returns
   exactly two hits: `chapter-06.md:41` ("I listed the objects" — Merope's list) and this line.
   Achird is never shown handling the shelf. The only departure action she performs on the page is
   `chapter-06.md:119`: *"she put her hand on the side of it"* — the sleigh.
2. **It contradicts the agency established in ch.4.** Ch.4 is explicit that *the beings* placed
   Merope's things on the shelf: *"they put them out, somebody put them out with the rest"*
   (`chapter-04.md:125`), and the whole of ch.4:77–81 is the beings moving shelf items around a room
   they know. An act attributed to Achird in ch.7 belongs to the beings in ch.4.
3. **It destabilises ch.4's load-bearing beat.** Ch.4's payoff is *"I was happy that my things were
   on the shelf with the others"* (`chapter-04.md:131`) — Merope is delighted by an arrangement she
   did not make. If Achird subsequently collects and returns those objects, the arrangement was
   something Merope's companion curated, and the beat loses the thing that makes it awful.

**Applied fix** (minimal, meaning-preserving, removes a false claim rather than adding a new one):

```
- She had put the objects back on the shelf and taken me by the hand for the second time in her life…
+ She had taken me by the hand for the fourth time in her life…
```

**Writer's note, and the reason this is flagged rather than buried.** The original line reads like the
remnant of an *intended* beat: Achird returning Merope's things instead of taking them, a wordless
renunciation of the place's claim. If that was the intent it is a good beat and it is currently
unearned. Two ways to restore it, both requiring an author decision because both add an act to the
story:

- ~~**Option A — show it.** One wordless sentence in ch.6, where Achird crosses the clearing: she stops
  at the shelf, puts Merope's button and the stone back, and goes on.~~ **CLOSED AS IMPOSSIBLE, 2026-09-22.**
  See the geography finding below.
- **Option B — leave it removed. ADOPTED 2026-09-22.**

### AUTH-2 closed: the act was not merely unshown, it was impossible where it was said to happen

Re-examining the option to show it turned up a harder fact than the original finding. **The shelf is
not in the clearing.** Ch.4 puts the camp out past the far edge of the growth and over a rise —
*"She walked me out past the far edge of the growth, where I had never gone"* (`chapter-04.md:5`),
*"The ground went up… and down into a place I had not seen"* (`:15`) — and the departure in ch.6/ch.7
happens in the clearing. Worse, ch.6 keeps Achird physically in place for the whole confrontation
(*"She stood there."*, *"She said nothing."*, repeated through the scene), so she never leaves and
comes back.

So the clause could not have occurred when ch.7 said it did (*"She had **just** done the thing"*).
That moves the finding from *unsupported* to **impossible**, and it means showing it in ch.6 as
originally proposed would require teleporting the shelf into the clearing. **Leaving it removed is
therefore not the cautious option; it is the correct one.**

**If the beat is wanted**, it belongs in an *earlier* scene — a short passage where Achird goes up to
the camp alone and retrieves Merope's things, establishing that she refuses to leave them with the
dead. That is a Phase 2 beat to be planned and placed, not a sentence to be patched into a departure.
Recorded in `PROJECT_STATE.yaml` and `CANON_LEDGER.yaml` so the idea is not lost with the clause.

The original wording is preserved verbatim in `CANON_LEDGER.yaml → superseded` so restoring it is one
edit. **Nothing else in ch.7 changed except CONT-002.**

---

## CONT-002 — CRITICAL — the hand was taken more than twice

**Location:** `chapter-07.md:65` — *"taken me by the hand for the second time in her life"*

The manuscript shows Achird taking Merope's hand three times before that line:

| # | Where | Text |
|---|---|---|
| 1 | `chapter-03.md:85` | *"Achird took me by the hand."* — with `:87` stating it is the first time: *"She had never done that… she had never once reached out and taken my hand"* |
| 2 | `chapter-04.md:3` | *"She took my hand **again**."* |
| 3 | `chapter-04.md:137` | *"She gave me her hand **again** at the top of the rise"* |

So ch.7's act is the **fourth**, and there is no reading on which it is the second. This is a plain
factual contradiction of the manuscript by itself, in the chapter that carries the book's arc.

**Applied fix:** `for the second time in her life` → `for the fourth time in her life`.

**Why the count matters beyond the number.** The line exists to mark the gesture as *rare* — that is
its whole job, and the rarity is what makes ch.7's two-fingers-on-the-back-of-a-hand land. Four
occasions across years of travel still reads as rare, and it now reads as rare *and true*. The
alternative fix — cutting the count and writing "again" — was rejected because it discards the
rarity note the sentence was built to carry.

---

## CONT-003 — MINOR — the curve was found twice, on different days

**Location:** `chapter-05.md`

- *"There is a shape down at the base of the growth… that Achird found **on the first morning**"*
- three paragraphs later: *"She had found it **in her first week**"*

And `chapter-03.md` places the discovery on a morning after ch.2's explicit "second morning" —
so day three at the earliest, never the first morning.

**Applied fix:** `found on the first morning` → `found that first week`, which reconciles with ch.3's
placement and with ch.5's own second statement.

---

## CONT-004 — MINOR (craft) — pipeline vocabulary in the prose

**Location:** `chapter-03.md:117`

> I am going to describe the happiness now, because **the packet of my life that contains this
> chapter** is one I would go back to…

`grep -n packet` across the manuscript returns this single hit. It is a **scene packet** — the
pipeline's own working artifact — leaking into the narrator's voice.

**Why this is worth more than a one-word fix.** The hostile persona (Priya, see
`reader-personas.md`) has "any sentence that sounds like the pipeline" as an explicit instant-fail.
A validation run whose own vocabulary surfaces in its output prose is producing exactly the artifact
its quality gate is supposed to catch. It also breaks the fictional frame more than the established
metafictional tic does: Merope says "this chapter" and "this book" elsewhere, so the frame was fine —
the word *packet* is the problem.

**Applied fix:** `because the packet of my life that contains this chapter is one I would go back to`
→ `because this is the chapter of my life I would go back to`. The metafictional frame is kept; the
pipeline word is gone. (−2 words.)

---

## CONT-005 — MINOR — `WARN-003`, trigger arrived

**Location:** `chapter-01.md` — *"It does not have a name I am willing to use."*

`WARN-003` was deferred with the named trigger *"carry it with the ch.1 polish pass."* This is that
pass, so the trigger has fired and the warning could no longer be deferred honestly.

The line implies the world **has** a name and Merope is declining to use it — which sits against
`R-008` (nothing on the planet is named) and against ch.1's own *"not on any chart. I checked."*
It was also the correct instinct: the *willfulness* was worth keeping.

**Applied fix:** → *"It does not have a name. I am not going to give it one."* The refusal is kept,
the implication that a name exists is removed, and the sentence is now in Merope's register rather
than the audit's. (+3 words.)

---

## CONT-006 — MINOR — the reverse frame describes something "already described"

**Location:** `chapter-05.md`, opening scene.

The chapter opens with a being doing *"the little wipe of the palms down the front of itself that I
have described already and am about to describe again"* — and the description of the wipe arrives
later in the same chapter, not before it.

This is a reverse-told chapter, so a frame that speaks from the end is *structurally* correct, and
"am about to describe again" is accurate. But "I have described already" is not: at the point of
utterance the description is coming, not past. Reported rather than changed because the fix is a
judgement call about how much the reverse frame is allowed to know, and because the sentence works
aloud. **Recommended if a further pass happens:** "that I have mentioned already and am about to
describe properly."

---

## CONT-007 — MINOR — an open question closed by implication

`ENTITY_STATE.yaml → timeline → T-008` carries the note: *"How long they have been here when the
shelf is found is STILL OPEN — do not fix a number."* The open question is also listed under
`open_questions`.

The manuscript uses the word **week(s)** five times:

| Where | Text |
|---|---|
| `chapter-05.md:75` | *"She had found it in her first week"* |
| `chapter-06.md:27` | *"I had stopped counting them **weeks** ago"* |
| `chapter-06.md:107` | *"it had not moved in all the **weeks**"* |
| `chapter-07.md:27` | *"It is a thing I did for **weeks** before I left"* |
| `chapter-07.md:51` | *"the dolphin had gone off about its own road **weeks** before"* |

No specific number is fixed, and ch.3 explicitly refuses to count mornings — so this is **not a
contradiction**. But five consistent uses of *weeks* settles the *scale* of the stay (weeks, not
seasons or years) without anyone having decided it. That is a determination arriving through prose
rather than through the ledger, which is the class of drift this layer exists to catch.

**Disposition:** reported and recorded. `T-008` is updated to state that the scale is *weeks* by
manuscript determination, with the exact number still open. If months or years was intended, ch.6
and ch.7 both need edits.

---

## CONT-008 — STATE — `ITM-001`'s form is stale and wrong

`ENTITY_STATE.yaml` records two things about the first object that the manuscript contradicts:

- *"'a button, bone-white, four holes' — the drafted chapter does NOT specify its form, so treat the
  form as unestablished"*
- The four-hole detail is a **BUILD-mode invention** that never made it into prose.

Three chapters specify the object precisely and consistently, and use a different word:

| Where | Text |
|---|---|
| `chapter-02.md:59` | *"It was small. It was white, or it had been. There was **a hole** worked through **one end** of it, and the work was fine"* |
| `chapter-04.md:117` | *"**my button**. The white one. The small white thing with the hole worked through one end"* |
| `chapter-02.md:63` | Merope, laughing at it: *"Did you feed it."* |

**Manuscript wins.** `ITM-001` must read: *button; bone-white; a single hole worked through one end;
work too fine to be from here.* Fixed in `ENTITY_STATE.yaml`.

---

## CONT-009 — STATE — the buried strap-end has no entity

The ch.3 shape is load-bearing twice over: Merope dismisses it in ch.3 (the `CRIT-003` beat) and
re-examines it in ch.5, where it turns out to be physical evidence of the buried past:

> It is not a curve… **It is the end of a strap. There is a buckle on it**, or there was, or the shape
> of one has been grown over and kept… The growth has laid itself over it and gone on covering it.
> — `chapter-05.md:73`

It has **no entity ID in `ENTITY_STATE.yaml`.** `ITM-002` is the face-stone; `ITM-003` is the shelf.
The curve/strap-end was simply never tracked, which is precisely why `CRIT-003` had nothing to check
against in the Phase 2.8 audit.

**Fixed:** added as **`ITM-004` — the buried strap-end**, with `introduced: ch.3`, `identified: ch.5`,
its two appearances, its evidence value, and the rule that it must never be identified before ch.5.

---

## CONT-010 — WARNING — ch.6's cruelty line is longer than its budget

`ENTITY_STATE.yaml → CHR-001.speech_budget.ch_6`: *"Boastful, then **one short accurate line**
delivered quietly. Sentences get LONGER before she gets cruel."*

The drafted cruelty is:

> "You have been standing beside me for years, and you have never once told me a single thing you
> wanted, and now you are angry at me for not hearing it."

Three clauses, and the longest thing Merope says in the chapter. The *quiet* half of the budget is
honoured (no volume, no exclamation, "I said it flat"). The *short* half is not. The "sentences get
longer before she gets cruel" instruction is also inverted here — length peaks *at* the cruelty
rather than before it.

**Why it was a WARNING rather than an automatic fix:** a draft-versus-contract disagreement, where the
draft could have been right. It was escalated, and then resolved **in the contract's favour on
2026-09-22** because the arithmetic was not a matter of taste: the cruel line was 30 words in a single
triple-clause, and it was the *longest* thing Merope said in the chapter — the exact inverse of a
budget that asks for the shortest. Two rewrites were weighed:

| Option | Effect | Verdict |
|---|---|---|
| Keep the long line | Keeps the content; leaves the contrast between swelling and blow inverted | **rejected** |
| Shorten the line, keep both of its two moves | Restores the contrast; the cruelty keeps its *shape* (the accusation, then the turn on her for the consequence) | **applied** |
| Reduce to one plain sentence, drop the turn | Shortest, but discards the part that makes her monstrous rather than merely defensive | rejected |

```
- "You have been standing beside me for years, and you have never once told me a single thing you
-  wanted, and now you are angry at me for not hearing it."          (30 words, one clause-chain)
+ "You never once told me what you wanted. And now you are angry at me for not hearing it."
+                                                                    (20 words, two clipped sentences)
```

**The change is a relocation, not a cut.** The material that came out of the dialogue — the duration
of the relationship, her standing beside her — is already in the narration immediately after
(*"not once, not in all the time we have had each other, and I have been beside her for every hour of
it"*). So the swelling now sits *after* the blow as well as before it, which is what the budget asked
for and what Merope actually does: she explains herself in the wake of the damage.

**Note for the record that the compliance check is what surfaced this.** The speech budget is
machine-readable specifically so that this kind of drift is checkable, and it worked — this is the one
finding in the whole project that a *contract* caught rather than a reader.

**Applied.** Chapter re-run through `tools/deslop-check.sh`: **PASS**, 2,101 → 2,089 words.
Manuscript 15,543 → 15,531.

---

## CONT-011 — MINOR — two straps, one word

Ch.4's shelf inventory includes *"A strap lay there, worn soft in one place where a hand had held
it"* (`chapter-04.md:69`). Ch.5's buried object is *"the end of a strap"* with a buckle
(`chapter-05.md:73`).

These are different objects in the world, but the reader meets one strap on a shelf in ch.4 and a
different strap in the ground in ch.5, with no signal that they are unrelated. Because ch.5 is the
chapter that assembles the truth, a reader is likely to *connect* them — and the connection is false,
which would make ch.5's reveal feel like it has one more proof than it does.

**Disposition:** reported, not changed, because the fix is either renaming the shelf item (a prose
edit in a different chapter than the collision appears in) or accepting the resonance. Author's call.
**Recommended:** change ch.4's shelf item to something else with a hand-worn surface — a *handle*, a
*glove*, a *bridle* — so the ch.5 strap is unique.

---

## Checked and CLEARED

Recorded with the same weight as the findings, because a continuity audit that only reports problems
misrepresents the manuscript.

| Check | Result |
|---|---|
| **Dialogue questions punctuated as statements** (6 found: `ch1:103`, `ch2:63,85,89,93,103`) | **CLEARED — deliberate.** `voice-dna.md:59` specifies it: *"Very few questions in dialogue — she asks questions the way other people make statements."* Only 3 question marks exist in 15,531 words, and the rule is consistent across both speakers. An editor will flag this; the contract is why it is correct. |
| **`R-006` / Decision C — no being ever explains, hints at, or warns about the truth** | **HOLDS.** Every being utterance in seven chapters is possession-or-present-tense: *"We are glad you came"* (a non-answer), *"the object is a good one / it is not theirs / belongs on the shelf"*, *"To be ready"*, *"To hand things over"*, *"Now it is where it goes"*. Nothing approaches the truth. |
| **`R-011` — no visitor remains, anywhere** | **HOLDS.** Ch.4's camp: *"Nothing was broken. There was no scattering in it and no tipping."* The evidence is belongings and the fed ground, never a body. |
| **`R-012` — nothing threatens them; no chase** | **HOLDS.** Ch.6 and ch.7 contain no pursuit, no danger, no rescue scene. |
| **`CRIT-003`'s fix — ch.4's recognition is possible** | **HOLDS.** Ch.3 shows the stone, describes it as *"small and round and dull… a face… worked into it in lines that were too fine to have been made by accident"*; ch.4 recognises it as *"dull, with the face worked into it in lines too fine to be an accident"*. Consistent, and the recognition is earned. |
| **`CRIT-001` — Achird's per-chapter speech budget** | **HOLDS** for ch.1–5 and ch.7. Ch.7 is fully silent (*"She did not answer"* ×2). Ch.6 is one sentence plus one word. Ch.5 states the fact once and stops. Only ch.6's *cruelty*, which is Merope's, is a deviation — CONT-010. |
| **The unstable crowd count** | **CLEARED.** Ch.1 counts 31 then gets a different number *on purpose*; ch.6 says *"thirty-odd of them or forty"* and *"forty of them, or thirty"*. This is the specified rule (*"exact count deliberately unstable and never fixed"*) executing correctly. |
| **`R-001` — no competence cascade** | **HOLDS.** Merope solves nothing and states the wrong explanation at every turn. |
| **`OBJ-001` narration rule — Merope narrates as pilot** | **HOLDS,** and ch.7 pays it off explicitly: *"she flies it, she has always flown it, and I narrate as though I do."* |
| **The ch.1 "eleven greetings" / ch.2 "eleven of them" echo** | **CLEARED** as an intentional echo, not a slipped digit. |
| **`R-008` — nothing named but constellations** | **HOLDS** after the CONT-005 fix. `Delphinus` and `Scorpius` are the only names in the book. |

---

## Gate state after this pass

- **2 CRITICAL found, 2 fixed.**
- 3 MINORs fixed (CONT-003, CONT-004, CONT-005), 2 state defects fixed (CONT-008, CONT-009).
- 4 reported but deliberately **not** changed on the day (CONT-006, CONT-007, CONT-010, CONT-011) — two
  are prose judgement calls in chapters that would need a further pass, one is a contract-versus-draft
  disagreement that is the author's, one is a resonance question. **Two of the four were closed the
  same day once released (`CONT-010` fixed; `AUTH-2` confirmed removed with a stronger reason) — see
  the addendum at the end of this file.**
- Prose gate re-run on all four changed chapters: **PASS.** Full manuscript 15,543 words **at this
  pass** (15,531 after the addendum below). Controls re-run: **ALL CONTROLS PASS.**

**Phase 5.6: PASSES, with four open items named rather than closed.**

---

## Addendum — 2026-09-22, the same day: two of the four open items closed

`CONT-010` and the `AUTH-2` half of `CONT-001` were released by the author and resolved.

| Item | Resolution |
|---|---|
| `CONT-010` | **FIXED.** The ch.6 cruelty line was rewritten from 30 words in one clause-chain to 20 words in two clipped sentences. See the rewritten section above. ch.6 re-gated **PASS**, 2,101 → 2,089 words. |
| `AUTH-2` (the `CONT-001` clause) | **LEFT REMOVED, and the reason upgraded.** Investigating the restore option proved the act was **geographically impossible** where ch.7 placed it — see the geography finding above. |

**Manuscript is now 15,531 words**, all seven chapters PASS, controls green, EPUB rebuilt.

**Still open, and deliberately:** `CONT-006` (ch.5's reverse-frame wording), `CONT-011` (the two
straps), `CONT-007` (the stay is *weeks* by implication — recorded as a determination, and the author
may change it). These are prose judgement calls and a scale confirmation, and none of them is a
contradiction the book is currently telling against itself.
