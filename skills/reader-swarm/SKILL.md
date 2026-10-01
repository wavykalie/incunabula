---
name: reader-swarm
description: Runs large simulated reader panels — many fictional readers reacting to a manuscript or package — plus niche and sensitivity-risk scouting, public-reaction forecasting, interviews, risk heatmaps, and revision tickets. Use when a book needs crowd-level reaction rather than a small beta read.
---

# Reader-swarm — crowd reaction, simulated

Reader-swarm builds a large panel of fictional readers, lets groups react to a manuscript
or a package, interviews selected members, and writes the results to files. It is a
diagnostic instrument.

It does not certify cultural approval, publication readiness, or bestseller odds. Simulated
readers are proxies, nothing more.

## When to use it

- Panels larger than a normal beta read.
- Niche and sensitivity-risk scouting before paying a human consultant.
- Public-reaction tests for a manuscript, premise, cover copy, query, launch angle, or flashpoint.
- Forecasts of short-form, review-site, and forum reaction.
- Testing whether the book is being framed wrongly.
- Producing heatmaps and revision tickets for `corrector`.
- Re-running after revision with comparable calibration.

Do not use it in place of sensitivity readers, legal review, factual consultants, or real
beta readers.

## Output

Always to disk. A run folder under `evaluations/book-swarm/<date>-<slug>/` holding the
persona roster, the sample map, cohort reports, interviews, the public-reaction report, the
risk heatmap, revision tickets, score calibration, and a summary. If no project folder
exists, create one beside the manuscript.

## The core rule

Keep three kinds of claim apart: **simulated signal** (a hypothesis from fictional
readers), **editorial judgment** (the running agent's craft and market read), and **needs
human validation** (anything touching lived culture, religion, trauma, law, medicine, or a
protected community). Never phrase simulated niche approval as real community approval.

## Workflow

1. **Load context** — project state, assumptions, positioning, market research, prior evaluations, and the manuscript. For package testing, also the logline, query, synopsis, cover copy, and launch material.
2. **Choose a mode** — `reader-swarm` (broad beta reaction), `niche-risk` (cultural, religious, professional, geopolitical, domain-specific), `public-opinion` (social reaction to premise, excerpt, controversy, package, or angle), `package-reaction` (agent/editor/bookseller/reader response to query, copy, comps, cover, metadata), `post-revision` (compare against an earlier run on the same calibration), or `hybrid`.
3. **Build the sample map** — for manuscripts over sixty thousand words, stratify rather than reading everything, unless a full read is requested. Always include the first chapter, the last, the climax, the weakest and strongest flagged chapters, and anything revised. Record what was read fully, partially, and not at all.
4. **Generate the roster** — twelve to eighty agents by default; forty to two hundred and fifty short personas for public opinion. Give each a cohort, taste, expertise, tolerance, bias, trigger points, social behaviour, abandon threshold, and influence weight.
5. **Run the cohorts** — each reports abandon point, confusion, delight, objection, shareability, rating, and evidence. Specialist and niche cohorts return pass, flag, or block with line or scene evidence.
6. **Simulate public reaction where asked** — model three to five waves: first hook, controversy, defence, backlash, stabilisation. Track what spreads, what gets misread, who defends, who attacks, and which framing limits the damage.
7. **Interview selected members** — the strongest love, the strongest rejection, the most useful niche concern, and a representative middle response. Ask why they reacted as they did and what change would move their rating.
8. **Synthesise** — heatmap, revision tickets, calibrated scores, summary. Mark every issue *fix*, *investigate*, *ignore*, or *human-validate*.

## Default cohorts

Use only those relevant to the book: literary craft reader; genre devourer; hostile
continuity reader; anti-AI reader; literary agent; acquiring editor; bookseller or category
buyer; target reader; non-target sceptic; public reviewer; short-form reader; long-form
forum commenter; niche or sensitivity proxy.

## Persona shape

```json
{
  "id": "agent_001",
  "cohort": "niche-risk",
  "name": "fictional label, not a real person",
  "background": "specific but fictional",
  "taste": ["what they love"],
  "intolerances": ["what makes them reject"],
  "expertise_scope": "what they can judge",
  "cannot_validate": "what still needs a human",
  "social_behavior": {
    "platform": "review-site | short-form | forum | agent-inbox | private-beta",
    "activity_level": 0.7,
    "influence_weight": 1.2,
    "conflict_style": "quiet | argumentative | evangelist | skeptical"
  }
}
```

## Scoring

Report raw and calibrated side by side. The default calibration subtracts 0.8 from internal
enthusiasm unless the project has its own; caps simulated niche approval at *flag* unless a
human validated it; and keeps overall readiness within 0.4 of the weakest major gate.

```
Raw swarm score:
Calibrated score:
Confidence:
Coverage:
Weakest cohort:
Best cohort:
Still requires human validation:
```

## Risk heatmap

Severity is pass, flag, or block. Columns: area, chapter or asset, cohort, severity,
evidence, fix type, owner. Fix types map onto the revision taxonomy — structural,
connective, prose-texture, factual — plus package and human-validate.

## Revision tickets

Written so `corrector` can act without re-reading the whole report:

```
## Ticket BS-001: [title]
Severity: BLOCK|FLAG
Mode: structural|connective|prose-texture|factual|package|human-validate
Files:
Evidence:
Problem:
Required change:
Preserve:
Acceptance test:
```

## Public-reaction simulation

Produce scenarios, not certainties: best framing, worst framing, likely praise, likely
backlash, likely misread, viral lines, sample review headlines, the one-star pattern, the
five-star pattern, mitigation edits, and package changes. Useful questions to test — what
does the first sentence promise, what does the cover copy accidentally imply, which
community might feel used, which reader becomes an advocate, which posts a rejection thread,
and what gets screenshotted.

## Niche-risk simulation

Label every niche agent as a simulated proxy, give each narrow scope, avoid claims of
insider certainty, prefer *this may read as* over *this is wrong* unless the text plainly
contradicts a fact, and route anything publication-facing through human validation. For each
niche cohort, record scope, what the proxy can flag, what it cannot validate, top risks,
evidence, recommended edits, and whether a human consultant is needed.

## Optional external simulator

If the user wants to run a real third-party social simulation and one is available, the
skill can export seed files, run that tool externally, and import personas, action logs,
interviews, and reports back into this skill's output format. That integration is optional;
the in-house workflow above stands on its own. Do not vendor another project's code into
this skill.

## Final reply

Keep it short: the run folder, the calibrated score, the strongest signal, the worst
blocker, and the next action. Do not paste whole reports into chat when the files exist.
