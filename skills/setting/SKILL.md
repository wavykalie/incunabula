---
name: setting
description: Line-level excellence — openings that hold a reader, dialogue that runs on subtext, and prose an editor would underline. Covers the hook, conversation, the anti-AI pass, scene transitions, how information is delivered, nonfiction prose, and line quality. Use in Phase 3, in prose revision, and wherever the writing has gone flat.
---

# Setting — the line itself

Other skills handle structure, character, and theme. Setting handles how each sentence
sounds, because a good idea delivered in dead prose is a book nobody finishes. The prose
is the interface between the writer and the reader; if the interface is bad, the content
never arrives.

---

## 1. Openings

The first page is where an editor decides and where a reader's free sample ends. It carries
more weight than any other page in the book.

**The first sentence has one job: prevent the stop.** Four kinds earn it — an immediate
situation with its consequence built in; a voice so specific the reader follows the sound
rather than the plot; withheld information that promises a reveal; or an image vivid and
unexpected enough to stick.

**The first paragraph sets voice and tone.** Within three or four sentences the reader
should know what kind of book this is: lyrical and slow, or short and hard, or a book that
keeps changing register.

**The first page makes a commitment.** By its end the reader should hold a question they
want answered, a person they want to know more about, and a sense of the tone to come.

**The first scene delivers the genre's promise.** A memoir of illness should land its
vulnerability; a thriller should make the reader feel exposed; a comic novel should have
made them laugh. If the first scene does not keep the genre's promise, nothing later is
believed.

**The first chapter makes it impossible to put down.** By its end: what is at stake, why
the reader cares about at least one person, and a concrete reason to open chapter two.

**Four diagnostics for any opening.** Remove the first sentence — does anything weaken? If
not, that sentence is decoration. Read each sentence and ask *so what?* — a sentence with
no answer is not working. Read it aloud; a stumble is a rhythm problem. And show one page to
a stranger who then cannot tell the genre: the opening has failed.

---

## 2. Dialogue

Weak dialogue is the most visible flaw in a manuscript. Exposition dressed as conversation,
everyone sounding alike, replies that answer too directly — all of it reads as amateur.
Strong dialogue is invisible; the reader feels the scene without seeing the machinery.

**Four jobs, and a line does at least one.** Reveal character (what they choose to say and
how, and equally what they avoid). Advance conflict (the state of the scene changes — calm
to furious is progress; calm to calm means cut the scene). Carry information (the riskiest
job, because it turns into exposition the moment a character explains something to the
reader rather than to the other character). Create tension (what is unsaid does more work
than what is said; two people discussing the weather while one knows the other is lying is
more tense than two people arguing openly).

**A scene also needs a fifth job, and it is the one that is hardest to brief and easiest to
cut.** *Advance nothing.* Banter that goes nowhere. An argument about a doorbell. Two people
who have to be in the same room and are not yet ready to say the thing. VERMILLION measures
the human corpus's dialogue as disproportionately **non-instrumental** — material that
advances no plot — and identifies this as the strongest single instruction available to a
writing tool: give the characters something to do with the scene that is not plot. Surplus is
what a model has no reason to generate and a reader most notices the absence of.

This is a brief, not a trim. A chapter whose every line of dialogue carries information is
not tight; it is dead, and it will read as competent and lifeless. `tools/prose/check-surplus.py`
reports speech-turn length distribution for a book, because a book whose dialogue turns all
run 8–14 words has one tempo for its whole conversation. Do not delete dialogue to move that
number — the remedy is a scene, not a cut.

**Subtext is the gap** between what a character says and what they mean. Ask about the
weather when the real question is whether he will show up this time. Techniques: answer a
different question than the one asked; contradict the words with action, saying *I'm fine*
while the glass cracks; change the subject, since avoiding the question *is* an answer; and
use silence, because not answering says more than any line could.

**Every character sounds like themselves.** Differentiate on vocabulary, sentence length,
verbal tic, certainty, and humour. Cover the names — if you cannot tell who is speaking,
differentiate harder.

**Beats over adverbs.** Most tags should be plain *said*, which the eye skips. For moments
that matter, replace the tag with a physical action that shows the state: not *he said
nervously* but the pen cap flexing until the plastic cracks. Never reach for showy verbs
(he vociferated, he opined) — they draw attention to themselves and pull the reader out.

---

## 3. The anti-AI pass

The greatest risk in machine-assisted prose is that it reads as machine-assisted. Once a
critic smells it, the book is finished regardless of structure. Apply this while writing,
not after.

The recurring tells, each with the fix:

1. **Forced symmetry** — *not X, but Y* constructions and balanced antitheses. A person
   does not speak in antithesis on every page. Rewrite most of them into plain statements.
2. **Empty poetic vocabulary** — tapestry, mosaic, alchemy, catalyst, intertwining,
   permeating, resonating, transcending, navigating one's feelings, journey-as-metaphor,
   delicate, profound-as-feeling. If it sounds like an inspirational caption, replace it
   with a word someone would say out loud.
3. **Automatic rule of three** — everything listed in threes. Vary: two sometimes, four
   sometimes, one and done.
4. **Em dash as a crutch** — the dramatic aside piled between dashes. Cap them tightly per
   page; where one is decorative, use a period, a comma, or restructure.
5. **Metaphors that decorate instead of meaning.** The test: remove the image and write the
   literal. If nothing is lost, the image was fat.
6. **Dramatic sentences opening on *And*.** If the sentence only works with the *And*, it
   is weak. Cut it.
7. **Pseudo-profound closings** — the short, wise-sounding last line of a section. Replace
   with something specific: not *maybe it was too late* but the unopened envelope, three
   months expired.
8. **Excessive parallelism** — anaphora works once per chapter, at the right moment. More
   than that is a tic.
9. **Over-smooth transitions** — every paragraph starting by connecting to the last. Cut
   thirty per cent of the transitions; hard cuts are allowed and good.
10. **Named emotions** — *a wave of sadness* instead of a man watching his coffee go cold.
    Delete the label and put an action, a detail, or an image in its place.

**After every chapter, check:** scan for the forbidden vocabulary; count the em dashes and
trim past the cap; check the proportion of three-item lists; read each section's final
sentence for captionitis; read the paragraph openings in sequence and break the smooth
ones; and finish with the honest question — would a sceptical reader say a machine wrote
this? Anything short of a confident no goes back.

---

## 4. Scene transitions

A transition is the join between one unit of story and the next. Readers never praise a good
one, which is the point — a transition that draws attention to itself has failed. What they
do notice, without being able to name it, is a book that joins everything the same way.

**Five types.** Use all of them. No type may carry two consecutive joins.

1. **Hard cut.** Leave mid-action or mid-sentence and open somewhere else, later or not.
   The most invisible option and the easiest to overuse.
2. **Time skip.** An explicit gap, marked by something the reader can measure — light,
   season, a change in routine, a healed injury. The gap itself can carry meaning.
3. **Sensory bridge.** One sensation crosses the join: a sound from the new scene already
   present in the old one, a smell, a temperature. Elegant when the two scenes share a mood,
   and it goes saccharine if the shared sensation is explained.
4. **Object handoff.** Something the reader saw in the closing scene reappears in the
   opening one, altered by the interval. Carries elapsed time without stating it.
5. **Interruption.** A scene is broken before it resolves and the next one starts on top of
   it. The accumulation of unfinished business is itself a form of tension — but resolve them
   eventually, or the book reads as noise.

**Within a chapter**, a plain break in the text does the same job for a smaller jump. Use it
when the scene genuinely changes place or time; do not use it to evade a join you cannot
write.

**How to check.** List the joins in order and name each one's type. Two of the same in a
row is a rewrite. All five of the same type anywhere is monotony, and it is the commonest
way a structurally sound book reads as flat.

---

## 5. Delivering information

Information has to reach the reader, and the moment a passage exists *only* to deliver it,
the prose dies. The rule: **naked exposition fails**, unless the telling is itself a scene
with someone at stake in it.

Five ways to dress it, all of which also advance something else:

1. **Conflict carriage.** Two people who want different things and know different amounts.
   The information surfaces because they disagree, never because one explains to the other.
   The disagreement is the excuse; the fact is the by-product.
2. **The wrong answer first.** Give the reader a partial or mistaken version early, then let
   a later scene correct it. The correction teaches twice — the fact and the reason it was
   concealed.
3. **A concrete object.** A document, a bill, a scar, a photograph, a room with one chair
   too many. The thing carries the fact and the reader does the inferring.
4. **Withheld context.** Proceed as though the reader already knows, and let meaning
   accumulate from consequences rather than explanation. Risky, and the strongest of the
   five when the consequences are unambiguous.
5. **The cost of ignorance.** A character acts on a wrong assumption and pays for it. The
   rules of the world are taught by the damage, which also gives the reader a reason to
   remember them.

**Density.** Even disguised, information arrives in two or three units a page at most.
Alternate an informative passage with one that does nothing but live in the scene. Three
consecutive explanatory units is a wall, however well disguised.

---

## 6. Nonfiction prose

Nonfiction has problems fiction does not: data that has to become narrative, reported
speech that has to stay honest and still sound alive, and argument that has to flow without
turning into a paper.

**Data as narrative.** A bare number is cold; a number with a human stake is a hook. Not
*47% of young people lack formal employment* standing alone, but the same figure attached
to what it means in a life — the count, then the thing the count does not measure. Four
ways to use a number: as a consequence, as confirmation the reader already feels, as
surprise against what they assume, or as a bare fact left to speak in an argument about
power. Keep density to two or three points a page, alternate number with reflection and
story, and never stack three data points in a row. Cite in the flow of the sentence, not in
academic footnotes.

**Reported speech.** Real people speak in nonfiction, and quoted dialogue has to stay
honest. Put a physical beat before the line so the speaker's state arrives before the words.
Quote partially — a fragment, then *I wasn't listening* — and carry personality through
indirect speech when you cannot recall the exact words. The honesty rule: if you do not
remember it precisely, do not put it in quotation marks.

**Argument that flows.** The moment an argument reads like a thesis, the reader closes the
book. Let the claim grow out of experience; replace *first, second, third* with three
scenes that build the same case; and let the reader arrive at the conclusion themselves,
so it feels like theirs.

---

## 7. Line quality

**What an editor underlines in the margin.** Specificity (a real amount, a real place).
A concrete image where an essay would have made a point. Varied rhythm — the long
accumulating sentence followed by something short and flat. A strong verb where an adverb
would have been used. And at least one sentence per chapter the reader re-reads voluntarily,
not from confusion but from pleasure.

**What an editor marks to cut.** Cliché (if you have heard the phrase, so has the reader).
Fat — *basically, literally, really, very, quite*. Abstraction where a body was needed:
*he felt a profound existential dread* becomes the tightened chest, the shaking hands, the
urge to be sick. Passive voice with no reason. Adjective piles — one strong one beats three
weak ones. **Figurative pile-ups** — two images fighting over one referent. Sensory density
is this craft's strength and its failure mode: *like chewing on copper foil while someone
struck a bronze bell inside her sinuses* is two good images in one sensation, and the
sentence loses both. One image per sensation, fully committed, beats two competing ones.
`tools/prose/check-figurative.py` points at the windows where images cluster.

**Per-chapter test.** Read it aloud for rhythm. Find three sentences that deserve
underlining; if none exist, the prose is functional but anonymous. Find three sentences
carrying fat and cut them. Confirm at least one concrete image per page. Confirm the
paragraph lengths vary.

---

## Using it

**Opening:** hand it a first chapter and run the four diagnostics.
**Dialogue:** hand it any scene with conversation — check job, subtext, voice, beats.
**Anti-AI:** hand it any chapter, run the ten tells and the six checks.
**Transitions:** hand it a manuscript or a batch of chapters — name every join and flag repeats.
**Information delivery:** hand it any expository passage and ask which of the five is carrying it, or whether it is naked.
**Nonfiction:** hand it a passage with data, quoted speech, or argument.
**General prose:** hand it anything, and get back the fat, the cliché, the abstraction, and
the chances it missed.

**Output:** revised text, annotated with what changed and why.
