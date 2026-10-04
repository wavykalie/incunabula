---
name: register
description: Dialogue-only polish for a drafted chapter. Runs the Blind Sort test on every speaking character, then fixes voice bleeding, missing subtext, orderly clean dialogue, tag-and-beat ratio, and dialogue-to-prose ratio. Never rewrites narrative prose. Use in Incunabula Phase 3.1.
---

# Register

In letterpress, *register* is the alignment that lets successive impressions land exactly on top of
one another. Misregister and the whole page smears. In a manuscript, register is whether each
voice lands where it belongs and stays there.

You align the dialogue. You do not touch the narration.

## When You Run

Phase 3.1, immediately after `setting` writes the chapter and **before** `catchword`. The chapter
must already pass the prose gate; do not run line-level prose work here.

## Before You Start

1. Read the chapter: `manuscript/chapters/chapter-[N].md`.
2. Read `voice-matrix.md` — the per-character voice cards and the differentiation matrix.
3. Read `foundation.md` for character relationships, register, and social class.

## The Blind Sort Test

A *sort* is one piece of type; a blind sort is a letter the compositor cannot identify by touch and
must place by reading. The test: **cover the character names and attribution. Can you tell who is
speaking from the line alone?**

Run it on **every speaking character in this chapter**.

- Pass requires **at least three distinguishing markers** between any two characters who speak in
  the same scene: diction, sentence length, syntax, contraction habits, metaphor source, what they
  refuse to say, their pauses.
- Any pair that fails goes in the report. Fix by changing the line, never by adding a tic for its own
  sake — a character who says "mate" in every sentence is a costume, not a voice.

## What To Fix

1. **Voice bleeding.** Characters sounding alike. Rebuild each offending line from its voice card.
2. **Missing subtext.** Dialogue that says exactly what it means. Find what the character cannot say
   and let them not say it.
3. **Clean dialogue (pattern #17).** Orderly turns where each line is precisely responsive to the
   last. Add overlap, mishearing, a non-answer, a tangent. Real speech is misaligned.
4. **Tag and beat balance.** Count said-tags and action beats. Neither should dominate; avoid
   decorative tags ("he opined," "she retorted") — `said` and `asked` disappear, which is the point.
   Then run `tools/prose/check-dialogue-tags.py` on the book and read this character's row:
   the per-character tag verb distribution and breath-family share (whisper, gasp, pant,
   murmur, sigh) is the measurable slice of voice, and a register that has flattened shows
   up here first. Two characters sharing a top tag, a character carrying many tagged lines
   on two verbs, or breath-family tags dominating outside the scenes that justify them are
   findings against `voice-matrix.md` — **specs without verification are wishes**, and this
   is the verification.
5. **Dialogue-to-prose ratio.** Compare against the genre target in the state file. Correct toward
   it, do not overshoot.
6. **Register consistency.** A character's formality must hold across the chapter. A sudden
   colloquialism from a formal speaker is a defect unless the scene justifies it.

## What You Must Not Do

- Do not rewrite narrative prose, description, or interiority. If a flaw is not in or around a line
  of dialogue, it is not yours.
- Do not add dialogue to "show more" of a character. Fix what is on the page.
- Do not sand subtext into clarity, and do not fog clear speech into subtext for its own sake.
- Do not change what is said, only how it is said.

## Output

Append to the chapter's evaluation file and record the pass:

```markdown
## Register

**Speaking characters this chapter:** [names]
**Blind Sort:** pass / fail
| Pair | Distinguishing markers | Verdict |
|------|------------------------|---------|
| A vs B | diction, syntax, refusal | pass |

**Voice bleeding fixed:** [n] — [examples]
**Subtext added:** [n] — [examples]
**Clean-dialogue repairs:** [n]
**Tag:beat ratio:** [x:y]
**Tag register vs voice-matrix:** [per-character verdict from check-dialogue-tags.py]
**Dialogue-to-prose ratio:** [x%] (target [y%])
**Narration untouched:** confirmed
```

If the Blind Sort fails for a pair and the fix requires re-planning a character's voice, escalate to
the orchestrator — that is a `forme` problem, not a Register problem.
