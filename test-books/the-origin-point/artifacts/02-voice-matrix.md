# VOICE MATRIX — The Origin Point

**Phase 2.5.** Per-character voice specification. The Writer reads this before drafting.
Purpose: **make the cover-the-name test pass** — every speaking character in a
paragraph must be identifiable from the prose alone, with no dialogue tag.

---

## Naming standard (author's, 2026-09-28) — a craft rule, not a gate

**A name in this book must mean something.** Not decoration: the specific thing the
character, their family, or the town would have reached for. This is the author's
standing position and it is recorded here because the voice matrix is where a writer
looks before drafting, not in a tool.

It is deliberately **not** enforced by `check-names.py`, and it should never be. A gate
that required meaningful names could not write a plain name for a character who needs
one, and it would convert a preference into a rule that generates a different preference
in disguise — picking flowers because the gate said flowers. The gate does the opposite
and much smaller job: it refuses names the model reaches for by default (SSA top 20 =
fail, Nameberry top 100 = warn, you rule) and names already used in another of your
books. **It filters; it does not compose.**

### The cast, and what each name is doing

| | name | the meaning |
|---|---|---|
| P-001 | **Delphine Rusk** | *delphine* — from Greek *delphis*, "of the womb," and the French form of a Greek sea-goddian name. Also: the name in *The Odyssey* for the dawn. She is a woman who works nights and certifies what happened at the start of things. The surname is plain American Dutch; the first name is the only European thing about her, and she has never fitted the town. |
| P-002 | **Roy Halloran** | *roy* — "king." He is the volunteer chief in a town that has informally elected him king of a fire he did not start, and he behaves like a man who knows it. Halloran is an Irish name in a county with no Irish left in it, which is its own small fact about the place. |
| P-003 | **Cora Vance** | *cora* — from Greek *kore*, "maiden," the same root as *Persephone* and *core*. A name a woman born in 1951 in this county would genuinely have, which is why it survives the popularity filter: this is period, not fashion. It is the most ordinary name in the book, and the book is about ordinary people protecting one another. |
| P-004 | **Terrell Vance** | An invented, region-correct surname; the first name is his mother's, and the fact that he and Cora were **not** named after the same person is the first thing about him that is wrong. Kept deliberately unmodern: he is 36 and sounds like a man who was named by someone else. |
| P-005 | **Denny Aylward** | Aylward is Anglo-Norman, "noble-bold" — a Norman name carried by a mechanic in a town with no Norman left in it. Denny is the diminutive a garage would give him. |
| P-006 | **Adela Iversen** | *adela* — from Old High German *adala*, "noble," the root of * Adelaide*. Iversen is a Scandinavian patronymic, "son of Iver." A woman with a German-Scandinavian name working as a county coroner in an American county: someone who came to the town or whose family did, a generation back, and who is therefore *inside* the network she is professionally obliged to be outside of. That is her entire character, and the name is the first sentence of it. |
| P-007 | **Sam Okafor** | *Sam* is short for Samuel, and short names are what a town gives the people it expects to keep calling by. Okafor is Igbo — "the caretaker of the choir," conventionally, and literally "Ochi Oris" in some readings. A pastor whose surname carries "caretaker of the choir," in a building with bad acoustics that is the whole setting of chapter 14. |

**One honest gap:** Rusk and Iversen are both European-origin, in a book that is
otherwise careful about whose names are in it. That is a casting question, not a naming
one, and it is recorded rather than fixed by renaming — a name swap that made the
composition look more considered without changing who is in the room would be worse than
the imbalance.

---

## Global narrative voice

**Close third, past tense, locked to Rusk. One POV character. No exceptions.**

The argument of this book is about *one person's compromised seeing* — she is the only
person qualified to read the evidence and the only person with a stake in what it
says. A book that wanders off her undermines the thesis it is built on. This is also
a deliberate divergence from *Paper Cage* (multi-POV) and *The Burning Girls* (also
close third) — the single-POV choice is made for the theme, not the market.

**Register:** quiet, not gentle. This is a direct instruction from the Tudor and
Doughty evidence: Doughty's sin was softness and she scored 3.5/5. The prose is
unsentimental and occasionally flat on purpose. Nobody performs grief.

**Sentence posture:** declaratives, short. Rusk is a person who states what she can
support. Long subordinate clauses are permitted **only** in interior monologue, and
they mark uncertainty — when the syntax opens up, she is losing her grip.

**The one thing to avoid:** the book is about a town that is careful with each other.
The prose must not imitate that. Everybody is helpful, and the narration is not.

---

## RUSK (P-001) — the investigator

**Speech pattern:** asks questions in sequence, gets complete answers, thanks people.
Rarely follows up. When she does follow up it lands hard because it is the first
unfamiliar thing she has done in the conversation.

- **Under pressure:** gets *more* procedural, not less. Numbered lists. Dates. She
  retreats into the form because the form is the only thing that is not her mother's
  daughter.
- **Marker:** precision. "Two-fifty-eight" not "about three." If she says "roughly,"
  something has gone wrong.
- **Never:** states a conclusion she cannot evidence. This is her hard character rule
  and it is the reason she is useless at ch 21 — the whole town is a conclusion and
  she has nothing to check it against.
- **Tic risk:** a chapter 4 retrospective could over-collect. The `check-uniformity`
  U6 gate watches for repeated sentence openers; Rusk's interiors are where they
  will come from.

**Voice under pressure — the one place she breaks:** she reverts to her mother's
vocabulary. Once, in Act IV. Once only.

---

## ROY HALLORAN (P-002) — the volunteer chief

**The hardest voice in the book, and the easiest to get wrong.** He is warm, useful,
and lying. His warmth must be indistinguishable from genuine warmth, because that is
what makes the book work.

- **Speech pattern:** practical nouns. He talks about what people will do, not what
  they meant. Offers help in the middle of sentences. Never finishes a thought about
  himself.
- **Under pressure:** *more* helpful. Offers food, offers lifts, offers his own
  theory. This is his tell and it must never be *signalled* as a tell in the prose —
  the reader is meant to feel it rather than see it labelled.
- **Marker:** he answers questions about himself with answers about somebody else.
- **Never:** defends himself. There is no scene where Roy says "let me explain."

**The ch 17 danger.** The chapter states outright that his kindness only happens when
observed. That is a structural clue (ledger item 10) and it is a voice risk: if the
narration labels it, the subtlety dies. **Rule: state the pattern in the plot, show
the pattern in the dialogue, never comment on it in the narration.**

---

## CORA VANCE (P-003) — the mother

- **Speech pattern:** the kitchen clock. Deflects to the practical and the domestic —
  how much sugar, did you eat, it's eleven minutes fast. Answers a hard question with
  a small logistical one, and the deflection is the tell.
- **Under pressure:** gets *shorter*. Full sentences to half-sentences. She stops
  finishing.
- **Marker:** the eleven minutes. She is the only character who knows the clock is
  fast; Rusk notices and says nothing; Terrell winds it and does not know why.
- **Never:** explains herself. The ch 27 line — "I didn't light it. I made it true." —
  is the *entirety* of her self-account, and it arrives in chapter 27 of 30.

**THE NAMED RISK.** Cora and Terrell share a surname and a secret, and both deflect
with logistics. **They must be distinguishable inside a paragraph, by voice alone.**
The mechanisms that separate them:
- **Cora deflects to the past; Terrell deflects to the future.** Cora says *was*;
  Terrell says *going to*.
- **Cora's sentences close. Terrell's don't.** She finishes; he trails into action.
- **Cora never uses anyone's name.** She says *she*, *he*, *your father*. This is
  the single sharpest separation and it must hold in every line.

---

## TERRELL VANCE (P-004) — the nephew, the arsonist

- **Speech pattern:** forward tense, always. Plans, not histories. Speaks in
  conditional: *when it's done, if nobody.*
- **Under pressure:** gets warmer. This is the horror of the character and it must be
  played straight, not signalled. Anger that sounds like affection.
- **Marker:** he calls Rusk *Del*. He is the only one who uses her first name. Nobody
  else in the book does, and his grandmother does it too, which is the point.
- **Never:** raises his voice. **Never:** explains the fire. Ch 24 lays out the motive
  whole and he does not defend it — he just lets it be laid out.

**The ch 24 requirement.** `CONF-004` sets him responsible-but-not-the-killer *for
2019 only*. He lit a fire he did not know was occupied, and he learns that. **That
learning has to be on the page in ch 24** — otherwise the leniency has no basis and
the ending reads as authorial protection, which is precisely R-04's deal-breaker.

---

## DENNY AYLWARD (P-005) — the mechanic

- **Speech pattern:** answers in order, completely, without being asked the rest of
  the question. Volunteer information. Numbers, because numbers are safe.
- **Under pressure:** *more* complete. He gets more forthcoming, which is the wrong
  way round and is the joke of the character.
- **Marker:** he volunteers the thing you did not ask about. Always relevant, never
  the thing you wanted.
- **Never:** asks a question. In the entire book Denny Aylward does not ask Rusk
  anything. This is a rule, not a tendency — it is what makes ch 25 land.

---

## PRIYA RAGHUNATHAN (P-006) — the coroner

- **Speech pattern:** technically correct and technically evasive. Answers the question
  asked, never the question meant. Uses the passive voice for anything about a person.
- **Under pressure:** gets *more* precise, and the precision is the evasion. She says
  *the decedent* and never *she*.
- **Marker:** she distinguishes between what is signed and what is believed, out loud,
  unprompted, because she is trying to teach the distinction to someone.
- **Never:** apologises. **Never:** uses the word *unfortunately*.

---

## SAM OKAFOR (P-007) — the pastor

- **Speech pattern:** the most fluent speaker in the book and the only one who
  finishes other people's sentences — kindly, and wrongly, which is how he gets
  information. He believes he is being helpful. He is a gossip who is on the side of
  the angels, and both halves of that are in the voice.
- **Under pressure:** gets warmer, and warmer is his problem. He softens when he is
  frightened, so warmth in Act III is a bad sign for the reader, not a good one.
- **Marker:** he names people by their baptism. He does this constantly, it is
  meaningless most of the time, and it is how a reader can feel that he has a list
  and is not giving it to her.
- **Never:** lies. He withholds. This is a hard rule — a single direct lie from Sam
  collapses the ch 14 list scene, which is the largest scene in the book.

---

## Blind Sort test — the four highest-risk pairs

Pairs chosen because they share a surname, a secret, a deflection habit, or a scene.

| pair | risk | what separates them |
|---|---|---|
| **Cora / Terrell** | surname, secret, logistics-deflection | past vs future tense direction · Cora's sentences close, his don't · Cora never uses a name |
| **Roy / Sam** | both are the *helpful* ones, both are lying by omission, both are liked | Roy speaks in practical nouns about what people will do; Sam finishes your sentences. Roy offers help, Sam offers interpretation |
| **Denny / Rusk** | both are procedural, both collect data, both are competent | Rusk asks; Denny volunteers. Rusk says *about three*; he says 340 |
| **Rusk / Adela** | both are professionals, both are precise, both are compromised | Rusk's precision is about *what happened*; Adela's is about *what she can defend* |

**Self-test, run at the end of every chapter that carries two of these:** cover the
names. If you cannot tell who is speaking, the scene is rewritten — not patched.

---

## The ensemble's shared risk

Ledger item 13: **everyone helpful, nobody uncooperative.** This is the book's
structural clue and it is also a voice trap. Seven distinct voices is the defence,
and the trap is that distinctive voices make the *uniformity of behaviour* look like
an accident of writing rather than a plant.

**Rule: no character in this book ever refuses Rusk a question.** Not once, not
accidentally, not in a minor part. Ch 14 makes the pattern explicit on the page; the
job of the voices is to make sure a reader never notices it happening *in isolation*
before they notice it happening *in aggregate*.
