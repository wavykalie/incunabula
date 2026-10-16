---
name: deslopify
description: Make text more genuine, natural, and feel not written by an AI or LLM by removing AI tropes and cliches. Use when asked to deslopify, naturalize, or remove AI tropes from text. Single home of the anti-AI pattern catalog and its checklist.
---
# Deslopify Text

This skill helps you rewrite or edit text so that it sounds more human, genuine, and free of the repetitive, patronizing, or grandiose patterns typical of AI-generated content.

`references/style_guide.md` is the **single home of the anti-AI pattern catalog**. The
former `humanizer` skill's catalog and `setting`'s anti-AI tell list were merged into it
on 2026-10-15 (recorded in `ERRATA.md`), and no other file restates the list.
`tools/prose/deslop-check.sh` is the mechanical enforcement; the guide is the reference
and the checklist. Read the whole guide before you edit anything.

## The pass has two halves

1. **Take the tells out.** Review the text against [references/style_guide.md](references/style_guide.md) the way you would read a draft against a style sheet. Mark every instance of the patterns (e.g. magic adverbs, the "delve" family, negative parallelism, false vulnerability, listicles in a trench coat). Rewrite each one while preserving the core meaning, intent, and register of the original. Prioritize clear, direct, and varied human-like prose.
2. **Put the person back.** The guide's closing section, *The second half of the pass — add a pulse*, is not optional. Have a view, vary the rhythm, admit complexity, let some mess in. A text that is clean and dead has failed the pass.

**The guide is a review checklist, not a generation brief.** Read a draft *against* it, the
way you would read a draft against a style sheet. Do not paste it into a generation context
and ask for compliance — an earlier version of this skill did exactly that, and it is the
documented failure mode in VERMILLION §8.8: a brief of pure prohibitions (*no em dashes, no
rule of three*) leaks its own constraint list into the output and spends the budget on
compliance instead of on the writing. The guide's own opening section now carries the
reasoning and the "ask for this instead" table.

## The per-chapter checklist

After every chapter: scan for the forbidden vocabulary; count the em dashes and trim past
the cap; check the proportion of three-item lists; read each section's final sentence for
captionitis; read the paragraph openings in sequence and break the smooth ones; read the
result aloud — does it sound like a person, does the sentence structure vary, are the
claims specific, is the register right for its context. Then finish with the honest
question — would a sceptical reader say a machine wrote this? Anything short of a
confident no goes back.

## Two scales, and you need both

Most of the guide is visible inside a paragraph. The last section, **Beyond the Sentence**,
is not: the explanatory coda, the antithesis formula, the uniform chapter, the cloned
rhythm, the boilerplate note. These only exist in the comparison between one chapter and
the next.

So deslopify a single passage one way, and a manuscript another:

- **One passage** — work through the guide top to bottom as above.
- **A whole book** — read the chapters against each other first. Compare chapter lengths,
  compare the rhythm of each chapter's opening, count how many chapters close on the same
  move, and check whether the front matter is the same front matter another book carried.
  Fix the uniformity before touching a single sentence, because a book whose chapters are
  interchangeable will not be repaired by polishing them one at a time.

The measured numbers behind those checks, and the controls that keep them honest, are in
`tools/prose/check-uniformity.py` and `tools/prose/deslop-check.sh` (rules `A24`, `A25`, `F1`, `U1-U3`).
The guide states the principle; the tools enforce it.
