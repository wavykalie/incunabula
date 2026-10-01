---
name: proof-panel
description: Runs three deliberately incompatible readers across a manuscript — the one who races through it, the one who reads with a pencil, and the one who did not want to read it at all. Reports where each stops, what confuses them, and what holds them. Use in Phase 4, before submission, or to test any finished section.
---

# Proof-panel — three readers who owe the book nothing

Three readers with different priorities and different tolerances read the manuscript and
report. The point is diagnosis, not praise.

One model asked for five perspectives returns five versions of the same bias. Three
thoroughly specified readers give more signal for less noise. Where the three agree that
something is wrong, it is genuinely wrong. Where only one objects, it is worth checking
before acting.

---

## The three readers

### The Devourer

Reads three or four books a month and reads them fast. Does not analyse — feels. A book
that flows is finished in two days; a book that snags is abandoned around page thirty and
never reopened.

Values pace above everything, strong feeling in the body, accessible language, and chapters
that pull into the next. Tolerates thematic complexity, plain prose, and moral ambiguity as
long as it does not slow down and the stakes stay clear. Cannot tolerate chapters that run
too long, explanatory paragraphs that halt the action, statistics stacked without narrative
threading them, or a point repeated after it has been made.

Reports like this: *"I snagged at page X. Chapter Y dragged here. I nearly quit. What kept
me was Z. The best moment was W — I felt it physically."*

Voice: direct, informal, impatient.

### The Critic

Reads with a pencil. Trained in literature. Reads reviews before buying. Compares against
everything else, and is demanding but fair — when something is good, they name precisely
why.

Values originality (*I have read this before* is a death sentence), thematic depth,
prose that surprises, internal coherence, and subtext. Tolerates slow pace if the prose
earns it, ambiguity and open endings (prefers them), and structural complexity. Cannot
tolerate cliché in phrase, character, or arc; exposition a reader could have deduced;
inconsistency between chapters; superficiality dressed in fine vocabulary; or a character
announcing what the book has taught them.

Reports in close analysis, citing what works at the macro level and where the line level
fails, and quoting other books as comparison.

### The Hostile

Did not want to read this. Opened it sceptical and is looking for a reason to stop. If
they fail to find one, their respect is worth more than any praise.

Actively hunts logical holes, emotional manipulation (feeling engineered without the setup
to earn it), dubious data, a condescending tone, contradictions between chapters and
between tone and content, self-indulgence, and any smell of machine authorship — predictable
vocabulary, over-symmetric structure, metaphors no person would reach for.

**The Hostile is also the monotony reader, and this is the check only they can make.** They
read the book in one sitting, so they are the one who can feel that chapter six has the same
shape as chapter two. Before reporting, they answer these, and a *yes* to any of them is a
finding regardless of how good the individual chapters are:

- Did any chapter run noticeably longer or shorter than the others? If not, why not — and
does the book have an outlier anywhere in it?
- Did the chapters end the same way more than twice?
- Could any two chapters be swapped without the reader noticing a change in texture?
- Is there a chapter that is merely competent — no scene anyone would quote, nothing wrong
  with it either? Published books have those. A book with none of them is suspicious.

Run `tools/check-uniformity.py` and put its output in the report. A panel that praises every
chapter individually and never compares them has not read the book; it has read the chapters.

What earns their respect: raw honesty that does not ask forgiveness; a verifiable fact they
did not know; an emotional moment that works *despite* their scepticism; prose that
surprises them.

Voice: dry, confrontational, economical. One sentence of praise. Three paragraphs of
criticism.

---

## Protocol

For each reader, produce:

1. **Where they stop** — chapter, page, passage. If they find no reason to stop, say so plainly.
2. **Three biggest problems**, each quoted from the text.
3. **Three strongest moments**, each quoted.
4. **What is missing** — what this reader feels is absent from the book.
5. **Engagement score** out of ten.
6. **Would they recommend it, and to whom.**

### Reading the cross-section

| Pattern | Reading |
|---|---|
| All three name the same problem | critical — fix it |
| Two of three | a real problem — investigate and probably fix |
| One of three | possibly preference — investigate before acting |
| All three praise the same passage | confirmed strength — protect it |
| The hostile one praises it | exceptional — this is a selling point |

---

## Calibration

Engagement scores from this panel carry a measured optimism of about **+0.8**, because the
same system that wrote the prose is scoring it. Validated against external critics, the
gap held steady across manuscripts at roughly that margin.

So every report closes with the standing note:

> **In-system bias.** This evaluation comes from the system that wrote the prose. Scores
> carry roughly +0.8 of measured inflation; subtract that for a realistic external estimate.
> Anything above 8.0 needs outside validation — human beta readers, an editor.

---

## Using it

**Input:** a chapter, a part, or the whole manuscript.
**Output:** the three reports, the cross-section, and prioritised recommendations.

Run it after each part is drafted rather than waiting for the whole book, before submitting
to agents or editors, after significant revisions (to confirm the fix did not create a new
fault), and whenever you are unsure whether a passage works.
