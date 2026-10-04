---
name: collator
description: Cross-manuscript consistency auditor. Runs after every three to five chapters and again over the finished manuscript. Finds continuity errors, information-flow violations, timeline contradictions, and orphaned plot threads that no single chapter's writer can see. The skill that asks "how does she know that?"
---

# Collator — the memory the manuscript does not have

Collator is the book's immune system. A chapter writer sees one chapter; collator holds
all of them at once and checks each against the others. Writers forget: a character is
Marco in chapter three and Marcos in chapter nine, has blue eyes in chapter two and brown
in chapter fourteen, acts on a secret that is not revealed until three chapters later, is
in two cities on the same Tuesday, and leaves a thread open that never closes.

Collator finds all of it. It does not fix anything.

## When it runs

- **Batch** — after every three to five chapters.
- **Full** — once the manuscript is complete, before packaging.
- **Post-revision** — after structural changes, to confirm nothing new broke.

## Before auditing

Read the foundation (names, descriptions, relationships, world rules, geography), the
outline (chapter timeline, who appears where, threads opened and closed), and every chapter
in scope — for a batch, the current chapters *and* everything before them. Read the project
state and, if it exists, `ENTITY_STATE.yaml`.

If the entity file exists, treat it as the primary data source and work the unresolved
`conflict` entries *first*, as priority findings. For each: verify both values against the
current text; if only one survives, it resolves as minor; if both survive, classify by kind
(a physical contradiction is critical, a behavioural one a warning); and cross-check the
foundation for whether it is a deliberate arc change. If the file does not exist, build the
databases yourself from the manuscript.

---

## The audits

Five core audits, plus a sixth that only runs when the entity file is present. Every
finding is critical, warning, or minor.

### 1. Characters

Build a fact sheet per named character from every claim made about them.

**Names.** Hunt spelling drift and variant forms — the stem search that catches *Helena*
and *Elena*, common substitutions, first vs last vs full name. A name appearing fewer than
three times may be a typo of another. Grep stems rather than exact names.

**Appearance.** Collect every physical descriptor — hair, eyes, height, build, age,
distinguishing marks, habitual clothing — into a table with chapter and paragraph. Any
trait carrying two values is a finding. Eye colour, hair colour, and distinguishing marks
contradicting are critical; height and build inconsistent are a warning; a clothing detail
that contradicts in a way that means nothing is minor.

**Traits and behaviour.** Does the character who never cries cry without the narrative
noticing? Does the one who is terrible with technology suddenly hack something? Does the
left-handed one use the wrong hand? Cross-check the foundation's wound, lie, and
contradiction against what is on the page. Contradiction that *is* the arc is not an error;
only unjustified contradiction is.

**Relationships.** Who knows whom, who is related to whom. A stranger who has already
spoken to you four chapters ago, old friends who have never met, a marriage that quietly
becomes a partnership.

**Location.** Log where each active character is per chapter. A character in a place they
could not have reached by the timeline is critical; a location ambiguous across three or
more chapters is a warning.

### 2. Timeline

Build a master timeline of every event with its stated or implied time.

Grep the explicit markers — weekdays, relative time ("three days later"), specific dates,
years, seasons, times of day. Then walk it event by event: do the relative gaps actually
add up, does the day of the week follow from the previous chapter, does travel take as long
as it should, do institutions operate at the hour they are shown operating? Out-of-order or
self-contradicting time is critical; an ambiguity that would trouble a careful reader is a
warning.

Cross-check seasons and weather against the calendar — no summer heat in a December scene,
no dry afternoon after a wet morning unless the rain stopped. Track character ages against
the elapsed timeline: a two-year error is critical, a one-year error is a warning.

### 3. Information flow — the critical audit

This is what separates a competent pass from a real one. For every fact a character acts
on, verify the chain by which they could know it.

Build a knowledge record for each significant piece of information: what it is, where it
first came into existence, who was present, every transmission between characters, and who
currently plausibly knows it.

Then scan forward for references. Does the character citing this fact actually possess it
at that point? Were they present at the reveal, told on the page or plausibly off it, or did
they discover it themselves? Typical failures: knowing a secret nobody told them; reacting
to news before it arrives; narrating a thought about something they do not yet know. A
character acting on information they cannot hold is critical — it is the error readers
notice and do not forgive. A knowledge path that is plausible but never shown is a warning.

**The room.** For every multi-character scene, track who enters, who leaves, and who is
still present at the end. Anyone who left before the secret was spoken cannot later know it.

**Communications.** Log every call, message, letter, and conversation. When someone later
cites what they learned "on the phone," confirm that call happened or is clearly implied.

### 4. World rules

**Technology.** Establish the period, then hunt anachronism — and services used before
they existed. A decade of drift is critical; a specific service predating its launch is a
warning.

**Geography.** Distances that stay consistent between chapters, directions that do not
move, and real-world places described accurately.

**Institutions.** Names spelled one way, ranks consistent, procedures stable (a building
that needed a badge in chapter two still needs one in chapter eleven), and no boss silently
replacing a boss.

**Money.** Currency consistent, prices proportionate to each other and to the period, and
financial status that does not flip from broke to house-buying without cause.

**Quantities.** Every number with a unit, checked against every other statement of the
same quantity: masses, distances, durations, accelerations, counts. The failure mode is
the book inviting a careful reading and then breaking its own numbers — a load stated as
fifty units on arrival and forty on departure, a body under a force no body survives, a
tonnage moved on thrust that does not cohere with its own mass. Run
`tools/prose/check-quantities.py` and read its table; the extraction cannot see what a
number applies to, so every hit is verified against the passage before it is a finding.
Order-of-magnitude sanity for anything physical is part of this audit: the reader who
computes will compute.

**Language.** Dialect, regional vocabulary, and code-switching patterns held steady.

### 5. Plot threads

**Inventory.** Every thread with where it opened, how it opened, its status, where and how
it resolved, and its importance.

**Unpaid setup.** Objects, skills, mysteries, promises, and threats introduced with
emphasis and never paid off. Not every detail needs payoff — a meaningful share should be
pure texture — so only flag what was introduced *with emphasis*, which is what creates an
expectation. A major setup without payoff is a warning.

**The narrative ledger, cross-checked against the text.** When
`NARRATIVE_LEDGER.yaml` exists, this audit becomes a two-way reconciliation, and the
two directions have opposite severities:

- a setup the manuscript introduces with emphasis and the ledger does not record is a
  finding — the debt ledger is blind to unrecorded promises, so this audit is the only
  place they surface;
- a ledger entry marked RESOLVED whose payoff is not on the page is **critical** — a
  resolution the book never earned is the payoff-without-setup error wearing a green
  status;
- an entry marked OPEN is not itself a finding mid-book (open debt is normal while
  drafting) but is a **blocking failure at the full pass before delivery**.

Also read, at batch and full scope, the two structural patterns no single chapter's
writer can see:

- **Beat repetition** — the per-chapter emotional arcs declared in the ledger compared
  across chapters. When consecutive chapters share one arc shape, or one circuit runs
  more than twice in the book, name it with the chapter numbers. Four chapters running
  the same circuit is the book having one scene four times.
- **Scene-function duplication** — extended scenes declaring the same function. Two
  `relationship shift` scenes in a row is a rhythm; the same function carrying the
  book's long scenes is a structure that needs a reader's ruling.

**Payoff without setup.** Resolutions that lean on something never established — the
lockpick her father taught her when no such scene exists, the symbol "from his research"
when there was no research. A major resolution depending on it is critical.

**Direct contradiction.** Facts that cannot both be true: the door locked from the inside
and later entered without a key; never having been to Paris and then remembering the last
trip. Plot-relevant contradiction a reader would catch is critical.

### 6. Entity-state divergence — only when the file exists

Compare the structured state against what the text now says, because case-keeper can
misparse.

Review each unresolved conflict in the entity file and decide which value to keep, which
to change, and in which chapter. Check staleness: anything appearing in chapters past
`chapters_tracked` may be out of date — warn that an update is needed before trusting it.
Then scan for named entities absent from the file entirely: trivial one-offs are minor,
anything in two or more chapters or with dialogue is a warning, and anything in a
plot-critical scene is critical.

---

## Cross-reference sweeps

Five passes guarantee coverage:

1. **Names** — every foundation name grepped across all chapters with context, feeding the fact sheet.
2. **Time** — every temporal marker extracted into the master timeline.
3. **Knowledge-critical scenes** — every scene where new information is revealed, with who was present, then searched forward for references.
4. **Repeated nouns** — anything named in three or more chapters, checked for consistent description.
5. **Dialogue attribution** — every line checked that the speaker is present, conscious, and capable of speech, and that no speaker got swapped.

---

## Output

Write `evaluations/continuity-check-[scope].md`, where scope is `batch-N`, `full`, or
`post-revision-N`.

```markdown
# Collation: [scope]

Date | Chapters reviewed | Totals: critical / warning / minor

## CRITICAL
### [CRIT-001] [title]
- Audit: [which]
- Chapters: [N] and [M]
- Description:
- Evidence: ch [N] p [X]: "[exact quote]" / ch [M] p [Y]: "[exact quote]"
- Suggested fix: [which chapter, changed how]
- Cascade risk: [what else this might break]

## WARNING
[same shape]

## MINOR
[location and fix]

## Tracking databases
Character fact sheet · master timeline · knowledge database · open threads
```

When the entity file exists, also emit a `suggested_patches` block — keep-original, update,
add, or create, each with a reason — for case-keeper to apply on its next update. These are
recommendations, not edits. The same block carries **suggested debt entries** for any
emphatic setup the ledger has not recorded, and suggested status changes with the
chapter that would fire them — case-keeper applies, collator never edits the ledger.

---

## Modes

**Batch** — current chapters plus everything before. Prioritise characters and information
flow, because those are the errors that become unfixable later. Skip deep thread analysis:
flag opened threads but do not call them unresolved until the full pass. Append to the
running databases rather than rebuilding them.

**Full** — the whole manuscript, all audits at full depth, with the tracking databases
attached as appendices. This is the definitive pass.

**Post-revision** — the revised chapters plus their neighbours, audits one through three
only, confirming the revision introduced nothing new.

---

## Rules

1. **Not the editor.** Report; do not fix. Suggested fixes are recommendations.
2. **Evidence or it is not a finding.** Exact quotes with chapter and paragraph.
3. **Separate error from choice.** Check the planned arc before flagging an inconsistency; if it aligns, it is not an error.
4. **When unsure of severity, escalate.** A dismissed warning costs less than a missed defect.
5. **Information flow is the signature.** Spend roughly 40% of the effort there.
6. **Read the entity file first, then audit.** Verify key facts against the text rather than rebuilding what already exists.
7. **Re-read your own findings.** A false critical wastes the editor's time and erodes trust in the pass.
8. **Record what you cannot verify.** A plausible but unshown knowledge path is a warning with a note to add the missing link, not a critical.
9. **Note cascade risk with every fix.** A change in one chapter may invalidate a later scene.
10. **Accumulate.** In batch mode, grow the databases; never rebuild from scratch.
