---
name: good-idea
description: Tests a raw video idea against real search demand and the channel's accumulated lessons, producing a GO / WAIT / NO verdict card and recording it in a calibration ledger. Use for "is this a good video idea", "should I film X", or "worth a video?". A bare keyword returns research only.
---

# good-idea — verdict an idea against demand and experience

Turns a rough video idea into a verdict card grounded in live search data and the lessons
the channel has already learned. Every verdict is stored, so the prediction can later be
scored against what actually happened.

**Two sources, never mixed.** The numbers come from the search API, which owns its own
gates. The judgment rules come from the channel's lessons file, read at runtime every run.
If that file is missing, judge on the numbers and gates alone and say so explicitly.

## Preflight

1. The local research service must be running — check its status endpoint and expect a healthy response. If it is down, start it.
2. The service needs a search API key configured in its environment. It authenticates from localhost, so no token is required from here.
3. Read the lessons file.

## Two modes

**Bare keyword** — a short phrase a viewer could type, such as a comparison or a tool name:
research mode. Run one search, summarise the top rows and their badges, link the table. No
verdict, no ledger entry.

**Idea sentence** — anything that sounds like *I want to* or *what if I made*: verdict mode.

## Verdict mode

### 1. Extract two to four typed phrases

The exact phrases a viewer would type into search to find this video. Entities and product
names, not descriptions. Prefer model and tool names, comparisons, and tutorial phrasing.
Never *my journey* or *testing the limits*.

### 2. Score each phrase

Query the search endpoint per phrase. The response carries the gates — the launch-wave
threshold, the seven-day interest threshold, the minimum thirty-day interest, and the
competition ceiling — plus scored rows, each with seven-day and thirty-day interest, the top
views in the current wave, thirty-day competition, whether the channel already ranks, and a
badge.

Watch the quota: each search is expensive against a daily allowance, so keep to two to four
phrases. Note the better-typed related phrases the table surfaces — the phrase worth owning
is often one of those rather than the seed.

### 3. Judge — numbers against lessons

Work through each, naming the lesson every judgment cites:

- **Dead phrase** — every phrase under the thirty-day minimum: no.
- **Launch-wave idea** — a video riding a release must clear the wave gate; if the wave is the entire premise and it is under the gate, no.
- **Own product** — a video about the channel's own tool has to be wrapped in an external entity; announcement framing dies regardless of numbers.
- **Already covered** — if the channel already ranks for the phrase, a second video competes with itself unless the angle is genuinely new.
- **Evergreen** — clearing the thirty-day minimum with modest seven-day interest means a tutorial frame; a steady search tail beats a spike.
- **Entity collisions** — check whose videos own the phrase; big numbers on a phrase owned by a different audience do not transfer, so disambiguate until the results are the right viewers.
- Anything else the lessons file says applies.

The verdict: **GO** when there is a clear phrase to own, the gates pass, and no lesson is
violated. **WAIT** when demand is real but a fixable blocker stands in the way — name what
unblocks it and when to re-run. **NO** when the phrase is dead, a gate fails, or a hard
lesson is violated.

### 4. The verdict card

```
## good-idea verdict — <short restatement>

**Verdict: GO | WAIT | NO**

**Phrase to own:** "<exact query>"  (7d <n> · 30d <n> · wave <n> · comp <n> · badge <b>)
**Frame:** wave-ride | evergreen tutorial | entity-wrap
**Format:** <hands-on test | head-to-head | build tutorial | listicle>

**Why:**
- <judgment> — cites <lesson> (<the numbers behind it>)

**Honesty checks:**
- Own product? <yes, wrapped how / no>
- Riding a real launch? <yes/no>
- Right audience on the phrase? <yes/no>

**Re-run when:** <for WAIT only — the condition and the phrase to search again>
```

### 5. Store the verdict

Record the idea, the verdict, the phrases, and one line per reason, and confirm the row back.
The ledger is a calibration record: when a verdict becomes a published video, compare the
prediction against what actually happened and write what was learned into the lessons file.
That loop is the entire point.
