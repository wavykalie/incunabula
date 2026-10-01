---
name: readership
description: Builds three to five reader personas for the book's target audience. Each persona carries reading habits, emotional triggers, deal-breakers, discovery channels, and comp-title taste. Used by the drafting, evaluation, and packaging skills for calibration and targeting.
---

# Readership — who the book is actually for

A book written for everybody is written for nobody. Readership produces concrete reader
profiles so every later skill knows exactly whose attention it is competing for.

Who consumes the personas:

- **forme** — where to set the patience threshold for pace.
- **setting** — vocabulary level, what to explain and what to assume, how hard to push feeling.
- **proof-panel** — simulates each persona against the manuscript.
- **colophon** — marketing angle, comp framing, discovery channels.
- **quoin** — which persona to unsettle (the comfortable one) and which to protect (the one closest to walking away).

---

## When to run

After the research and foundation exist, and before any drafting. Run once at setup.
Re-run only if genre, thesis, or intended audience genuinely changes.

## Inputs

`foundation.md` (genre, engagement ranking, premise, theme, protagonist, target residue),
`research/bestseller-dna.md` and any market research if present, and the project state.

## Output

`readerships.md` in the project root.

---

## Building the personas

### 1. Read the landscape

**Genre audience.** From the declared genre, establish the core reader: age band, any
gender skew, education, books per year, where they discover books (BookTok, Goodreads,
clubs, reviews, podcasts, airports), what makes them buy (cover, blurb, recommendation,
author loyalty, subject), and what makes them leave (content they refuse, pace they
cannot forgive).

**Comp-title audience.** For each comp, find who read it, what the positive reviews
praised, what the negative ones attacked, and what adjacent books those readers also read.

**Engagement to behaviour.** Translate the book's engagement ranking into how the reader
actually behaves:

| Engagement | Behaviour | Pace | Why they recommend |
|---|---|---|---|
| Empathy-first | wants connection and vulnerability | slower, savours | "how it made me feel" |
| Fascination-first | wants surprise, cannot predict | faster, chases | "you won't believe what happens" |
| Self-insertion | wants to see themselves | moderate | "this is literally me" |
| Intellectual | wants to think and argue | varies | "it changed how I see X" |
| Aspiration | wants elevation by association | varies | the book's cultural status |

The primary engagement type produces the primary persona.

### 2. Create three to five personas

Three are required:

1. **Primary** (~60%) — the core reader, mapped to the primary engagement type. Most likely to buy, finish, and recommend.
2. **Stretch** (~25%) — does not normally read this genre, but something about *this* book could pull them in. Mapped to a different engagement type.
3. **Hostile** (~15%) — predisposed to dislike it; picked it up because of hype, a club, or a gift, and is looking for a reason to stop.

Two are optional, and only when the book genuinely crosses over: a **niche** reader
(a community that adopts it for a professional or discussion reason) and a
**generational** reader (from a different age band, connecting through a different lens).

Do not pad to five. Three real personas beat five thin ones.

### 3. Fill every field

```
## PRIMARY READER: [name]

### Identity
Age: [exact] | Gender: [if it matters] | Location: [type, region]
Education: [level, field] | Occupation: [specific job, not a category]
Books per year: [n] | Format: [print / ebook / audio / mixed]

### Reading psychology
Why they read: [escape, learning, processing, entertainment — be concrete]
How they describe their taste: [in their voice]
What hooks them on page one: 
What makes them stop: [specific triggers]
Emotional triggers: [what lands hardest for THIS reader]
Re-read triggers:
Reading speed: [skimmer / moderate / savourer]
Patience for slow sections: [how many pages before they skip]
Discomfort: [do they read to be challenged or comforted?]

### Feeling
Wants to feel:
Will not feel:

### Genre relationship
Three they loved, and why (in their voice):
1. [real title] — [reason]
2. [real title] — [reason]
3. [real title] — [reason]
Three they abandoned, and why:
1. [real title] — [reason]
2. [real title] — [reason]
3. [real title] — [reason]
What they love about the genre:
What they are tired of:
Crossover taste:

### Discovery and purchase
Where they find books: [ranked]
What makes them buy:
What makes them recommend:
How they recommend: [word of mouth, link, gift, club]
Price sensitivity: [hardcover / waits / ebook / library]

### Sharing
Platforms:
What they post: [quotes, reviews, photos, takes]

### The one thing they need from chapter one
[Specific. Not "a good hook."]

### What earns a five-star review
### What loses them at chapter three
### Their test question
[Pick one of: would they finish? would they recommend? what would they highlight? where do they leave?]
```

**Stretch** reuses the template plus: why they avoid this genre; what in this book could reach past that; and the bridge element that connects their usual taste to this one.

**Hostile** reuses it plus: their expectation before reading; what would confirm it; what would convert them; and the **chapter number** by which that conversion must happen or they are gone.

**Niche** reuses it plus: the community context; how they encounter the book; and what they extract that the primary reader does not.

### 4. Derive instructions for the pipeline

**Chapter one must deliver:** for each persona, the specific need and the page it has to land by.

**Pace limits:** maximum consecutive pages of reflection before something happens; minimum
event frequency; intellectual density matched to the primary reader's tolerance.

**Content boundaries:** explicitness, darkness, humour level, and how overt the social or
political content should be.

**What each persona shares:** the type of moment each would send to a friend.

**Deal-breaker watchlist:** the four things that will lose readers — specific to each
persona, plus the AI-writing patterns that break immersion for all of them.

---

## How the pipeline consumes it

- **setting** calibrates to the primary persona. When two personas want contradictory
  things, the primary wins, and the trade-off is written down so the cost is visible.
- **proof-panel** reads the manuscript as each persona and reports where they engage,
  disengage, and leave, using each persona's own test question. The hostile pass matters
  most: a book that survives it survives everyone.
- **colophon** aims the pitch at the primary persona's discovery channels and purchase
  triggers, uses the stretch reader's bridge for crossover angles, and uses the hostile
  reader's conversion point as the strongest selling argument.
- **quoin** pushes the primary reader out of comfort while keeping the stretch reader.

---

## Rules

1. Personas are people, not demographics. "Women 25–40 who like literary fiction" is a
   segment. A burned-out therapist who reads on the train is a persona.
2. Ground every claim in comp-title audience data or genre convention. Invented audiences
   are worthless.
3. The hostile reader is not a strawman. Their objection must be one a real person could
   hold. If you cannot articulate a fair reason to dislike the book, the persona is a lie.
4. Loved and hated titles must be real books that this reader plausibly read.
5. Give a chapter number for the hostile conversion point, not "eventually."
6. Instructions are prescriptive. "No more than three consecutive pages of reflection
   before an event or exchange," not "consider the reader's patience."
7. One persona per engagement type, so the book serves more than one reason to read.
8. Every persona needs at least one deal-breaker the others do not share. If all three
   leave for the same reason, you have one persona in three masks.
9. If the foundation or outline changes materially, flag the personas for recalibration.
10. Psychographics, not demographics, do the work. Age and location are context.
