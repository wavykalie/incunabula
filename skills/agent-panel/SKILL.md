---
name: agent-panel
description: Simulates a literary agent, an acquiring editor, a bookseller, and a target reader reviewing a book for market viability and submission readiness. Use on a concept, opening pages, synopsis, query package, or a finished manuscript.
---

# Agent-panel — the market-side stress test

This skill does not write anything. It decides whether the people who stand between a book
and its readers would keep reading, ask for pages, buy, stock it, or pass.

Run it when a concept exists, when market research needs pressure-testing, when the first
ten pages need a commercial read, when a full draft is being considered for submission, or
at the audit, final-score, and delivery phases.

## The four voices

One verdict each, independent:

1. **Literary agent** — query hook, category clarity, comp fit, sellability, submission risk.
2. **Acquiring editor** — manuscript strength, list fit, editorial labour required, positioning.
3. **Bookseller / category buyer** — shelf fit, cover and copy expectations, the promise the book makes.
4. **Target reader** — opening pull, emotional promise, readability, whether they would recommend it.

## Inputs

Read whatever exists: the project state, market research, positioning notes, opening pages
or chapters, synopsis, query, cover copy, and the scored evaluation. Where a market artifact
is missing, flag it as a blocker rather than inventing confidence.

## Verdicts

- **PASS** — would continue, request, acquire, stock, or recommend.
- **FLAG** — viable with specific fixes.
- **BLOCK** — would reject or abandon for commercial or product reasons.

The overall verdict is the weakest of the four. One block means not market-ready.

## Criteria, scored out of ten with brief evidence

Category clarity · reader promise · opening-page pull · voice distinctiveness · comp-title
fit · commercial pacing · emotional stakes · shelf and thumbnail fit · submission package
strength · launch and platform leverage.

## Output

Written to `evaluations/agent-panel.md` inside a project.

```markdown
# Agent Panel

## Overall verdict
[PASS/FLAG/BLOCK] — [one sentence]

## Verdicts
| Role | Verdict | Reason |

## Scores
| Criterion | Score | Evidence |

## Top rejection risks
## Fix before submitting
## Best market angle
## Package notes
[logline, synopsis, comps, cover brief, author bio]
```

## Rules

- Be candid. Do not flatter weak work.
- Use present-market logic; flag comp titles that have aged.
- Never promise bestseller status.
- Keep taste objections separate from commercial blockers.
- For Portuguese-language projects, judge Portuguese-market fit unless the user asks for a global read.
