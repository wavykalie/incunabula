# DRAFTING FRAMEWORK

**Written 2026-09-28, replacing every word target in the pipeline.** Applies to fiction
and non-fiction. There are no numbers in this document that describe how long anything
should be, and that is the point of it.

## The rule, and what it rests on now

**A chapter is as long as the thing in it takes, and not a word more.** No length target
goes into a drafting document.

**This is a convention, not a finding.** It was a finding once; the evidence was traced to
a filing artifact on 2026-09-29 and withdrawn, and a re-derivation from the published corpus
on 2026-09-29 failed to replace it. Two candidate mechanisms were measured against the six
published volumes that carry real chapter boundaries, and **both were falsified.** The
measurements are in `ERRATA.md`; the short form is that nothing available here can tell a
real chapter boundary from a cut one.

So the rule is kept because it is a good way to work, and it is labelled as a convention so
that nobody cites it as a law or spends a gate defending it. **It carries no numeric claim
and no distributional promise.** Nothing in this document says a book written this way will
score inside any band, because nothing in this project has shown that.

The one thing the corpus does support is the band itself, which was re-measured here
independently of our own books: 33.3–45.0% CV across six real volumes, 303 chapters,
agreeing with the recorded figures. That is what `U1` is calibrated on, and it stands.

## The finding that removed the numbers — WITHDRAWN 2026-09-29

Three books, measured against the same frozen instrument:

| book | range | ratio | CV | written with length targets? |
|---|---|---|---|---|
| Merope 1 | 478 – 2,304 | 4.8× | 40.9% | ~~no~~ **yes** — 2,450 × 7, declared |
| Merope 2 | 519 – 2,406 | 4.6× | 40.0% | ~~no~~ **yes** — 2,450 × 7, declared |
| The Trick | 1,460 – 3,442 | 2.4× | 23.7% | **yes** |

**Why it is withdrawn.** The Merope manuscripts were seven chapters when they were written,
to an outline reading `7 chapters × ~2,450 words`, and they scored **CV 5.8% and 10.9%** —
the most uniform books in this project. They were later re-partitioned into eleven chapters
in place, and the re-partitioned files are what the table above measures. 97–99% of every
eleven-chapter file is verbatim seven-chapter prose, and the word totals hold to within
0.5%. Cutting the archived prose to those sizes reproduces **41.0% and 39.9% exactly**,
with nothing written.

The "no" in that column described a file. It was read as a description of the drafting.

The 478-word chapter held up below as a model of a legitimate short scene is the last 475
words of a 2,173-word chapter, split off by the same operation. The book ends 39 words
before where it actually ends.

**What this changes.** The correlation the framework drew was an artifact of a file
overwrite. Every book measured here that was genuinely drafted to targets scored *lower*,
not higher — 5.8%, 10.9%, 23.7%. The one book drafted from scratch with no targets of any
kind, `muzzle-and-marrow`, scores **12.1%**, well under the 33.4–45.1% band.

**So the honest position: this project has never shown that a book drafted without length
targets lands in the band.** The books that scored in the band got there by being cut
afterwards. That is not an argument for putting numbers back in — a plan followed exactly is
still a plan followed exactly — but it is an argument against claiming the numbers as
support, and against reading the pilot's 12.1% as a defect.

## The re-derivation, and why it failed

Attempted 2026-09-29, against `tools/prose/calibration/corpus/multivolume/` — the only
chapter-level published data in the repository, six volumes with real boundaries.

**First, a limit worth stating.** The 140-novel public-domain corpus cannot answer this. It
is sliced into fixed 2,150-word chunks by `chunk-pd-corpus.py` and has no chapter structure
of its own, so it holds no evidence about how long chapters should be. Any claim resting on
it would be the same category of error as the one being corrected.

The band was re-measured from the six real volumes and reproduced: **33.3–45.0%**, 303
chapters, against the recorded 33.4–45.1%. The calibration is sound.

**Candidate 1 — distribution shape.** Every one of the six real volumes is right-skewed
(0.27 to 2.39). The pilot is −0.08 and the re-partitioned Merope books are 0.04 and 0.52,
which looked like a clean discriminator: real boundaries make a short tail, cut ones make a
flat distribution.

Falsified. Re-partitioning each volume's own prose into random equal-count parts produces
skewness from −0.90 to 3.12 — the real values sit inside the null, and **2 of 6 real volumes
fall below the null's 25th percentile.** The apparent signal was the null, not the books.

**Candidate 2 — short chapters close the same way long ones do.** If the rule is right, a
500-word chapter should end as resolved as a 3,000-word one, because it finished its thing.
Scored 36 short and 267 long published chapters on whether the closing paragraph leans
resolved or suspended. **0.36 against 0.36.** No separation at all, and the measure is a
word-list proxy too crude to rescue with a better one.

**What this means.** Two plausible mechanisms, two clean falsifications. The honest
conclusion is not "the rule is wrong" — it is that **the question cannot be settled with the
data in this repository**, and a rule that cannot be checked should not be stated as though
it were derived. Hence the demotion above.

This is the tenth instance of the recurring failure, and the first where the tempting move
was to publish a mechanism because two measurements had not yet come back. Earlier nine:
KF-004, KF-005, Freeze 8, Freeze 9, deletion-layer escalation, archive-as-graveyard,
three-copies, the from-scratch U1 failure, the re-partition evidence. The cheaper fix
applies again: **name the state, don't build a detector.**

## Why the earlier design failed, precisely

It failed because a design that can be satisfied by arithmetic will be.

A CV target is a number about a distribution. A plan that sets 17 chapters at 3,150–4,220
and 17 at 1,760–2,000 produces a two-point distribution that scores 33.7% — inside the
33.4–45.1% band — while the two clusters are each internally tight. **U1 measures spread
and cannot tell "these chapters differ because they contain different things" from "these
chapters differ because a plan assigned them to two buckets."** The row is not wrong. It is
answering a narrower question than the one that matters.

That is a limit of the instrument, not a defect in any book, and it belongs in `ERRATA.md`
as such. It is not work to do on a manuscript. **No manuscript should be edited to satisfy
it twice.**

## The rule

**A chapter is as long as the thing in it takes, and not a word more.**

That is the whole framework. Everything below is what follows from it in practice.

## What a chapter is, and therefore how long it is

Chapters are not sized. They *end*. A chapter ends when the thing it was about has been
finished and the reader knows it, and the reliable symptoms are:

- **It has a question that got answered**, or a question that got definitively *not*
  answered and everyone now knows that. (Arrival, refusal, a document, a question put.)
- **Somebody has been somewhere and come back.** (A scene that happened.)
- **A thing that was withheld has been spent or explicitly not spent.** (The release, or
  the decision not to release.)

A chapter that has none of these is not short. It is unfinished, and lengthening it will
not fix that.

The failures this prevents, in order of how often they happen:

- **The stub.** A chapter under about 600 words that contains a scene. Real and legitimate.
  ~~A 478-word chapter in Merope 1 is a whole scene and it is the reason that book has a
  4.8× range.~~ Withdrawn: that chapter is the tail of a 2,173-word chapter, split off by
  the re-partitioning described above. It contains no scene. The stub failure is real; that
  was not an instance of it.
- **The filler.** A chapter that is 1,200 words because 1,200 is near the middle of the
  other chapters. Symptom: it is the same length as its neighbours, not because of what it
  contains.
- **The quota chapter.** A chapter that exists at a target length. Symptom: the outline row
  for it has a number in it and the "what happens" column is one clause.

## In practice, per chapter

1. Write the scene. Stop when it is finished.
2. If it stopped early, ask *what is this chapter about that it has not finished saying.*
   Answer, and write that. Do not answer by adding description of what already happened.
3. If it ran long, ask *what is the first sentence a reader could have stopped at.* Cut from
   there, not from the end.
4. **Never pad, never trim to a number, never append a closing section.**

## Where the numbers still legitimately live

Two places, and only two:

- **The book.** A declared total length for the whole manuscript is a real contract with
  the author and it is enforced by `check-length.py`. It stays.
- **The sweep.** `check-uniformity.py` reports the actual distribution at the end, once,
  on a finished book, and it is read as *information about the book*, not as a thing to be
  optimised. A book that fails U1 is a book worth looking at. A book that passes U1 by
  being bimodal by design is a book that has been gamed, and this document exists so that
  nobody does that on purpose again.

## The honest bit

This framework cannot be checked by a gate, and that is a defect in it, not a virtue.

There is no instrument that can tell whether a 900-word chapter is a complete scene or a
trimmed one. The U rows measure shape. Shape is a proxy. The only test of this rule is
somebody reading the chapter and asking whether it finished, and that is a person, and
they are the reason this file is a set of instructions rather than a script.

The project already knows the failure mode of the alternative. `USER_PREFERENCES.md` and
`KNOWN_FINDINGS.md` between them record three cases of a measurement being laundered into
a preference, a preference into a rule, and a rule into a verdict. This framework refuses
the third of those on purpose, which is why it is the shortest document in the repository.

## Applies to

- **Fiction.** Scenes, arrivals, refusals, documents, set-pieces, rests.
- **Non-fiction.** An argument that finishes; a chapter that is one question; a chapter
  that is a single case study; an introduction that is genuinely two pages.
- **Series.** Each book separately. A book in a series gets no length guidance from its
  neighbours any more than a chapter gets any from its chapters.
