---
name: deslopify
description: Make text more genuine, natural, and feel not written by an AI or LLM by removing AI tropes and cliches. Use when asked to deslopify, naturalize, or remove AI tropes from text.
---
# Deslopify Text

This skill helps you rewrite or edit text so that it sounds more human, genuine, and free of the repetitive, patronizing, or grandiose patterns typical of AI-generated content.

## Workflow

1. Read the text provided by the user.
2. Review the comprehensive AI writing tropes list in [references/style_guide.md](references/style_guide.md).
3. Identify instances of these tropes in the text (e.g., magic adverbs, the "delve" family, negative parallelism, false vulnerability, listicles in a trench coat).
4. Rewrite the text to eliminate these tropes while preserving the core meaning and intent of the original text. Prioritize clear, direct, and varied human-like prose.

Always review [references/style_guide.md](references/style_guide.md) before attempting to deslopify text to ensure your edits are aligned with the established anti-patterns.

**The guide is a review checklist, not a generation brief.** Read a draft *against* it, the
way you would read a draft against a style sheet. Do not paste it into a generation context
and ask for compliance — an earlier version of this skill did exactly that, and it is the
documented failure mode in VERMILLION §8.8: a brief of pure prohibitions (*no em dashes, no
rule of three*) leaks its own constraint list into the output and spends the budget on
compliance instead of on the writing. The guide's own opening section now carries the
reasoning and the "ask for this instead" table.

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
`tools/check-uniformity.py` and `tools/deslop-check.sh` (rules `A24`, `A25`, `F1`, `U1-U3`).
The guide states the principle; the tools enforce it.
