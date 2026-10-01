---
name: voice-matrix
description: Produces the Voice Matrix — the per-character specification that lets a writer keep every voice distinct. Covers the book-level narrative register, a voice card per character including how each one breaks under pressure, the anti-pattern budgets, and benchmark samples that make the blind-sort test passable on a first draft.
---

# Voice-matrix — the specification for how prose sounds

Voice-matrix defines sound without writing any of it. It takes the foundation and outline
and produces one document precise enough that a drafting agent can tell every character
apart on the first try.

Output: `voice-matrix.md`, saved beside `foundation.md` and `outline.md`. It is the source
of truth for how each character speaks, thinks, and comes apart.

## Position in the pipeline

Runs after `forme`, before any writing (`setting`, `quoin`, `register`, `catchword`).
Needs `foundation.md`, `outline.md`, and the project state; optionally the research DNA
file and any existing samples in a voice bank.

If `foundation.md` is missing, stop. Voice comes out of character, and characters live in
the foundation. There is nothing to formalise yet.

---

## The document

### Section 1 — Global narrative voice

The register the reader swims in, present even in multi-POV work.

**Point of view.** Who narrates, the rotation between them, and the discipline: what the
voice can know, what it can only infer, and whether wrong inference is permitted (it
usually should be). State the tense, and if tense moves, state the rule for when.

**Sentence architecture.** Target average length and range. A rhythm worth naming: how
paragraphs open and how they close. Say what a paragraph is not allowed to close on —
summary and abstraction are the usual bans, image and silence the usual replacements.
Length ceiling per paragraph, with the warning that any paragraph past it must earn the
space with rising tension or accumulating detail.

Hard constraints worth setting here: no three consecutive sentences of near-identical
length; at least one very short sentence per page and one long one; fragments and
one-word paragraphs permitted but rationed per chapter.

**Register.** How formal the prose sits, on a scale from plain speech to elevated, and
which vocabulary roots carry which jobs — Germanic words for feeling, Latinate words kept
for institutional and clinical contexts, or whatever split fits the book.

**Metaphor field.** Where imagery comes from: a primary domain, a secondary one, and
domains the book refuses outright. How often metaphor appears, and the ratio of simile to
metaphor (a voice that says *like* more than *is* is a voice that approximates rather than
asserts). One hard rule: an image is never unpacked. No extension, no clarification, no
*not X but Y* follow-up. If the image needs that, the image is wrong.

**What the narrator sees first.** What this voice registers when it enters a room, what
it notices second, and what it never notices at all. Rank the senses in order of dominance
with a one-line reason each. A narrator who ignores architecture is making a choice.

**Emotional signature.** The tone when nothing is happening. The floor and ceiling of
intensity — the smallest thing the voice notices, and the largest it can carry before
language itself shows strain. How feeling arrives (suddenly, gradually, accumulated, or
displaced), and whether humour is present at all, and — if it is — when it leaves. The
departure of humour is an emotional event in itself.

**Vocabulary.** The private words the book uses repeatedly, each with the resonance it is
carrying, and a list of words the book never uses. The usual AI fingerprints belong on
that list with a one-line reason each. Name the world the vocabulary comes from: a book
whose language is medicine, or kitchens, or a particular trade.

**Forbidden constructions.** Constructions banned outright, each with an example and the
reason. Typical offenders: stacked em-dash parentheticals, *not X but Y* extensions, *the
kind of X that Y*, triple-adjective piles, a rhetorical question answered in the next
sentence, *there was something about X*, *and just like that*, *little did they know*.
Add two to four specific to this book.

**Benchmark sentences.** Three sentences that demonstrate the narrative voice at its most
characteristic. Not from the manuscript — targets the writer re-reads as a tuning fork.

### Section 2 — Voice cards

A full card for every POV character and every character who speaks across three or more
chapters. A mini card for the rest.

**Full card:**

- **How they talk.** Sentence length in speech. Vocabulary domains (the specific jargons
  and habits they draw on). Three to five verbal tics, each concrete — the opener they use
  when defensive, the word that ends conversations they are losing, whether contractions
  survive when they are angry. Then code-switching: how the voice changes with authority,
  with intimates, with strangers, and when lying.
- **Five things they would never say**, each with the reason it is impossible for them.
  These are not arbitrary; each one reveals something, and each one is a tripwire that
  tells you when the character has gone off-voice.
- **Syntax fingerprint.** Fragment use and when. Whether they favour compound sentences.
  Whether they ask declarative questions. Whether they interrupt, get interrupted, or
  finish other people's sentences. Whether they trail off, how often, and in what states.
- **Their metaphor field.** Separate from the book's: the primary domain this character
  draws from, a secondary one, and the sources they would never use. Three example
  metaphors in their voice.
- **What they notice.** Primary attention, secondary attention, and the blind spot — and
  what the blind spot says about them.
- **How they think.** Structured or associative, looping or flowing. Whether internal
  sentences run longer or shorter than spoken ones. Whether they narrate themselves
  (second person in their own head) or only react. What uninvited thoughts arrive —
  worst-case rehearsal, song fragments, counting. How interior thought is punctuated, and
  whether italics mark it or thoughts bleed into narration unmarked.
- **Voice under pressure.** Three levels, each with what changes and what survives.
  *Stress:* sentences shorten, adjectives drop, humour goes. *Overwhelm:* syntax breaks,
  words repeat, tense slips, the world narrows to one detail. *Collapse:* either the prose
  goes deliberately flat and under-described, or it runs and will not stop — and at least
  one tic survives to the end, because that is the last thing standing. Then the
  **recovery voice**: how they sound afterward, which is never simply back to normal.
  Record whether sentences get shorter or longer under strain, how vocabulary shifts, and
  what specifically breaks in their speech.
- **Three signature moves.** Recurring behaviours that fingerprint their sections, each
  with an expected frequency and what it reveals.
- **Blind-sort markers.** Three things that identify this character with the name removed.
  Check them against every other character: if any marker could belong to someone else, it
  is not a marker yet.
- **Two dialogue samples**, one ordinary and one under pressure, visibly different from
  each other. Plus three lines that should be attributable by voice alone.

**Mini card:** role, the one thing that identifies their dialogue, where their vocabulary
comes from, one tic, one thing they never say, and one sentence on how they change under
pressure.

### Section 3 — Differentiation matrix

The blind sort is a judgement; this is the proof. Lay every character's properties side by
side in a table — spoken sentence length, thought sentence length, vocabulary, metaphor
source, two tics, humour type, pressure response, what they notice first, interruption
pattern. Then, for every pair, list three differences that would survive the blind sort,
and name the one dimension where the pair is closest, with the distinction that still
holds there.

The rule: two characters may share one voice property, not two. Any pair sharing more gets
pushed apart until at most one remains.

### Section 4 — Anti-pattern budgets

Split into two kinds.

**Failures (zero tolerance).** Every character sharing one rhythm, so five lines from each
could be shuffled without anyone noticing. Literary metaphors in the mouth of someone who
would not have them. Voice under pressure identical to voice at rest. Narrator register
bleeding into a character's thought. Perfect grammar during a crisis. Dialogue that reads
like therapy, where characters name their wounds aloud instead of deflecting.

**Budgets (per chapter, max).** A table covering forced symmetry, empty poetic vocabulary,
automatic rule-of-three, em-dash pile-ups, metaphors that could apply to anything,
dramatic *And* openings, pseudo-philosophical chapter closings, excessive parallelism,
over-smooth transitions, named emotions ("a wave of"), simile extension (the single
biggest AI tell — after every image, does the next sentence explain it?), binary negation
openers, fake-precise numbers, demonstrated emotional control, confident description of a
place the character has never been, mug-ready philosophising, orderly turn-taking dialogue,
thematic saturation, graduated reveal as default structure, and reported body temperature.

Two budgets earn their own calibration tables: em dashes and simile extension, both set
per genre, because the tolerable maximum differs sharply between literary fiction,
commercial fiction, memoir, romance, and prescriptive nonfiction. For simile extension,
the test is one sentence: does it restate, clarify, or unpack the image (cut), or does it
add something the image cannot carry on its own (keep, and flag for review)?

### Section 5 — Benchmark samples

What the writer actually internalises. Budget roughly 40% of the effort here, because a
writer who reads only this section should still produce accurate prose.

For each POV character: **at rest** (two to three paragraphs, no plot, just the voice
existing), **under pressure** (the same character in crisis, visibly different), **an
irrelevant thought** (something unrelated arriving uninvited mid-scene and leaving without
comment), and **dialogue** with another character, showing a tic, a code-switch, and at
least one reply to the wrong thing.

Every sample is annotated: which sentence demonstrates which choice, where a signature
word lands, where the metaphor domain shows, what is deliberately absent. Then three
published benchmarks — real books with genuinely distinct voices — each with the specific
technique that makes the distinction work and how it applies here.

---

## Method

1. **Extract.** Pull every voice specification out of the foundation explicitly. These are hard constraints.
2. **Infer.** From wound, lie, want, need, contradiction, and distortion, derive properties the foundation leaves implicit — the abandoned character who braces by shortening sentences, the catastrophiser whose interior monologue runs on. Mark each inference clearly as inferred, so the writer knows which constraints are fixed and which are interpretive. Where an inference and a writer's instinct conflict, the instinct wins; where a specification conflicts, the specification wins.
3. **Differentiate.** Put all POV properties side by side, force apart any pair sharing two or more, build the matrix, and confirm three blind-sort differences per pair. Fewer than three means revise.
4. **Budget.** Set the genre-calibrated budgets, refined against research data if it exists.
5. **Sample.** Write the benchmarks, then read them aloud. Do they sound like a specific person, or like competent writing? If the latter, rewrite — the goal is specificity, not quality.
6. **Validate.** Run the blind sort on every character. Check the cards against the foundation (the foundation wins on conflict). Sanity-check that the budgets are achievable rather than punishing. Scan the samples for any word the document itself forbids. Confirm the profile fits the genre or that any subversion is deliberate. And compare rest against pressure for each character: if you have to squint to see the difference, the pressure spec is too weak.

---

## Consumers

| Skill | Uses |
|---|---|
| `setting` | the whole document; cards before every chapter, samples as the standard |
| `quoin` | pressure specs and budgets, so disruption respects the voice |
| `register` | speech patterns, tics, code-switching, never-say lists |
| `corrector` | budgets and blind-sort markers |
| `proof-panel` | samples as the comparison standard |
| `catchword` | the global profile, for opening calibration |

A weak matrix makes every downstream skill worse. This document is the multiplier.

## Secondary output

Save `voice-matrix-report.md` alongside: what it was generated from, the genre, which
characters got full and mini cards, the budget profile applied, blind-sort result per
character, the most significant inferences and their reasoning, any tension between voice
requirements and how it was resolved, and a note for the writer before chapter one.

---

## Rules

1. The foundation is upstream. Deepen it; never contradict it.
2. Voice comes from character — background, wound, education, region, age, work — never from the writer's preference.
3. Specific beats excellent. A specific mediocre voice is worth more than a generic good one.
4. The blind sort is pass/fail and it is the document's whole purpose.
5. Pressure voices are mandatory. Without them characters read as templates and the craft score caps out.
6. This document is prescriptive, not advisory. Deviation is a voice-consistency failure.
7. The samples are the product; the earlier sections are reference.
8. Mark inferences as inferences.
9. Budgets are ceilings, not targets. A chapter at zero is clean, not under-budget; a chapter at maximum across every budget is suspicious.
10. It is a derived artifact. If the foundation changes, regenerate it.
11. Every decision is genre-aware. A thriller matrix and a literary matrix should not look alike.
