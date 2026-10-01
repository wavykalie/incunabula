# The Trick — premise (TEST CASE for Freeze 5)

**This book is the test case for the two gates added in Freeze 5.** It is the first
premise to be scoped against `check-premise-distinct.py` and `check-comps.py` *before*
any prose exists, rather than having them applied to a manuscript afterwards. Whatever
those gates say about this premise is the finding.

**Not a book in progress.** No outline, no architecture, no manuscript. The premise and
the comp set, and the gates' verdicts on them.

---

## 1. The premise

A stage conjurer, working the tent circuit in the 1930s, kills his performers using real
sleight of hand. Not poison, not a gun in a bag — the methods a working magician would
know and a coroner would not.

He travels. The book moves across at least three countries as the circuit moves, and the
sleight of hand changes with the country, because the props and the customs do.

**The engine, stated exactly:** a killer whose method is a *performance*, and an
investigator who must reconstruct the trick before she can name the man. The trick is
the clue, and the clue is useless until it is understood as a trick.

## 2. The four questions, and whether a fair-play mystery survives them

The reason this premise is worth doing is that it has a second, nested puzzle. Most
murder mysteries ask one question. This one asks four, nested:

1. **Who** is the killer?
2. **How** — what is the actual method?
3. **Why this method** — why conjuring, why not poison?
4. **Can the method be proven** — and this is the real one.

The fourth is where most versions of this book collapse, and where the interesting
version lives. A magic trick is, by definition, a procedure that produces an impossible
result and is not reproducible by an observer. So: **if the detective cannot reproduce
the trick, can she prove murder at all?**

That is a real legal and epistemological problem, not a plot convenience. The
investigator's job is to take a thing that is designed to be unbelievable and make it
believable — which is the exact inverse of what the killer does with it. The book's
central move is a character who has to learn a craft in order to disbelieve it.

**Answer, stated at premise time so it can't be fudged later:** the proof is not "he did
it" but "only someone with this skill could have done it, and the skill is on a list." The
detective reconstructs the method from the props she can find.

**The method itself is INVENTED, and that is a decision, not a compromise.** It does not
have to be a real documented conjuring effect. See §6.

## 3. The travelling structure, and why it earns itself

The multi-country setting is not decoration; it is load-bearing, in three ways:

- **The method localises.** A vanish built on a deck of cards is a European and American
  card trick. A coin, a shell, a rope routine, a light effect — each is strongest in a
  different theatre tradition. A travelling killer has to change his method to suit the
  local act, and *that* is a signature the detective can track. The route itself becomes
  evidence.
- **The props travel, the technique doesn't.** The method is the one thing the killer
  cannot buy, learn locally, or disguise. It stays his.
- **It breaks the small-town engine.** A book set in one town is a book about a place. A
  book that moves is a book about a *system* — and the system here is a circuit, which
  has its own silence, its own economics, and its own reasons for a death to be dropped.

## 4. The comps — every one verified or falsified, with a source

This is the section `check-comps.py` reads.

| recalled | verdict | what is actually true |
|---|---|---|
| Philip Carter, *The Murder of the Conjurer* (1936) | **DOES NOT EXIST** | **FALSIFIED** 2026-09-28. No such title by Carter. Carter's real conjuring books are *The Magic of the Conjurer* (1932) and *Paper Magic* (1956), both manuals, not novels. Falsified rather than verified. |
| William Hope Hodgson, *The Last of the Legions* | **DOES NOT EXIST** | **FALSIFIED** 2026-09-28. This is a different book entirely (*The Last of the Legions*, 1910, a historical romance); it is not a mystery and has nothing to do with conjuring. Recorded here because the model produced it as a comp for this premise, which is exactly the failure this gate exists to catch. |
| Kobo Abe, *The Clerk* (1959) | **VERIFIED** 2026-09-28 | Kodansha English ed., 1970. Bizarre bureaucratic dystopia, mechanisms and paperwork, no conjuring. Slot: the *system* that processes a person, not the trick. |
| Tana French, *In the Woods* (2007) | **VERIFIED** 2026-09-28 | Viking; NYT bestseller, Edgar Award 2008. A murder investigation where the detective's own history sabotages the solve. Slot: investigator psychology as an obstacle. Weak comp on tone (Dublin, literary). |

**The two that mattered — the ones that actually share the premise — are the ones the
gate cannot help with.** The nearest real book to "a killer who murders by real
sleight of hand" is a *falsified entry*. The nearest real book to "an investigator
reconstructs an impossible method" is Kobo Abe's *The Clerk*, which is not remotely
this. **This is the honest position: the specific engine is unoccupied in the comp set
this research found, and that is a finding, not a green light.** A gap found by a search
of four comps is a small sample. Before committing, the comp set needs to be widened —
and per `check-comps.py`'s own stated limit, the gate cannot widen it, only demand that
what was found be real.

## 5. The honest risks, stated before drafting rather than discovered after

1. **The trick can be a cheat.** The single worst outcome is a book where the reveal is
   "he used a secret magician's trick the reader could not have known." That is not a
   puzzle, it is a withheld fact. The cause is not that the trick is fictional — a
   fictional trick is fine — but that it was **not planted**. The rule is about
   underdetermination, not realism. Every component of the method must appear on the
   page, in the vocabulary the detective uses, before the reveal needs it.
2. **Sleight of hand on the page is nearly impossible to write.** Prose cannot render a
   vanish. The temptation is to describe the effect and let the reader infer the method.
   Mitigation: the method is understood in *props and procedure*, in a language the
   detective learns, never as a sensory "you should've seen it."
3. **A real trick can be spoiled by a reader who looks it up.** A documented effect has a
   known solution in print, so the reveal is one Google search away from collapsing for
   exactly the readers who care most. See §6 — this is a real argument for inventing.
3. **The travelling can go thin.** Three countries means three settings, and a research
   detail in one can read as a set piece. Mitigation: the travel is the evidence, not the
   backdrop — the reader should be able to reconstruct the route from the method changes.

---

## premise_axes (read by check-premise-distinct.py)

    premise_axes:
      profession: "stage conjurer (the killer) / investigator reconstructing a method"
      engine: "a murder committed as a conjuring trick, provable only by someone who can rebuild the trick"
      relationship: "the investigator must learn his craft in order to disbelieve him"

---

## 6. The method is invented. This is the right call, and here is why.

**Revised 2026-09-28.** The first version of this premise required every method to be a
*documented, public* conjuring effect, named in the text. That was wrong, and it was
wrong in the same direction as my own bad justification for `Adela` earlier in this
project — reaching for the choice that could not be objected to, because it is real, and
real is defensible. Defensible is not the same as right.

Three reasons inventing is better, and the first is decisive:

**1. A real effect has a published solution.** Any reader can look up how the French
*cinétique* vanish works, or the shell game, or *The Haunted Key*. The reveal is then one
search away from collapsing — and it collapses for exactly the readers who care most, the
ones who go looking. An invented effect has exactly one source: the book. Nobody can spoil
it. **The premise's whole engine is "learn the trick to disbelieve the killer," and a
trick the reader can look up short-circuits the second half of that.** A real effect
actively damages the plot.

**2. The real method is not actually credible as murder.** Documented effects are
performed in a lit room, at a known distance, to a compliant audience, with a table, with
time, and with a second person. A murder is none of those. Fitting a stage effect to the
facts of a killing — no audience, no table, a body to account for — tends to produce
*complications* a conjuror would not attempt, which then have to be explained away.

**3. Invented lets the method be designed around the plot instead of around the
tradition.** The method is chosen for what it does to the evidence: what it leaves behind,
what it requires the killer to have brought with him, what it forces the detective to
learn first. Inherit a method and you inherit its constraints; design one and it is
plumbing.

**What "plausible" has to mean, precisely.** Not *documented* — **internally
consistent.** The standard:

- **Mechanically complete.** Every part of the method is a real, describable piece of
  handling or physics. Nothing is exempt from explanation. The reveal is an *explanation*,
  not a *declaration*.
- **Planted before it is needed.** Each component appears on the page — a prop, a
  marking, a habit, a repeated phrase — at least two chapters before the reveal requires
  it. This is the same standard the pipeline already applies to every high-impact beat:
  confirm the character is shown vulnerable, trying, and at stake before the turn lands.
- **The reader beats the detective, or ties her.** Her reconstruction must not contain
  one insight the reader could not have had from the planted evidence. If it does, the
  book is a reveal, not a puzzle, and the fair-play contract is void.
- **It respects the cost.** She has to *learn* it — a year of it, or a season — and the
  book has to show the learning. A craft acquired in an afternoon is a plot device. A
  craft that takes a year of failure is a character.

**The one thing that is still forbidden:** the trick working because the author needed it
to. An effect that requires a coincidence the killer could not have arranged and the
detective could not have anticipated is not a trick, it is an author's escape hatch. If
the solution depends on something that only appears at the reveal, the puzzle is a
withheld fact wearing a costume.

**Bearing on §4.** Because the method is invented, the *comp set matters less than it
would have.* The relevant comps are no longer "murders committed as real conjuring
tricks" — they are novels whose engine is *a reconstruction the reader can follow*:
*In the Woods* for an investigator whose method is her own obstruction, Abe's *The Clerk*
for a system that processes a person through paperwork. The specific-solution problem the
comp set flagged as unoccupied is largely dissolved by the decision to invent. The
remaining research need is narrower and is about **structure**, not subject: how other
books pace a reconstruction the reader performs.

---

## 7. The rulebook is the author's to write too

**Added 2026-09-28.** §6 established that the *method* is invented. That is only half
the licence. The deeper point is that **fair play is independent of ontology.**

A mystery is fair when every rule the solution depends on has been disclosed to the
reader before the reveal needs it. It is *not* fair when the world is realistic. Those
are different properties, and the pipeline was conflating them — the original premise
demanded *real documented* conjuring, which is a demand about plausibility, and plausibility
was standing in for fair play when it had no business doing so.

**The example that makes it obvious.** In a magical-girl story, a murder can be explained
entirely by the characters' powers — and the *better* version is that a power is fake,
hiding a different power underneath it. That reveal is completely fair, and it is fair
*because* the powers were disclosed in advance, not in spite of their being impossible.
Nobody objects to a murder mystery in a world where people can do magic. They object to one
where the culprit has an ability nobody had heard of and it arrives with the solution.

**Three levels of invention, in increasing order of risk:**

| level | what is invented | what the reader must know | fair play requires |
|---|---|---|---|
| 1 | the method, in a real world | the method | the method planted before the reveal |
| 2 | the world has powers; the rules are **disclosed** | the rulebook | the rulebook given before it is needed |
| 3 | the world has powers; the rules are **hidden** | nothing — and that is the point | **a different contract entirely** |

Levels 1 and 2 are the same contract: disclose the governing rules early. Level 3 is a
different instrument and a much harder one — the reader must be able to *infer* the
rulebook from the story's evidence. That is achievable and it is a genuinely great book,
but it is a design decision that has to be made deliberately, never discovered at the
reveal.

**The one failure mode, named in the new costume.** "The culprit had a power nobody knew
about" is the same underdetermination trap as §6's escape hatch — the solution depends on
a thing that exists only at the reveal. It is *worse* in a magical story, because a reader
of that genre is actively hunting for what the characters can do, and an unplanted power
reads as a betrayal rather than a twist. The cure is unchanged and now applies twice: the
governing rules must be on the page, at readable depth, before the reveal requires them.

**What this opens for The Trick.** Level 1 is the conservative choice, and §6 already
licenses going past it. The real prize is that **the killer's repertoire can be invented
as a school** — a body of handling that does not exist in the world, with its own
conventions, its own tells, and its own orthodoxy, which a detective learns the way she
would learn a real tradition and which no reader can look up. The methods are then
designed around what they leave as evidence, and the "how" of the mystery is a language
the book itself invents.

**A discipline note.** *Magical Girl Raising Project* is recorded here as **the author's
example of a rulebook-invented mystery**, not as a verified comp. It has no
`**VERIFIED**` stamp and is not in the comp table, and `check-comps.py` would flag it if
it were. If it is to inform the structure, it gets verified like anything else — and
noted as a reference for *technique*, not for subject, since the subjects are nothing
alike.

---

## 8. Level chosen: 1, with an invented canon. And an invented school, `Corbeau`.

**Decided 2026-09-28.** Full design in `artifacts/01-the-corbeau-school.md`.

**The world is real; the *practice* is invented.** Physics is physics, 1930s is 1930s,
wood and cloth. Invented: one school of handling with its own vocabulary, six canon
effects, and three national orthodoxies that disagree about everything. A school is a body
of practice, and practice is exactly what people invent.

**Why not level 2.** The engine is *learning a craft in order to disbelieve a man*. Magic
makes learning trivial — and then either the ability is the reveal or it is not. A
conjurer's hands being bad at something **for years** is the thing that makes the
acquisition cost something, and it is the whole reason the fourth question has teeth. Take
away the cost and there is no book.

**Why not level 3.** A hidden rulebook makes the reveal a *declaration* rather than a
*reconstruction*. The reader who failed to infer the rules by the reveal has been told the
answer, and a puzzle has become a twist. Level 1 keeps them working.

**The design rule, and it is the one that matters:** each effect is designed around the
**evidence it leaves**, not around what a conjurer would plausibly attempt. Six effects,
each with a `[presumed / actual]` pairing. `The Reconciled` is the load-bearing one — it
leaves *no* evidence and only works on a witness already complicit in the misreading, so
the endgame is a situation where the trick is unfalsifiable because the town has agreed to
it. That is "can the method be proven" arriving as plot instead of as theme.

**The protagonist decision that carries the rest:** Elsa Reiner is **a working conjurer,
not a police officer.** If she is police, the book is an investigation with a trick in it
and the fourth question is answered by procedure. If she is a conjurer, **there is no
procedure** — she must persuade people who do not believe the thing happened that it
happened, using the only currency she has, which is a practice they may not share. The
law cannot help her and the school will not.

**Names, per the standing naming preference:** `Corbeau` is French for raven, the bird
that is never what it appears — a conjuring school named for being misread. `Elsa Reiner`,
*Reiner* being German for *cleaner*, the one who makes a method legible. `Rask` is
**deliberately plain** — a real Estonian surname meaning nothing, because he is the
counterweight and a man whose argument is that the plain thing is the difficult thing
should not carry a loaded name. All three clear of the frequency tiers and of the
catalogue.

**Still forbidden, unchanged and now load-bearing:** no component of any method may exist
only at the reveal. The school, its six effects and its vocabulary all go on the page
before they are needed, or the design is decoration.

---

## 9. RULING, 2026-09-28 — the trial, and he does not want it

**Human decision, taken on the orchestrator's recommendation.** The four-question engine
is answered by a trial, and the killer does not know one is coming.

**The structure: a hybrid, and the hybrid is the point.**

| act | what happens | what it is for |
|---|---|---|
| I | the tour. Three deaths, three countries, three orthodoxies, each staged for a retinue he assembled | the evidence, and the reader does not know a trial exists |
| II | the assembly. The circuit is forced into one place, and someone who learned the trick refuses to perform it | the reader learns what the method *is*, on the page, before the trial |
| III | the trial | the proof, and the fourth question |

**The travelling stays** even though a closed room suits the trick better, because the
three orthodoxies are how he is tracked and because the grammar he abandons in the southern
ports is how the deterioration is visible. The closed room arrives at the end as a
consequence instead of a container.

**The trial is the institution the design refused to give Elsa** (§8). She had no
procedure: she is a conjurer, the law cannot help her and the school will not. A trial is
a procedure, and the fourth question changes from *can she prove this to people who will
not listen* to *can she make a witness demonstrate an accounting*. That is a far better
question and it is a **public** one, which means the falsifiable prediction from
`07-the-test.md` becomes a spectacle: she states in open court where a named man will say
he was looking, and a room of people who do not share the school's vocabulary confirm it.

**The killer's psychology — the part that is a real change and not a set piece.** He does
**not** know, and he does **not** want it. Danganronpa's murderer performs *for* an
audience of investigators; this one has spent a career making sure there is no audience.
The dossier is the record of a man avoiding exactly this: a clean record applied for in a
city where he had never played, a challenge withdrawn the day before hearing. He is not
performing the deaths. He is *working*, and the working requires that no one competent
is ever in a position to ask.

So the trial is not his stage and he is not a performer in it. **He is a professional
caught by a procedure he has spent his life avoiding, in front of people he cannot
perform for because he does not know what they want.** He does badly. That is the point,
and it is why the ending is worse for him than a Danganronpa ending would be: he is not
defeated by a cleverer detective, he is defeated by *paperwork he considered beneath him.*

**What this forbids.** He may not monologue. He may not be delighted. He may not enjoy the
trial, and no scene may be written from his point of view. The reader gets him entirely
through what he writes and what the room does to him — the same way the dossier works, and
for the same reason. **The man who has never been in a room that was reading him is
finally in one, and it is the last thing he does.**
