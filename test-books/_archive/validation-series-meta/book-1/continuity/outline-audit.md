# Continuity Check: outline (Phase 2.8)

**Date:** 2026-09-22
**Method:** `/continuity-guardian`, pre-writing mode (Audits 1–6)
**Documents audited:**

| Document | Role |
|---|---|
| `outline.md` | chapter beats, tension map, structural ledger |
| `foundation.md` | characters, engine, world rules, writer warnings |
| `voice-dna.md` | voice contract — the prescriptive document drafting follows |
| `ENTITY_STATE.yaml` | structured entity + knowledge + timeline state (Phase 2.7) |
| `PROJECT_STATE.yaml` | primary state file, phase gates, canon pointers |
| `scene-packets/chapter-01..07.md` | the beats drafting actually runs off |
| `manuscript/chapters/chapter-01.md` | **already drafted** — audited against the contract |

**Ran late.** This audit was supposed to run *before* drafting began. It ran after chapter 1.
Recorded as late, not as having run on schedule.

**Total findings: 22 — 4 CRITICAL, 12 WARNING, 6 MINOR.**

**Gate status at issue: FAIL.** The Phase 2.8 → 3 gate requires zero CRITICAL findings.

---

## DETERMINATIONS (user, 2026-09-22)

Recorded against the findings as issued. The findings above are **not rewritten** — this section is
the determination that sits on top of them. **Nothing here has been applied to the story documents
at the user's instruction**, so where a decision contradicts a document, that divergence is stated
below rather than quietly created.

### D-1 — CRIT-002: the sleigh decides, and she is carried

**User decision: option (c).** The sleigh's decision stands as written; Merope does not choose to
leave; foundation's arc is what changes.

Consequences, recorded now because they are decisions and not edits:

| Document | Currently says | Must become |
|---|---|---|
| `foundation.md`, Merope's arc | "She takes **one step** against her own appetite: she leaves." | She never chooses. What changes is that she **looks**. |
| `foundation.md` warning 7 | "Do not damage anyone. Nothing is lost. The ending is growth." | Still true — but the growth now lives **entirely in the acknowledgement**, which is small. |
| `scene-packets/chapter-06.md` Beat 5 | "the sleigh moves on its own… Merope follows, still talking" | **Stand as written.** No longer a contradiction; it is the mechanism. |
| `scene-packets/chapter-07.md` | "leaving is easy"; "she simply went" | **Stand as written** — now literally true rather than under-motivated. |

**What this buys:** the theme sharpens. *Does a place that asks nothing of you keep you from becoming
anything?* — answered by implication as *it kept her from acting at all; she was carried out.* She is
the evidence rather than the exception. And the sleigh becomes the theme's answer: the only thing
that can move without anyone deciding is what breaks a world built to make movement unnecessary.

**The risk to watch, on the record:** with no decision, the book can read as fatalism rather than
growth. The entire counterweight is that the acknowledgement is mutual and real — which puts the
whole arc on ch.7's S3/S4, two small beats. Check that load when ch.7 is drafted. The tsundere
deflection gains a real reason from this reading (she cannot claim a choice she did not make), so the
defence mechanism and the theme now point the same way instead of merely coexisting.

### D-2 — WARN-004: the rescue clause was mine, not the user's

**Determination: WARN-004 and CRIT-002 were the same finding seen twice, and D-1 resolves both.**

Provenance, corrected: `scene-packets/chapter-07.md:68` reads "A chase, a rescue, a last-minute
danger, or the sleigh saving anyone." **Only the first item traces to the user** — decision C, *no
host, no confrontation, no chase.* The other three are the agent's extension of it, written to guard
against inheriting the reference's chase ending, and were then reported as a conflict with the user's
own decision that the sleigh "will save someone if it needs to." **The over-reach is the agent's.**

What survives: *nothing threatens them* — that is decision C plus the user's `INTAKE.md:214` answer,
"Nothing malicious happens. That is worse." What should be cut: the ban on the **meaning**. Under
D-1 there is no rescue scene and no threat, and the sleigh's decision is simply what got her out, so
the clause and the sleigh's established capability no longer collide at all.

### D-3 — WARN-006: the constraint is no *visitor* remains, not no bodies

**Determination: the finding's premise was over-broad. Narrowed.**

The prohibition is the user's — `PROJECT_STATE.yaml:200`, rationale "User decision": *"Chapter 4
discovery is belongings only - no bodies, no remains. The absence is the horror."* But the user
**scoped it to chapter 4's discovery**, and what it protects is the absence of **visitor** remains.
The phrasing "no bodies, anywhere, ever" is the agent's own wording in the ch.4 and ch.7 packets, not
the user's rule.

**A body of a different species does not touch what this rule protects.** The horror is that the
people who came here left their belongings and nothing else; a creature's remains are a different
fact, and would arguably strengthen ch.5 by demonstrating the growth mechanism without spending the
visitor revelation early. The chapter 3 shape remains an open creative choice, explicitly including a
body of something that is not a person.

**Follow-through owed when edits are permitted:** narrow ch.4's "No bodies. No remains. No trace of a
body." and ch.7's "No body, no remains, no victim anywhere in the chapter" to **visitor** remains.
The ch.5 packet's step-back wording ("shaped out of what came before") needs the same narrowing so
it cannot be read as human remains.

---

## CRITICAL ISSUES (must fix before proceeding)

### [CRIT-001] Achird's silence is specified four ways, and chapter 6 contradicts itself

- **Audit:** 1c (trait consistency) · 3 (information flow) · 5d (contradictory plot points)
- **Chapters:** 5, 6, 7
- **Description:** Achird's silence is decision B — the load-bearing structural change of the whole
  book, "the middle of the book is her unable to be heard." Four documents describe it, and they do
  not agree on when it starts, how total it is, or whether it ever breaks. Chapter 6 contradicts
  **its own packet** in the same file.
- **Evidence:**
  - `scene-packets/chapter-05.md:62` — "Achird's silence begins here and **holds through ch. 6 and
    7.**"
  - `scene-packets/chapter-05.md:69` — "Achird can no longer be heard, because **she has stopped
    speaking.**"
  - `scene-packets/chapter-06.md:57` — "Achird **stopped speaking in ch. 5 and does not resume
    here.**"
  - `scene-packets/chapter-06.md` Beat 1 — "**One sentence.** *We have to go.* Flat, complete, no
    preamble."
  - `scene-packets/chapter-06.md` Required — "Achird's total dialogue in the chapter is **one
    sentence**, plus at most one word."
  - `scene-packets/chapter-06.md` Opening line — "**Achird's one sentence**, or Merope's voice
    cutting in before it finishes."
  - `scene-packets/chapter-07.md:52` — "Achird has been **silent since ch. 5.**"
  - `voice-dna.md` — "her **largest moment in the book is one sentence.**"
- **Suggested fix:** Assign one meaning and make the other four lines agree. The reading the rest of
  the corpus supports is:

  | Chapter | Achird |
  |---|---|
  | 5 | stops **arguing and explaining**. States the fact once and stops. Movement II's last line. |
  | 6 | **one sentence**, exactly one, plus at most one word. This is the largest moment in the book. |
  | 7 | says nothing. |

  Concretely: ch.5 line 62 becomes "Achird stops explaining here; from this point she says only what
  is necessary, and she says it once." Ch.6 line 57 becomes "Achird has not argued since ch. 5. Her
  one sentence in this chapter is the whole of her speech." Ch.7 line 52 becomes "Achird has said one
  sentence since ch. 5. She stays silent."
- **Cascade risk:** Ch.5's exit pull currently reads "Achird can no longer be heard, because she has
  stopped speaking" — if she still speaks in ch.6, that line needs to become "because she has stopped
  arguing." Check ch.5's final beat and the ch.5→6 gate after editing. `ENTITY_STATE.yaml` has no
  entry for the silence at all; add one (see CRIT-003 patches).

### [CRIT-002] The ending has no author — Merope's step is taken by the sleigh

- **Audit:** 5d (contradictory plot points) · arc consistency (foundation is the arc authority)
- **Chapters:** 6, 7
- **Description:** The book's stated arc is that Merope takes **one step** against her own appetite.
  Chapter 6 specifies that the step is taken by the sleigh, against her, while she follows still
  talking. Both cannot be the mechanism. If the sleigh forces the departure, the ending's growth is
  unearned and decision B's payoff — Merope finally seeing Achird — has nothing behind it. This is
  the one finding that touches the *meaning* of the ending rather than its mechanics.
- **Evidence:**
  - `foundation.md`, Merope's arc — "She takes **one step** against her own appetite: she leaves.
    She does it for a reason she will not name."
  - `foundation.md`, warning 8 / `outline.md` ch.7 writer notes — the ending is "**growth, not
    damage**."
  - `scene-packets/chapter-06.md` Beat 5 — "The argument ends because **the sleigh moves on its
    own.** It has decided, and it will not be argued with." · "Achird goes to it. **Merope follows,
    still talking.**"
  - `scene-packets/chapter-06.md` Required — "The sleigh acts of its own accord, **against
    Merope.**"
  - `scene-packets/chapter-06.md` Exit pull — "**Achird stops asking** — and the sleigh, which has
    been still the whole time, has already decided."
  - `outline.md` ch.7 — "Merope does not announce why she left and does not understand why… **She
    simply went.**"
- **Suggested fix:** Two workable resolutions; this is an authorial call, not a mechanical one:

  **(a) The step is boarding.** The sleigh moves on its own, and the beat that belongs to Merope is
  that **she climbs in** — one action, on the page, unmotivated by anything but the sight of Achird
  already at the front of it. Her step is following, chosen. Ch.6's "against Merope" then means
  *against what she said*, not *without her.*

  **(b) The sleigh moves last, not first.** Achird stops asking, and *then* Merope stands up. The
  sleigh moving on its own becomes the confirmation of a choice already made, and ch.7's opening
  ("already leaving, mid-sentence") reads as continuity rather than rescue.

  (a) is smaller and keeps ch.6's beat order intact. (b) gives Merope the decision outright and costs
  one beat of restructuring.
- **Cascade risk:** Large either way. Ch.6's exit pull, ch.7's opening line, ch.7's "leaving is
  easy," ch.7's residue ("she got what she wanted, it was smaller than she thought") and
  `ENTITY_STATE.yaml` `OBJ-001.acts_without_decision_in: ["ch.6"]` all key off this. Fix the
  documents first, then the ch.6 packet, then everything downstream.

### [CRIT-003] Merope is required to recognise an object she was never shown

- **Audit:** 3b (forward-reference violation / impossible information flow)
- **Chapters:** 3, 4
- **Description:** Chapter 4 requires that the objects from chapters 1 and 3 be **among** the things
  on the shelf and that **Merope notice that.** She saw the chapter 1 object (ch.2 has Achird show it
  to her). She never saw the chapter 3 object: Achird asks her to come and look and she says she will
  come later. She cannot recognise, on a shelf, an object she has never laid eyes on. This is the
  exact class of error — "but how does she *know* that?" — this audit exists to catch, and it is the
  next chapter to be drafted.
- **Evidence:**
  - `scene-packets/chapter-03.md` pass 2 — "Achird finds **another object**, and this time asks her
    directly to come and look. **Merope is elsewhere and says she will come later.**"
  - `scene-packets/chapter-04.md` Continuity — "The objects from ch. 1 and ch. 3 are **among** the
    things on the shelf. **Merope should notice that**, and be pleased."
  - `ENTITY_STATE.yaml` `ITM-002` — "the remaining belongings, introduced ch.4" — the chapter 3
    object is not tracked as an item at all, so the shelf constraint has no entity behind it.
- **Suggested fix:** Have Merope look, in ch.3. One line in pass 2: she comes to the pocket, looks,
  and dismisses it — which is *better* than not looking, because ch.5's reversal then costs
  something: she has already seen and waved away the evidence. Alternative: narrow the ch.4
  constraint to the chapter 1 object only, and let the chapter 3 object stay unseen. The first is
  cheaper and strengthens ch.5.
- **Cascade risk:** Adding the look to ch.3 pass 2 changes the packet's stated beat order and gives
  Achird one more non-answering beat. Verify ch.3's "she narrates over Achird's warning from pass 1"
  still lands, and add the chapter 3 object to `ENTITY_STATE.yaml` as its own item ID.

### [CRIT-004] `PROJECT_STATE.yaml` does not parse — the primary state file is unloadable

- **Audit:** 6 (state divergence) · pipeline integrity
- **Chapters:** n/a — this is the state file itself.
- **Description:** Line 66 is indented **deeper than its own parent key**, which puts a mapping key
  where a scalar value already sits. The file fails to parse at all. Every phase gate, every "load
  the prior project state" instruction, and Book 2's "load the series canon, Book 1's approved voice
  contracts, and the prior project state" step read this file. As of right now, none of them can.
- **Evidence:** verified with a real parser (`js-yaml`, not a grep):
  ```
  $ npx --yes js-yaml validation-series/book-1/PROJECT_STATE.yaml
  YAMLException: bad indentation of a mapping entry (66:7)
    65 |     pipeline_gate: "required at pipeline Phases 3 (Drafting), ..."
    66 |       note: "caps are tuned to light-novel narrative register ..."
  ------------^
    67 |     exempt: "..."
  ```
  `ENTITY_STATE.yaml` parses clean (exit 0). Only `PROJECT_STATE.yaml` is broken.
- **Suggested fix:** Fold the orphaned `note:` into `pipeline_gate` (it is a qualification of that
  value, not a sibling), or promote it to a `note:` sibling at 4-space indent. Applied in this pass.
- **Cascade risk:** None — any correct reading of the block preserves the meaning. But this defect
  has been sitting in the file since the pipeline-gate decision was written, so **every earlier
  claim that the state file was updated needs re-checking**; a file that cannot be parsed cannot have
  been read by anything downstream. This one is on me.

---

## WARNING ISSUES (should fix, may confuse readers)

### [WARN-001] The sleigh/steed mechanism is contradicted by chapter 1's own draft

- **Audit:** 4 (world rules consistency)
- **Chapters:** 1, 7
- **Description:** Warning 13 exists specifically to close the "what is pulling this thing?"
  question. The drafted chapter 1 reopens it: the steed is described as a **detached sky object**
  while the sleigh sits parked on the ground, and no document says what moved the sleigh, whether the
  steed is attached to it, or what "steed" means if it isn't.
- **Evidence:**
  - `chapter-01.md:129` — "By the middle of that morning Delphinus had gone far enough along its own
    road that the dolphin was no longer overhead. **It had drifted out past the trees and was hanging
    there in the open sky**, bright, unmistakably a dolphin, doing nothing at all."
  - `chapter-01.md:9` — "**I am steering it.**"
  - `foundation.md` warning 13 — "its steed is **a constellation that has taken a shape.** Never imply
    a draft animal between shafts."
  - `ENTITY_STATE.yaml` `OBJ-001.steed` — "a constellation that has taken a shape and holds it; the
    shape moves as the constellation moves."
- **Suggested fix:** Decide the relationship and write it once, in `foundation.md`, then make the
  chapter agree. The coherent option is that the steed is **not a body pulling the sleigh** and not a
  detached sky decoration either: the constellation is the *route* the sleigh runs on — the shape is
  overhead and ahead, the sleigh moves along it, and when it is parked the shape has moved on without
  them. That reading makes "drifted out past the trees" a *measurement of time passed* rather than a
  loose animal, which is more interesting and explains Merope's annoyance at the end of ch.1.
- **Cascade risk:** ch.7's required "the steed takes a new constellation's shape as it goes" must
  match whatever is decided. `ENTITY_STATE.yaml` `OBJ-001.steed_examples` needs the same wording.

### [WARN-002] The dread curve is stated three incompatible ways, and foundation calls its own table stale

- **Audit:** 4 (world rules) · document integrity
- **Documents:** `foundation.md`, `outline.md`
- **Description:** Three statements of when dread enters, and none of them reduce to the others.
  Separately, `foundation.md` still labels its own movement table **provisional pending a structural
  revision that has since been selected and recorded directly above it.**
- **Evidence:**
  - `foundation.md`, movement table row I — "**Dread does not enter here as dread** — but Achird is
    already finding things."
  - `foundation.md`, tone section — "**Dread enters late in movement I** and rises steadily through
    II and III."
  - `foundation.md`, tone balance — "the first movement is genuinely warm and light; unease then
    **builds steadily across movements II and III.**"
  - `foundation.md`, immediately below the movement table — "**The movement table above is
    provisional** pending the structural revision currently being selected." (The revision — A/B/C —
    is recorded in the same section, above that line.)
  - `outline.md` — "dread never announces itself… **not one cold statement, not a chapter-four
    lurch.**"
  - `scene-packets/chapter-02.md` — "The beings' answer about the object is **the first cold thing in
    the book.**"
- **Suggested fix:** One sentence, in `foundation.md`, replacing all three: *unease begins in ch.2
  with the beings' flat answer about the object; it is never announced and rises from there.* Then
  delete the stale "provisional" paragraph.
- **Cascade risk:** ch.3's packet forbids "any menace, omen, or wrongness the reader can name." Under
  the single-sentence version that is still correct — ch.3 has no new dread, it has Achird's finds
  and Merope's dismissals. Confirm ch.3 is not edited to add any.

### [WARN-003] The naming rule vs. chapter 1's line about the world's name

- **Audit:** 3 (information flow) · 4 (world rules)
- **Chapters:** 1
- **Description:** The naming rule says nothing on the planet is named and `ENTITY_STATE.yaml` records
  that Merope knows the world is "not on any chart." The drafted line implies she has a name for it
  and is declining to use it — which is a different, larger claim, and an unpayable one.
- **Evidence:**
  - `chapter-01.md:35` — "Below us was a world. **It does not have a name I am willing to use.**"
  - `chapter-01.md:9` — "We are somewhere that is not on any chart. I checked."
  - `foundation.md` naming rule — "**Nothing on the planet is named.** No planet name."
  - `ENTITY_STATE.yaml` `CHR-001.knows` — "that they arrived at a world not on any chart."
- **Suggested fix:** "It does not have a name." Four words, same rhythm, no implied withheld fact.
  If a withheld name is wanted deliberately, it needs to be recorded as a decision and paid off
  somewhere — right now nothing would ever collect it.
- **Cascade risk:** None. Same paragraph, no knowledge state changes.

### [WARN-004] The sleigh's one stated capability — saving someone — is forbidden at the only place it could pay off

- **Audit:** 5b (Chekhov's gun) · 5d
- **Chapters:** 6, 7
- **Description:** Three documents and the original user decision establish that the sleigh will act
  on its own to save someone. Nothing in the book is ever saved: ch.6 forbids physical danger and
  ch.7 explicitly forbids "the sleigh saving anyone." Either the ch.6 departure **is** the rescue —
  staying is what kills her, so leaving is being saved — or the foundation's headline description of
  the sleigh's agency is a promise the book never keeps.
- **Evidence:**
  - `foundation.md`, the sleigh — "**if it needs to save someone, it will.** It is therefore the one
    thing in the book that can move without anyone's decision."
  - `ENTITY_STATE.yaml` `OBJ-001.agency` — "it chooses as well as being chosen; if it needs to save
    someone, it will."
  - `scene-packets/chapter-06.md` Beat 5 — the sleigh moves on its own. No one is in danger.
  - `scene-packets/chapter-06.md` Forbidden — "Any physical danger to anyone."
  - `scene-packets/chapter-07.md` Forbidden — "A chase, a rescue, a last-minute danger, or **the
    sleigh saving anyone.**"
- **Suggested fix:** Take the first reading and record it: **the sleigh's rescue is the departure.**
  The planet's method is to make leaving feel unnecessary; the sleigh overrides that. Then delete the
  ch.7 forbidden clause about the sleigh, or narrow it to "no rescue *scene*," so the meaning is not
  forbidden along with the cliché.
- **Cascade risk:** Interacts directly with CRIT-002. Decide CRIT-002 first — if Merope's step is
  boarding, the sleigh's act is better read as making room for her decision than as overriding it,
  and this warning softens.

### [WARN-005] Chapter 2's object question is the one place "the beings answer honestly" can collide with "the beings never explain"

- **Audit:** 4 (world rules) · 3 (information flow)
- **Chapters:** 2, 4, 5
- **Description:** The beings are governed by two absolute and separately-stated rules: they **cannot
  lie**, and they **cannot explain** — and, crucially, they do not know that any visitor has died.
  Chapter 2 asks a being directly what the object is, in front of the reader, and requires an honest
  answer. The object belonged to a dead visitor. Define what a being may truthfully say about it
  before drafting, or ch.2 will either produce an evasion (breaking the first rule) or a disclosure
  (breaking the second and collapsing ch.5's reversal).
- **Evidence:**
  - `scene-packets/chapter-02.md` — "Achird asks **one of the beings** what it is. The being answers
    **honestly, helpfully, and cheerfully** — and the answer means nothing to it. **It is the first
    cold thing in the book.**"
  - `foundation.md` warning 10 — "No being ever explains, warns, hints or states the truth. **Not
    once, to anyone.**"
  - `voice-dna.md`, the beings — "they cannot lie, and they cannot explain. They do not know what
    they are, so there is nothing for them to conceal."
  - `ENTITY_STATE.yaml` `COL-001.does_not_know` — "that they grew from the dead; that any visitor has
    ever died here."
- **Suggested fix:** Write the boundary into `voice-dna.md`: a being may answer only from
  **possession and present tense** — what it is called here, where it is kept, who handles it, that
  it is nice. It may never answer from **origin or ownership** — where it came from, whose it was,
  how it got here. "Somebody lost this" (ch.1) already sits on the right side of that line: it is a
  true statement about a possession, offered without knowledge of the owner. Under that rule the
  chapter 2 answer stays honest and stays empty at the same time.
- **Cascade risk:** Constrains every being line in chs.1–4. Ch.1's drafted being dialogue is
  consistent with the boundary already.

### [WARN-006] The non-plant shape resolving in ch.5 invites a remains reading the book forbids

- **Audit:** 5b · 5d · hard rule collision
- **Chapters:** 3, 4, 5
- **Description:** The engine says the growth grew from the dead. Ch.5's step-back requires "the
  growth… is shaped **out of what came before**" and says the ch.3 non-plant shape "resolves here."
  Ch.4 carries a hard rule: "No bodies. No remains. No trace of a body… No bodies, anywhere, ever."
  A shape that is *not a plant*, growing in the growth, made of what came before, is going to be
  read as a body — which is the one thing the book must never show.
- **Evidence:**
  - `scene-packets/chapter-03.md` — "**a shape in the growth that is not a plant**… It is not a
    monster and must not read as one."
  - `scene-packets/chapter-05.md` — "The things growing here… They are not shaped for guests. They
    are shaped **out of what came before.**" · "The non-plant shape Achird noticed in ch. 3
    **resolves here**, quietly, as part of this."
  - `scene-packets/chapter-04.md` Required — "**No bodies. No remains. No trace of a body.**"
  - `scene-packets/chapter-04.md` Forbidden — "Remains, bones, graves, monuments, or a marked place
    for the dead."
- **Suggested fix:** Decide what the shape is, and make it *made* rather than *organic*: something a
  person brought and the growth accepted — a hand tool, a buckle, a strap — half-covered, still
  recognisable as manufacture. Then ch.5's resolution is that the planet incorporates **things** as
  it incorporates people, and the horror is intact without a body ever being on the page.
- **Cascade risk:** Ch.3's packet currently says the shape "is never returned to in this chapter and
  never explained"; ch.5 keeps that. Only the *what it is* needs fixing, not the timing. If the shape
  becomes a made object it also gives ch.4's shelf a legitimate precursor.

### [WARN-007] Chapter 2 has no timeline entry and no stated relation to chapter 1

- **Audit:** 2b (logical sequence) · 6c (coverage gap)
- **Chapters:** 1, 2, 3
- **Description:** Chapter 1 ends at night with Merope sleeping. Chapter 2 is specified only as "two
  halves of **the same day**" — same as what is not stated. Chapter 3 then establishes that days stop
  behaving, so the book needs a stable "normal" day count *before* ch.3 for the distortion to read as
  distortion. `ENTITY_STATE.yaml`'s timeline has no entry for ch.2 or ch.5 at all.
- **Evidence:**
  - `scene-packets/chapter-02.md` — "The chapter alternates between two halves of **the same day.**"
  - `chapter-01.md` closing — "**I slept better than I have ever slept.**"
  - `scene-packets/chapter-03.md` — "Time is not behaving; days are being lost."
  - `ENTITY_STATE.yaml` `timeline` — T-001…T-004 are all ch.1; T-005 is ch.3; T-006 is ch.4. **No
    entry exists for ch.2 or for ch.5.**
- **Suggested fix:** State it in the ch.2 packet: chapter 2 is **day two**. Add T entries for ch.2
  and ch.5. Explicit day numbering also lets ch.3's repetition be countable, which is what makes it
  unsettling rather than merely vague.
- **Cascade risk:** If chapter 2 is day two, ch.2's "Achird shows Merope the object from chapter 1"
  is one day after the find — fine. Do not let the numbering appear on the page; the packet's rule
  that "the repeated day is never explained and never mentioned by anyone but Merope, casually" still
  holds.

### [WARN-008] `foundation.md` still says the Phase 2 gate is awaiting approval, and `outline.md` still lists the beats as pending

- **Audit:** 6 (state divergence) · document integrity
- **Documents:** `foundation.md`, `outline.md`, `PROJECT_STATE.yaml`
- **Description:** Three documents disagree about whether the gate that drafting already passed has
  passed. This is the same failure mode the validation run exists to catch: the file that carries the
  evidence still says the work has not been permitted.
- **Evidence:**
  - `foundation.md` header — "Phase 2. **GATE: awaiting user approval.** Nothing here is fixed until
    approved."
  - `outline.md` gate checklist — "- [ ] **Chapter beats approved** — PENDING"
  - `PROJECT_STATE.yaml` phase history — `{ phase: "2", status: "gate_passed", … "GATE PASSED BY
    USER: instruction to begin drafting accepted as approval of the chapter beats." }`
  - `PROJECT_STATE.yaml` `chapters.completed` — chapter 1, status `drafted`, prose gate `PASS`.
- **Suggested fix:** `foundation.md` header → "Phase 2. **GATE PASSED** (user, 2026-09-22: instruction
  to begin drafting). Titles remain deferred." `outline.md` checklist → checked, with the approval
  date. Applied in this pass.
- **Cascade risk:** None.

### [WARN-009] The Phase 2.5 voice-bank gate is unmet — 4 samples against a required 10

- **Audit:** 6 (state divergence vs. gate checklist)
- **Documents:** `voice-dna.md`, `PROJECT_STATE.yaml`
- **Description:** The pipeline's 2.5 → 2.7 gate requires a voice bank of **≥10 samples, including
  ≥3 voice-breaking and ≥2 irrelevant-thought samples.** `voice-dna.md` carries 4 benchmark samples
  and `PROJECT_STATE.yaml` records `voice_bank: initialized: false, sample_count: 0`.
- **Evidence:**
  - `book-genesis/SKILL.md` gate checklist — "Voice bank initialized with >=10 samples including >=3
    voice-breaking and >=2 irrelevant-thought samples."
  - `voice-dna.md` — four benchmark samples.
  - `PROJECT_STATE.yaml` — `voice_bank: { initialized: false, sample_count: 0 }`.
- **Suggested fix:** Either extend `voice-dna.md` to 10 samples (adding voice-breaking and
  irrelevant-thought registers — Merope's deflections and Achird's flatness are the obvious sources),
  or record explicitly that the sample count is a deliberate partial and why. The state block must
  then say whichever is true.
- **Cascade risk:** The voice-breaking samples are the ones chapters 2–7 will actually need — ch.6's
  cruelty and the beings' flat answers are both voice-break registers with no sample behind them.

### [WARN-010] Phase 1.5 (reader personas) never ran and is not in the phase history

- **Audit:** 6 (state divergence) · pipeline integrity
- **Documents:** `PROJECT_STATE.yaml`
- **Description:** Phase 1.5 reader personas are absent from phase history — which jumps 2 → 2.5 —
  and `reader_personas.created: false`. Phase 4's evaluation is specified as a **four-reader
  simulation**; it has no personas to simulate. This is a gap on the record rather than a hidden one,
  but it is not *marked* as a gap the way Phase 2.8 was.
- **Evidence:**
  - `PROJECT_STATE.yaml` `phase.history` — entries for 0, 1, 2, 2, 2.5, 2.7, 2.8, 3. **No 1.5.**
  - `PROJECT_STATE.yaml` — `reader_personas: { created: false, count: 0, primary: "", hostile: "" }`
  - Pipeline — "PHASE 1.5: READER PERSONAS -> /reader-persona (3-5 reader personas for
    writer/evaluator/packager)"; Phase 4 uses `{ devourer, critic, hostile, casual, devoted }` slots.
- **Suggested fix:** Run `/reader-persona` before Phase 4, or record it as a deliberate omission with
  the evaluator's substitutes named. Do not leave it absent from history — the whole point of the
  history is that a missing phase is visible.
- **Cascade risk:** None for drafting. Blocks Phase 4 evaluation if unresolved.

### [WARN-011] `PROJECT_STATE.yaml`'s canon pointers claim completed files do not exist, and one required file has never been created

- **Audit:** 6 (state divergence) · run contract
- **Documents:** `PROJECT_STATE.yaml`, project tree
- **Description:** Four "not yet created" pointers, two of which point at files that exist and are
  complete. Separately, two artifacts the run's brief explicitly requires — the series
  `CANON_LEDGER.yaml` and `maintenance/PRUNING_LOG.md` — do not exist at either level, and success
  criterion 5 ("PRUNING_LOG.md records maintenance decisions") cannot be satisfied by a file that
  isn't there.
- **Evidence:**
  - `PROJECT_STATE.yaml` `canon` — "`entity_state`: ENTITY_STATE.yaml  # not yet created" ·
    "`voice_contract`: voice-dna.md  # not yet created" — both files exist and are complete.
  - `PROJECT_STATE.yaml` — `voice_dna: { created: false, character_cards: 0,
    differentiation_matrix: false }` — `voice-dna.md` has four voice cards and a full differentiation
    matrix.
  - Tree check — `validation-series/CANON_LEDGER.yaml` **MISSING**; `book-1/CANON_LEDGER.yaml`
    **MISSING**; `book-1/maintenance/` **does not exist.**
- **Suggested fix:** Correct the four flags (applied in this pass). Create `CANON_LEDGER.yaml` at
  series and book level from `ENTITY_STATE.yaml` + the decisions log, and `maintenance/PRUNING_LOG.md`
  with a first entry, before Phase 3 continues — otherwise the run cannot demonstrate criterion 5.
- **Cascade risk:** None technical. `canon.series_ledger` is the path Book 2 is told to load; if it
  stays missing, the Book 2 step either stalls or invents.

### [WARN-012] The voice contract's absolute "she never explains" is broken by chapter 1's own dialogue

- **Audit:** 1c (trait consistency) · voice contract vs. draft
- **Chapters:** 1, 2
- **Description:** `voice-dna.md` lists "Explain" under what Achird **never** does, without
  qualification. The drafted chapter 1 has her deliver a two-clause explanation of a cultural
  behaviour, and chapter 2 requires a being to answer a direct question. As written, the contract's
  most absolute line is already violated by the first drafted chapter and will be again — which
  trains the writer to ignore the contract.
- **Evidence:**
  - `voice-dna.md`, ACHIRD, "What she never does" — "**Explain.** Complain about not being heard."
  - `chapter-01.md` — "'The hands.' / 'Which hands.' / '**The ones with nothing in them. That is
    what they do instead of a greeting.**'"
  - `voice-dna.md`, ACHIRD syntax fingerprint — "**Two to four words is a normal Achird sentence.**"
    (the line above is 7 and 9 words)
- **Suggested fix:** Narrow the rule to what is actually meant: **she never explains a mystery, her
  own state, or anyone's feelings.** Reporting an observed fact is not explaining and is the whole
  content of her attention. Then, separately, decide whether her one long sentence in ch.1 is
  deliberate voice-breaking or should be trimmed — right now nothing in `voice-dna.md` licenses it.
- **Cascade risk:** If the long sentence is trimmed, ch.1's later payoff ("That is what I mean") loses
  its setup. Prefer narrowing the rule.

---

## MINOR ISSUES (polish-level, fix in production)

### [MINOR-001] `voice-dna.md`'s "never mentions Achird's hands" is falsified by a legitimate line

- **Audit:** 1c · **Location:** `chapter-01.md:189`
- **Description:** The rule means she never mentions Achird *at the controls*. The drafted chapter
  mentions a hand in a pocket, which is not the same thing and is a good line. The rule as written
  invites a future pass to "fix" correct prose.
- **Suggested fix:** In `ENTITY_STATE.yaml` `OBJ-001.narration_rule` and the ch.1 packet, change "never
  mentions Achird's hands" to "never mentions Achird at the controls."

### [MINOR-002] The chapter 3 object is not tracked as an entity

- **Audit:** 6c (coverage gap) · **Location:** `ENTITY_STATE.yaml`, `items`
- **Description:** `ITM-001` (ch.1) is followed directly by `ITM-002` "the remaining belongings"
  (ch.4). The object Achird finds in ch.3 has no ID, which is why CRIT-003 has nothing to patch.
- **Suggested fix:** Add it as `ITM-002` and renumber the ch.4 shelf to `ITM-003`.

### [MINOR-003] `LOC-004` and `LOC-005` are the same place, double-counted

- **Audit:** 6c · **Location:** `ENTITY_STATE.yaml`, `locations`
- **Description:** Both are `first_referenced: ch.4`; `LOC-005` is "somewhere Achird leads her" and
  `LOC-004` is "the camp," which is where Achird leads her.
- **Suggested fix:** Merge into one location, or make `LOC-005` the *walk* rather than a place.

### [MINOR-004] Merope's recorded knowledge omits what she actually heard in chapter 1

- **Audit:** 3a (knowledge database) · **Location:** `ENTITY_STATE.yaml` `CHR-001.knows`
- **Description:** The record says she knows Achird "picked up something and pocketed it (seen from a
  distance, never examined)." She also **heard Achird say "Somebody lost this"** — a claim about a
  person — and that is a different and larger piece of knowledge for ch.4 to build on.
- **Suggested fix:** Append: "that Achird said the object was somebody's, lost (ch.1, heard, not
  followed up)."

### [MINOR-005] Chapter 1's stated question is never assigned a payoff

- **Audit:** 5a (thread inventory) · **Chapters:** 1 → 5
- **Description:** Ch.1's exit pull is "how long have they been expecting somebody?" and Merope
  closes the chapter without asking it. Nothing in the outline says where it is answered, if at all.
  Ch.5's reverse structure is where it plausibly lands but this is not written down.
- **Suggested fix:** Record it as a thread with a resolution point, or record it as deliberately
  never answered. Either is fine; ambiguity is what gets forgotten in drafting.

### [MINOR-006] Two chapter 1 details carry emphasis with no planned payoff

- **Audit:** 5b (Chekhov's gun) · **Location:** `chapter-01.md`
- **Description:** "A stretch of ground that was better for sitting on than the ground beside it. The
  difference was real and I could not tell you why." and "a small brass thing on the wall that has
  never been explained to me." Both are close-up, both are flagged by the narrator as unexplained.
  Neither is picked up by any packet. The first is genuinely load-bearing if it is the growth; the
  second is texture.
- **Suggested fix:** Either connect the ground to ch.5's growth material — it is the cheapest possible
  setup for the reversal — or mark both as deliberate texture in the ch.1 packet so a later editor
  does not read them as orphans.

---

## TRACKING DATABASES

These are built here because Phase 5.6 and the Editor will need them, and because the audit's value
compounds only if they persist. **Cumulative — append in later batches, do not rebuild.**

### Character Fact Sheet

| Entity | Trait | Value | Source |
|---|---|---|---|
| CHR-001 Merope | age | 19 | foundation |
| CHR-001 | given voice | grandiose, certain; boastful → cruel under pressure | foundation, voice-dna |
| CHR-001 | want | to be watched (never stated) | foundation |
| CHR-001 | appearance | **unestablished — "during drafting only"** | ENTITY_STATE |
| CHR-001 | narration rule | narrates herself as pilot; never mentions Achird at the controls | ENTITY_STATE |
| CHR-002 Achird | age | 19 | foundation |
| CHR-002 | voice | 2–4 word sentences, no modifiers, attending not absent | voice-dna |
| CHR-002 | want | to be seen by Merope specifically | foundation |
| CHR-002 | escalation | quieter, then silent | voice-dna |
| CHR-002 | appearance | **unestablished** | ENTITY_STATE |
| COL-001 beings | count | deliberately unstable, never fixed | ENTITY_STATE |
| COL-001 | tell | smell of cut stems; hands warm | ENTITY_STATE; ch.1 draft confirms the smell |
| COL-001 | rules | never lie; never explain; never sinister; no spokesperson | foundation |
| OBJ-001 sleigh | description | old enclosed cabin on runners, glazed, wood runners | ENTITY_STATE, ch.1 |
| OBJ-001 | agency | acts without decision; "will save someone" | **unpaid — see WARN-004** |

**Both principals have no physical description on record.** That is deliberate
(`physical_appearance: "est. during drafting only"`), but it means Audits 1b and the Illustrator
brief have nothing to check against. Chapter 1's draft does not establish either. Flagging it now so
it is a choice rather than a discovery at Phase 5.6.

### Master Timeline

| ID | When | Event | Source |
|---|---|---|---|
| T-001 | ch.1, night | sleigh in transit; Delphinus overhead | ENTITY_STATE, ch.1 |
| T-002 | ch.1, morning | landing; easy light; growth reads as arranged | ENTITY_STATE, ch.1 |
| T-003 | ch.1, same morning | the beings come, all at once | ENTITY_STATE, ch.1 |
| **—** | **ch.2** | **NO ENTRY — see WARN-007** | — |
| T-005 | ch.3 | days stop behaving; the same day three times | ENTITY_STATE |
| T-006 | ch.4 | the shelf: belongings, no bodies | ENTITY_STATE |
| **—** | **ch.5** | **NO ENTRY — reverse structure, covers the years** | — |
| T-004 | ch.1, evening | Achird finds the object and pockets it | ENTITY_STATE, ch.1 |
| — | ch.6 | the refusal; sleigh moves | outline |
| — | ch.7 | departure | outline |

The night→morning boundary between T-001 and T-002 is not dramatised in the draft and reads as one
continuous descent. That is fine; recorded so it is not mistaken for a missing scene later.

### Knowledge Database

| Information | Origin | Witnesses | Current knowers | Risk |
|---|---|---|---|---|
| The object is not from here | ch.1, found by Achird | Achird; Merope at a distance | CHR-002 | ✓ |
| The object belonged to somebody ("somebody lost this") | ch.1, said aloud | Merope, Achird | both | minimal — MEROPE-004 |
| The world is not on any chart | ch.1 | both | both | ✓ |
| Nobody has ever left; nobody is buried | ch.4 shelf | both | both | **CRIT-003** |
| Everyone here died here; the beings grew from them | ch.5, **assembled, never stated** | reader | **neither character states it** | decision C holds |
| The beings do not know what they are | ch.5 | reader | nobody on the page | ✓ |
| Achird loves Merope | ch.7, Merope's realisation | Merope | Merope only | warning 8 holds |

**No being is ever a knower of the truth in any entry.** Decision C survives the audit intact — that
is the strongest result here.

### Open Plot Threads

| Thread | Opened | Status | Planned resolution |
|---|---|---|---|
| The button / first object | ch.1 | OPEN | ch.2 (shown), ch.4 (on the shelf) |
| How long were they expected | ch.1 | **OPEN, unassigned** | — MINOR-005 |
| Achird's second object | ch.3 | OPEN | ch.4 shelf — **CRIT-003** |
| The non-plant shape | ch.3 | OPEN | ch.5 — **WARN-006** |
| The shelf / the pile | ch.4 | OPEN | ch.5 |
| Achird's silence | ch.5 | OPEN | ch.6, ch.7 — **CRIT-001** |
| Merope's realisation | ch.7 | OPEN | ch.7 |
| The sleigh's autonomy | ch.1 (capability) | OPEN | ch.6 — **WARN-004** |

---

## WHAT THE AUDIT DID NOT FIND

Recorded so the result is not read as a list of problems only.

- **Decision C holds.** Across all seven packets, no being states, hints at, warns about, or
  approaches the truth. There is no host, no spokesperson, and no chase. Every "the beings explain
  something" risk is a *boundary* to define (WARN-005), not a violation on the page.
- **The exclusion rule holds.** No ledger, no record of the dead, no companion who pays, no damaged
  relationship, no "What the X Kept" title pattern. The engine is not Coldbrook's.
- **The naming rule holds.** Nothing on the planet is named in any packet or in the drafted chapter;
  constellation names appear only where permitted.
- **Achird never explains her own state, never asks to be heard, and never says what she wants.** Her
  voice card survives contact with chapter 1's draft.
- **Merope never winks.** No self-deprecation, no ironic distance, no deflating aside in ch.1 — the
  register conversion away from Reference A's self-aware narrator is holding.
- **No competence cascade.** Chapter 1 solves nothing and demonstrates no skill, as required.
- **Nobody is damaged and nothing is lost.** No packet, including ch.6 and ch.7, inflicts a loss.
- **The tension map and structural ledger hold.** No consecutive structural repeats; ch.3's false-low
  is marked as such in both documents.

---

## SUGGESTED YAML PATCHES

For `/entity-tracker` (UPDATE mode) once the CRITICALs are resolved:

```yaml
suggested_patches:
  - entity: "CHR-002"
    action: "add"
    value:
      speech_budget:
        ch_5: "stops explaining; states the fact once"
        ch_6: "one sentence, plus at most one word - the largest moment in the book"
        ch_7: "silent"
    reason: "CRIT-001. Four documents specified this four ways; ch.6 contradicted itself."

  - entity: "CHR-001.knows"
    action: "add"
    value: "that Achird said the object was somebody's, lost (ch.1, heard, not followed up)"
    reason: "MINOR-004. Recorded knowledge omitted a claim Merope actually heard."

  - entity: "new_item_ITM-002"
    action: "create"
    value:
      name: "the chapter 3 object"
      introduced: "ch.3"
      found_by: "CHR-002"
      seen_by_merope: "ch.3 pass 2 (pending CRIT-003 fix)"
    reason: "MINOR-002. The object existed in the packet but had no entity, which is why CRIT-003
             had nothing to check against."
    cascade: "renumber the current ITM-002 (the shelf) to ITM-003."

  - entity: "OBJ-001"
    action: "add"
    value:
      steed_mechanism: "TO BE DECIDED - see WARN-001; the constellation is the route the sleigh runs,
                       not a body drawing it"
    reason: "WARN-001. Chapter 1's draft shows the steed as a detached sky object while the sleigh is
             parked, which warning 13 was written to prevent."

  - entity: "LOC-005"
    action: "remove_conflict"
    reason: "MINOR-003. LOC-004 and LOC-005 are the same place; both first_referenced ch.4."

  - entity: "timeline"
    action: "add"
    value: ["T-002.5 ch.2 day two", "T-006.5 ch.5 the years behind the shelf (reverse)"]
    reason: "WARN-007. Chapters 2 and 5 had no timeline entries."
```

---

## GATE DECISION

**Phase 2.8 → 3: FAIL.** Four CRITICAL findings open. Per the phase gate, no CRITICAL may remain
unresolved before drafting continues.

| Finding | Blocks | Status |
|---|---|---|
| CRIT-001 Achird's silence | ch.5, ch.6, ch.7 drafting | proposed, edits held |
| CRIT-002 who authorises the ending | ch.6, ch.7, and the ending's meaning | **DECIDED — the sleigh decides, she is carried (D-1). Not applied.** |
| CRIT-003 the object she never saw | **ch.3 — the next chapter to be drafted** | proposed, edits held |
| CRIT-004 state file does not parse | every phase gate, and Book 2 | fixed in this pass |

CRIT-004 is fixed. CRIT-002 is decided and recorded but deliberately **not applied** — its resolution
contradicts `foundation.md`'s current arc line, and that divergence is stated rather than created
silently. CRIT-001 and CRIT-003 have proposed resolutions that need a yes. All story-side edits are
held at the user's instruction.

**Amended by D-2 and D-3:** two of the twelve WARNINGs as issued were the agent's own inferred rules
reported as if they were canon — WARN-004's rescue clause and WARN-006's book-wide no-bodies rule.
Both are narrowed above. That is a failure mode worth naming: an auditor that launders its own
inference into a finding produces exactly the kind of confident wrong rule this audit exists to
catch.

The 12 WARNINGs may be addressed or deferred with rationale, per the gate — but WARN-001 (the sleigh
mechanism) and WARN-005 (the beings' answer boundary) both govern chapters not yet drafted and are
worth settling in the same pass.
