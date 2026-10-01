# AI Writing Tropes — a diagnostic reference

Pattern list from [tropes.fyi](https://tropes.fyi), with measured footnotes added where this
project has its own numbers.

---

## Read this before you use this file

**Use it to review prose, not to generate it.** An earlier version of this file opened with
"add this to your AI assistant's system prompt," and that instruction was wrong in a way
worth recording.

VERMILLION (`vermillion-study/`, 140 public-domain English novels against 185 machine texts,
genre/period/length controlled) tested exactly this kind of instruction. §8.8 gave a model a
brief of pure prohibitions — *avoid clichés, no em dashes, no rule of three* — and the result
(a) leaked its own constraint list into the prose, (b) spent its budget on compliance rather
than on the writing, and (c) produced good specific detail only as a side effect. The same
section notes what a substantive brief does instead: *a missing heirloom that means something
to three generations* yields the detail directly, with no leakage.

The mechanism is not hard to see. A prohibition tells a model what shape not to produce; the
shape is still the thing being modelled, and forty-one of them are forty-one instructions to
imitate a style by describing its outline. A substantive constraint tells it what to produce.
**Style constraints make a model imitate the shape of good prose. Substantive constraints make
it produce the things good prose is made of.**

So the pattern list below stays exactly as it is — it is a genuinely good diagnostic, it
names things that are genuinely there, and several of its rows carry measurements this project
made. What changed is its job. Read a draft *against* it, the way you would read a draft
against a style sheet. Do not paste it into a generation brief and ask for compliance.

Where a pattern below has a counterpart, it is given as a **request for the thing itself**,
because that is the form that works:

| Instead of | Ask for |
|---|---|
| Vary your sentence length | A scene where the rhythm changes because something in the scene changes |
| Add a one-line paragraph for emphasis | A beat the reader has to sit through |
| Drop the connective phrases | A paragraph that opens on the thing rather than on the logic for it |
| Replace buzzwords with concrete words | A specific object that costs something to choose |
| Cut the hedging | A narrator with a position — including a position of uncertainty |
| Fill the silence where dialogue should be | Two people in a place the plot does not require them to be in |

That last row is the strongest single instruction in the study, and it is the one no pattern
list contains. VERMILLION measures the human corpus's dialogue as disproportionately
*non-instrumental* — material that advances nothing — and names surplus as what a model has
no reason to generate and a reader most notices the absence of. A chapter in which every line
of dialogue states a fact or moves someone to a new place is not badly written. It is dead.

And note what the study does **not** support. Its Finding 4: machine prose is not lexically
impoverished — it is *more* varied than the human corpus (moving-average TTR at AUC 0.739,
Yule's *K* at 0.615). "Vary your vocabulary" and "use more varied words" are not on this list
because they are not supported, and the same goes for sensory density, which runs at AUC 0.672
for the *machine* side. A stylometric finding about human prose is a finding about the sampled
humans, and the sample is somebody's canon.

---

---

## Word Choice

### "Quietly" and Other Magic Adverbs

Overuse of "quietly" and similar adverbs to convey subtle importance or understated power. AI reaches for these adverbs to make mundane descriptions feel significant. Also includes: "deeply", "fundamentally", "remarkably", "arguably".

**Avoid patterns like:**
- "quietly orchestrating workflows, decisions, and interactions"
- "the one that quietly suffocates everything else"
- "a quiet intelligence behind it"

### "Delve" and Friends

Used to be the most infamous AI tell. "Delve" went from an uncommon English word to appearing in a staggering percentage of AI-generated text. Part of a family of overused AI vocabulary including "certainly", "utilize", "leverage" (as a verb), "robust", "streamline", and "harness".

**Avoid patterns like:**
- "Let's delve into the details..."
- "Delving deeper into this topic..."
- "We certainly need to leverage these robust frameworks..."

### "Tapestry" and "Landscape"

Overuse of ornate or grandiose nouns where simpler words would do. "Tapestry" is used to describe anything interconnected. "Landscape" is used to describe any field or domain. Other offenders: "paradigm", "synergy", "ecosystem", "framework".

**Avoid patterns like:**
- "The rich tapestry of human experience..."
- "Navigating the complex landscape of modern AI..."
- "The ever-evolving landscape of technology..."

### The "Serves As" Dodge

Replacing simple "is" or "are" with pompous alternatives like "serves as", "stands as", "marks", or "represents". AI avoids basic copulas because its repetition penalty pushes it toward fancier constructions (I've studied this!).

**Avoid patterns like:**
- "The building serves as a reminder of the city's heritage."
- "Gallery 825 serves as LAAA's exhibition space for contemporary art."
- "The station marks a pivotal moment in the evolution of regional transit."

---

## Sentence Structure

### Negative Parallelism

The "It's not X -- it's Y" pattern, often with an em dash. The single most commonly identified AI writing tell. Man I f*cking hate it. AI uses this to create false profundity by framing everything as a surprising reframe. One in a piece can be effective; ten in a blog post is a genuine insult to the reader. Before LLMs, people simply did not write like this at scale. Includes the causal variant "not because X, but because Y" where every explanation is framed as a surprise reveal.

**Avoid patterns like:**
- "It's not bold. It's backwards."
- "Feeding isn't nutrition. It's dialysis."
- "Half the bugs you chase aren't in your code. They're in your head."

### "Not X. Not Y. Just Z."

The dramatic countdown pattern. AI builds tension by negating two or more things before revealing the actual point. Creates a false sense of narrowing down to the truth.

**Avoid patterns like:**
- "Not a bug. Not a feature. A fundamental design flaw."
- "Not ten. Not fifty. Five hundred and twenty-three lint violations across 67 files."
- "not recklessly, not completely, but enough"

### "The X? A Y."

Self-posed rhetorical questions answered immediately in the next sentence or clause. The model asks a question nobody was asking, then answers it for dramatic effect. Thinks this is the epitome of great writing.

**Avoid patterns like:**
- "The result? Devastating."
- "The worst part? Nobody saw it coming."
- "The scary part? This attack vector is perfect for developers."

### Anaphora Abuse

Repeating the same sentence opening multiple times in quick succession.

**Avoid patterns like:**
- "They assume that users will pay... They assume that developers will build... They assume that ecosystems will emerge... They assume that..."
- "They could expose... They could offer... They could provide... They could create... They could let... They could unlock..."
- "They have built engines, but not vehicles. They have built power, but not leverage. They have built walls, but not doors."

### Tricolon Abuse

Overuse of the rule-of-three pattern, often extended to four or five. A single tricolon is elegant; three back-to-back tricolons are a pattern recognition failure.

**Avoid patterns like:**
- "Products impress people; platforms empower them. Products solve problems; platforms create worlds. Products scale linearly; platforms scale exponentially."
- "identity, payments, compute, distribution"
- "workflows, decisions, and interactions"

### "It's Worth Noting"

Filler transitions that signal nothing. AI uses these phrases to introduce new points without actually connecting them to the previous argument. Also includes: "It bears mentioning", "Importantly", "Interestingly", "Notably".

**Avoid patterns like:**
- "It's worth noting that this approach has limitations."
- "Importantly, we must consider the broader implications."
- "Interestingly, this pattern repeats across industries."

### Superficial Analyses

Tacking a present participle ("-ing") phrase onto the end of a sentence to inject shallow analysis that says nothing. The model attaches significance, legacy, or broader meaning to mundane facts using phrases like "highlighting its importance", "reflecting broader trends", or "contributing to the development of...".

**Avoid patterns like:**
- "contributing to the region's rich cultural heritage"
- "This etymology highlights the enduring legacy of the community's resistance and the transformative power of unity in shaping its identity."
- "underscoring its role as a dynamic hub of activity and culture"

### False Ranges

Using "from X to Y" constructions where X and Y aren't on any real scale. In legitimate use, "from X to Y" implies a spectrum with a meaningful middle. AI uses it as a fancy way to list two loosely related things. "From innovation to cultural transformation" -- what's in between???? Nothing!

**Avoid patterns like:**
- "From innovation to implementation to cultural transformation."
- "From the singularity of the Big Bang to the grand cosmic web."
- "From problem-solving and tool-making to scientific discovery, artistic expression, and technological innovation."

### Gerund Fragment Litany

After making a claim, AI illustrates it with a stream of verbless gerund fragments — standalone sentences with no grammatical subject. "Fixing small bugs. Writing straightforward features. Implementing well-defined tickets." The first sentence already said everything. The fragments add nothing except word count and that familiar AI cadence. Humans don't write first drafts this way. It's a pure structural tic.

**Avoid patterns like:**
- "Fixing small bugs. Writing straightforward features. Implementing well-defined tickets."
- "Reviewing pull requests. Debugging edge cases. Attending architecture meetings."
- "Shipping faster. Moving quicker. Delivering more."

---

## Paragraph Structure

### Short Punchy Fragments

Excessive use of very short sentences or sentence fragments as standalone paragraphs for manufactured emphasis. RLHF training has pushed models toward "writing for readability" aimed at the lowest common denominator: one thought per sentence, no mental state-keeping required. It's an inhuman style. No real person writes first drafts this way because it doesn't match how humans think or speak.

**Avoid patterns like:**
- "He published this. Openly. In a book. As a priest."
- "These weren't just products. And the software side matched. Then it professionalised. But I adapted."
- "Platforms do."

### Listicle in a Trench Coat

Numbered or labeled points dressed up as continuous prose. The model writes what is essentially a listicle but wraps each point in a paragraph that starts with "The first... The second... The third..." to disguise the format. Perhaps you told it to stop generating lists and it decided to do this instead... still very common.

**Avoid patterns like:**
- "The first wall is the absence of a free, scoped API... The second wall is the lack of delegated access... The third wall is the absence of scoped permissions..."
- "The second takeaway is that... The third takeaway is that... The fourth takeaway is that..."

---

## Tone

### "Here's the Kicker"

False suspense transitions that promise a revelation but deliver a point that did NOT need the buildup. The model uses these phrases to manufacture drama before an otherwise unremarkable observation LOL. Also includes: "Here's the thing", "Here's where it gets interesting", "Here's what most people miss".

**Avoid patterns like:**
- "Here's the kicker."
- "Here's the thing about AI adoption."
- "Here's where it gets interesting."

### "Think of It As..."

The patronizing analogy. AI constantly reaches for "Think of it as..." or "It's like a..." to simplify concepts. The model defaults to teacher mode and assumes the reader needs a metaphor to understand anything. Often produces analogies that are less clear than the original concept.

**Avoid patterns like:**
- "Think of it like a highway system for data."
- "Think of it as a Swiss Army knife for your workflow."
- "It's like asking someone to buy a car they're only allowed to sit in while it's parked."

### "Imagine a World Where..."

The classic AI invitation to futurism. To sell the argument usually begins with "Imagine" followed by a list of wonderful things that will happen if the reader agrees with the premise.

**Avoid patterns like:**
- "Imagine a world where every tool you use -- your calendar, your inbox, your documents, your CRM, your code editor -- has a quiet intelligence behind it..."
- "In that world, workflows stop being collections of manual steps and start becoming orchestrations."

### False Vulnerability

Simulated self-awareness or honesty that reads as performative. The model pretends to break the fourth wall or admit a bias, creating a false sense of authenticity. Real vulnerability is specific and uncomfortable; AI vulnerability is polished and risk-free!!!!

**Avoid patterns like:**
- "And yes, I'm openly in love with the platform model"
- "And yes, since we're being honest: I'm looking at you, OpenAI, Google, Anthropic, Meta"
- "This is not a rant; it's a diagnosis"

### "The Truth Is Simple"

Asserting that something is obvious, clear or simple instead of actually proving it. If you have to tell the reader your point is clear, it very likely isn't.

**Avoid patterns like:**
- "The reality is simpler and less flattering"
- "History is unambiguous on this point"
- "History is clear, the metrics are clear, the examples are clear"

### Grandiose Stakes Inflation

Everything is the most important thing ever. AI inflates the stakes of every argument to world-historical significance. A blog post about API pricing becomes a meditation on the fate of civilization.

**Avoid patterns like:**
- "This will fundamentally reshape how we think about everything."
- "will define the next era of computing"
- "something entirely new"

### "Let's Break This Down"

The pedagogical voice that assumes the reader needs hand-holding. AI defaults to a teacher-student dynamic even when writing for expert audiences. Also includes: "Let's unpack this", "Let's explore", "Let's dive in".

**Avoid patterns like:**
- "Let's break this down step by step."
- "Let's unpack what this really means."
- "Let's explore this idea further."

### Vague Attributions

Attributing claims to unnamed authorities instead of being specific. AI loves to invoke "experts", "observers", "industry reports", and "several publications" without naming anyone. It also inflates the quantity of sources -- presenting what one person said as a widely held view, or writing "several publications have cited" when it means two. If you can't name the expert, you don't have a source.

**Avoid patterns like:**
- "Experts argue that this approach has significant drawbacks."
- "Industry reports suggest that adoption is accelerating."
- "Observers have cited the initiative as a turning point."

### Invented Concept Labels

AI clusters invented compound labels that sound analytical without being grounded. It appends abstract problem-nouns (paradox, trap, creep, divide, vacuum, inversion) to domain words — "supervision paradox", "acceleration trap", "workload creep" — and uses them as if they're established, rigorously defined terms. They function as rhetorical shorthand: name a thing, skip the argument. Multiple such labels in the same piece is a strong signal of AI slop.

**Avoid patterns like:**
- "the supervision paradox"
- "the acceleration trap"
- "workload creep"

---

## Formatting

### Em-Dash Addiction

Compulsive overuse of em dashes for dramatic pauses, parenthetical asides and pivot points. A human writer might use 2-3 per piece (and naturally); AI will use 20+.

**Avoid patterns like:**
- "The problem -- and this is the part nobody talks about -- is systemic."
- "The tinkerer spirit didn't die of natural causes -- it was bought out."
- "Not recklessly, not completely -- but enough -- enough to matter."

### Bold-First Bullets

Every bullet point or list item starts with a bolded phrase or sentence. Extremely common in Claude and ChatGPT markdown output. Almost nobody formats lists this way when writing by hand. It's a telltale sign of AI-generated documentation and blog posts AND README files (especially with emojis).

**Avoid patterns like:**
- "Every single bullet point begins with a bold keyword."
- "**Security**: Environment-based configuration with..."
- "**Performance**: Lazy loading of expensive resources..."

### Unicode Decoration

Use of unicode arrows (->), smart/curly quotes, and other special characters that can't be easily typed on a standard keyboard. Real writers typing in a text editor produce straight quotes and -> or =>. Claude in particular loves the -> arrow.

**Avoid patterns like:**
- "Input → Processing → Output"
- "This leads to better outcomes → which means higher engagement"
- "“Smart quotes” instead of straight "quotes" that you’d actually type"

---

## Composition

### Fractal Summaries

"What I'm going to tell you; what I'm telling you; what I just told you" -- applied at every level of the document. Every subsection gets a summary. Every section gets a summary. The document itself gets a summary.

**Avoid patterns like:**
- "In this section, we'll explore... [3000 words later] ...as we've seen in this section."
- "A conclusion that restates every point already made in the previous 3000 words"
- "And so we return to where we began."

### The Dead Metaphor

Latching onto a single metaphor and beating it into the ground across the entire thing. A human writer would introduce a metaphor, use it then move on. AI will repeat the same metaphor 5-10 times.

**Avoid patterns like:**
- "The ecosystem needs ecosystems to build ecosystem value."
- "Walls and doors used 30+ times in the same article"
- "Every paragraph finds a way to say "primitives" again"

### Historical Analogy Stacking

ESPECIALLY COMMON IN TECHNICAL WRITING: Rapid-fire listing of historical companies or tech revolutions to build false authority.

**Avoid patterns like:**
- "Apple didn't build Uber. Facebook didn't build Spotify. Stripe didn't build Shopify. AWS didn't build Airbnb."
- "Every major technological shift -- the web, mobile, social, cloud -- followed the same pattern."
- "Take Spotify... Or consider Uber... Airbnb followed a similar path... Shopify is another example... Even Discord..."

### One-Point Dilution

Making a single argument and restating it in 10 different ways across thousands of words. The model pads a simple thesis to feel "comprehensive" by rephrasing the same idea with different metaphors, examples, and framings. An 800-word argument becomes 4000 words of circular repetition.

**Avoid patterns like:**
- "The same point, restated eight ways across 4000 words."
- "Each section rephrases the thesis with a different metaphor but adds nothing new"

### Content Duplication

Repeating entire sections or paragraphs verbatim within the same piece. This happens when the model loses track of what it has already written, especially in longer pieces. A dead giveaway of unedited AI output. Less common nowadays.

**Avoid patterns like:**
- "The same section appeared twice, word-for-word identical."
- "Paragraph 3 and paragraph 17 are the same sentence reworded"

### The Signposted Conclusion

Explicitly announcing the conclusion with "In conclusion", "To sum up", or "In summary". Competent writing doesn't need to tell you it's concluding. The reader can feel it. AI signals its structural moves because it's following a template, not writing organically.

**Avoid patterns like:**
- "In conclusion, the future of AI depends on..."
- "To sum up, we've explored three key themes..."
- "In summary, the evidence suggests..."

### "Despite Its Challenges..."

The rigid formula where AI acknowledges problems only to immediately dismiss them. Always follows the same beat: "Despite its [positive words], [subject] faces challenges..." then ends with "Despite these challenges, [optimistic conclusion].".

**Avoid patterns like:**
- "Despite these challenges, the initiative continues to thrive."
- "Despite its industrial and residential prosperity, Korattur faces challenges typical of urban areas."
- "Despite their promising applications, pyroelectric materials face several challenges that must be addressed for broader adoption."

---

## Beyond the Sentence

Everything above is visible in a paragraph. These are not. They live in the comparison
between one chapter and the next, which means no reader can point at them and no
single-chapter check can catch them. They are also the hardest tells to shake, because
they come from doing the same competent thing every time rather than from doing
anything badly.

The measurements below are real: 48 chapters and 177,047 words of published narrative
(Wandering Witch, Yen Press) set against two finished machine-assisted books from this
project, in different genres and written months apart.

### The Explanatory Coda

The closing move that turns the chapter's meaning over and hands the reader the
interpretation. It arrives as a small, tidy paragraph: *That is why...* *Which is why...*
*It is also why...* *The next chapter is about...* *That is what makes him the test.*

It feels like insight. It is the machine tidying up after itself, because a coda is the
cheapest way to guarantee a chapter "lands". One per book is a choice. Six out of eleven
is a fingerprint.

**Measured:** published prose — **0 of 50 chapters** close this way, and 6 coda formulas
in 177,047 words (0.03 per 1,000). The two project books: 45, 34 and 32 hits, and
15 of 25 chapters ending on one.

**Avoid patterns like:**
- "That is a refusal no other figure here makes, and it is the closest thing in the book to an answer."
- "Which is why the next emperor is a better test of the system than he was."
- "It is also why, two thousand years later, we are still reading a man whose body was taken."

Let the chapter stop where its last scene stops. If the meaning needs saying, the scene
did not carry it — fix the scene.

### The Antithesis Formula

*It was not X. It was Y.* A negation, a full stop, then the correction. It reads as
decisive and costs nothing, so it gets reached for whenever a paragraph needs to sound
like it concluded something.

The pattern spreads by imitation: once one chapter closes this way, the next one does,
and by chapter four it is the book's house style even though nobody chose it.

**Measured:** published prose — **1 occurrence in 177,047 words**, worst document 0.43 per
1,000. The project books: 0.58, 0.71 and 1.45 per 1,000 — up to 145x the published rate.

**Avoid patterns like:**
- "I did not decide to go. I did not weigh it and I did not agree and I did not turn to them."
- "The dynasty had another two hundred years to run, and the belief did not survive the century."
- "They were not religious and they were not kind."

State the thing. The correction only earns its shape when the reader already believed
the wrong version, and then it happens once.

### The Uniform Chapter

Every chapter arriving at nearly the same length. It looks like discipline and it is the
single clearest mechanical signal in a finished book, because no human writes that way.
A writer's chapters run long when the material demands it and short when it does not.

**Measured:** published chapters inside one volume run **466 to 9,184 words**; volume-level
coefficient of variation 48.4% to 70.6%. The project books: **3.2%, 5.8% and 10.8% CV**, with
one book holding every chapter between 2,401 and 2,686 words. There is no overlap between
the two groups at all.

**Avoid patterns like:**
- eleven chapters, none shorter than 2,400 words or longer than 2,700
- a plan that assigns every chapter "about 2,500 words" and a draft that hits it
- trimming a strong chapter to fit the target, or padding a thin one to reach it

If a chapter needs four hundred words, give it four hundred. A real book has an outlier
in it somewhere.

### The Cloned Rhythm

Every chapter sharing one sentence-length profile — same average, same spread, same
proportion of short and long. The prose varies inside a chapter and then resets to the
same setting for the next one, like a metronome with a heartbeat.

**Measured:** published volumes show a per-chapter mean sentence length spanning 4.3 to
11.0 words. A project book whose chapters all sit within 3.5 words of each other is
running one setting.

**Avoid patterns like:**
- every chapter averaging 17 to 19 words per sentence
- a long, accumulating paragraph opening every chapter
- the same ratio of dialogue to narration from chapter to chapter

Break the setting deliberately: let one chapter open on a two-word line, let another run
its first page as a single paragraph.### The Symmetrical Page

Two claims used to live here and they do not have the same standing, so they are separated.

**Paragraphs all about the same size.** This one holds everywhere. A model has one setting
and holds it; a writer runs long where the material runs and cuts short where it stops.
Paragraph lengths that never vary read as a wall however good the sentences are.

**Measured:** published prose lets paragraph lengths vary at CV **87–89%**. The project books:
one at **51%**. This is the transferable half — variation is not genre-dependent in any corpus
measured so far.

**Almost none of them a single line.** This one is a *publishing convention*, and a large
independent measurement puts it the other way round. A writer breaks a paragraph to one
sentence when that sentence deserves the white space around it — the landing, the punch, the
beat of silence — and in dialogue-dense commercial fiction that happens constantly.

**Measured:** published commercial fiction runs **50–62%** of paragraphs as a single sentence.
The project books: one at **14%**.

But VERMILLION (`vermillion-study/`), comparing 140 public-domain English novels against 185
machine texts with genre, period and length controls, measures short-paragraph frequency
running at AUC **0.715 for the machine side** — machine prose carries *more* one-line
paragraphs than human prose. Its human corpus is nineteenth-century, which predates the
convention; its machine corpus is Royal Road serialisation, which runs on it.

So: keep the beat-per-line instinct, because the market this pipeline sells into rewards it and
the number is real **for that market**. Do not treat 50% as a property of English prose, and do
not open with "prose with no one-line paragraphs has been laid out by a machine" — outside
dialogue-heavy fiction that sentence is simply false. The grid is the tell. The one-line
paragraph is a house style.

**Avoid patterns like:**
- every paragraph landing between 60 and 120 words
- paragraphs of near-identical length from top to bottom
- breaking paragraphs only at scene changes rather than at beats

Give the important line its own paragraph *where the market expects it*. In dialogue-heavy
commercial fiction that means routinely; in a chapter that is not dialogue-driven it means
occasionally, and forcing it is the grid this section exists to catch. The check that always
applies is variation.

### The Default Name

Language models sample names from probability peaks rather than drawing them, so the same
clusters recur across projects, genres, and unrelated books. Research on this is
model-family-specific and reproducible: *Elena Vasquez*, *Marcus Chen* and *Amara Okafor*
cluster around one family; *Elara Voss*, *Aiden Sinclair* and *Isabella Nguyen* around
another; *Thorne*, *Kael*, *Vael*, *Garrick*, *Voss*, *Hale*, *Aldren* cross the boundary
entirely.

The tell is not any single name. It is a cast that sounds invented rather than chosen —
names with no cultural grounding, no family, no etymology, and no relation to where the
characters are from. The same applies to places (*Miller*, *Hollow*, *Ash*, *Raven*) and to
any invented system the book needs a word for.

**Avoid patterns like:**
- a cast drawn from the cluster lists above, especially several together
- a sapient species or faction named for a single flattering adjective
- a magic, tech, or governance system named *Aether*, *Quantum*, *Resonance*, *Veil*
- a village called Hollow and a forest called the Whisperwood

Name from somewhere. A place with a real language and a real history produces names a
model would never reach for, and that specificity is most of what makes a cast feel
authored.

### The Boilerplate Note

The same label pasted across unrelated books — the same "working title" note, the same
provenance paragraph, the same chapter heading format, the same author bio. Two books in
different genres should not carry identical front matter, and no finished book should
carry the pipeline's own working notes at all.

**Avoid patterns like:**
- "Working titles. The book title, the subtitle and every chapter title are provisional..." on two different books
- a build script that hardcodes the same front-matter text per book
- the same dedication, the same epigraph, the same "A Novel" subtitle shape

Notes about a book's production state belong in the project's own files. A reader never
sees the pipeline.

### Consistency Is the Fingerprint

This is the rule the rest of this section follows from, and it is worth stating plainly:
**sustained consistency is itself the tell.**

Human writing is competent and irregular. It has off chapters, a section that runs long, a
chapter that ends flat because the author stopped for the night, a tic that appears for
forty pages and then dies. Machine writing is competent and even. Every per-chapter quality
check this system runs can be passed by a uniform book, because a per-chapter check never
holds two chapters at once.

So when a manuscript is uniformly good, even, and well-formed, that is not a pass. It is
the finding. Look for the absence of the accidents — the outlier chapter, the abandoned
obsession, the paragraph that only exists because it was interesting.

Reproduce the accidents on purpose. That is the whole job.

### What Was Tested Here and Rejected

Recorded because a guide that only lists its successes teaches nothing, and because several
of these are commonly recommended as AI tells and do not hold up on measurement.

- **Burstiness (sentence-length variance).** Widely cited as *the* signal. It does not
discriminate here: published chapters run a sentence-length standard deviation of 9.5, 10.1
and 10.4; the project books run 13.2, 13.3 and 14.5. Machine-assisted prose in this system
is *more* varied than published prose, not less. The live metric is the spread of those
figures **across** chapters, which is `U2`.
- **Type-token ratio (vocabulary diversity).** Also commonly cited, and not usable as
measured: TTR falls as a document gets longer, so the published chapters (mean 3,557 words)
score 28–30% against the project books' 20–22% mostly because the project chapters are a
third shorter. Any rule here needs length normalisation first. Logged, not gated.
- **The standard word-level tells.** *in the world of*, spectral and dark-imagery
vocabulary, vague attribution (*some say*, *many believe*), hedging openers, and the
*utterly / entirely / absolutely* register all measured **at or near zero in both corpora**.
The existing rules already cover them and the project books do not trip them. No new rule.
- **Perfect grammar, em-dash use alone, short fragmented sentences, overwrought metaphors.**
Not tells. All four appear in the published control.

What survived measurement is what is gated: chapter length, rhythm across chapters, the
closing coda, paragraph layout, and the antithesis formula. Everything else in this section
is the reasoning behind those five.

---

Remember: any of these patterns used once might be fine. The problem is when
multiple tropes appear together, when a single trope is used repeatedly, or when
nothing in the manuscript is ever irregular.
Write like a human: varied, imperfect, specific.