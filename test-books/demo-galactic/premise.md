# Bell Tide — premise

**Demo project.** Not a real book. This exists to test one thing: whether the pipeline
produces names with *reasons* when the author has stated a naming preference, and whether
that preference can be **declined** where it does not fit.

**Preference consulted:** `USER_PREFERENCES.md` §1 Naming — read, applied, not enforced.
**Preference declined in one place:** see §4, character 5. That decline is the actual
test. A preference that cannot be declined is a rule.

**Benchmark:** Kenji Miyazawa, *Night on the Galactic Railroad* (1934). Not for its plot.
For its naming, which the research turned out to be a *system* (see `research/namings.md`).

---

## 1. The story

A fen village built on a pump house. The pump is the only reason the ground is dry; it
has run on the same schedule since before anyone alive was born. Swithin Garrow, 14, is
the pump-keeper's grandson and the last person who knows the schedule by feel rather than
from the board.

On the night the pump is due to run, it does not. The water comes anyway.

What Swithin knows, and cannot prove, is that the pump was not broken. It was *let go* —
by a man who profits from a flooded fen, and who has done this once before, decades ago,
to a village that could not prove it then either.

The book is about whether a thing that is obviously true counts if nobody can demonstrate it.

## 2. Cast and the logic of the naming

The Miyazawa system, stated as a rule this book can apply:

> **Every name is drawn from the world of the story — its work, its weather, its saints,
> its past — and every name is one the character's family would plausibly have chosen.
> No name comes from outside the fen.**

| # | name | derived from | why it fits this character |
|---|---|---|---|
| 1 | **Swithin Garrow** | St Swithin's Day, 2 July — the old rain charm: *if it rains on Swithin's day, forty days of rain follow* | A pump-keeper named for a saint who predicts water. The name is a job description in a fen. Also: forty days is longer than anyone waits. |
| 2 | **Hesper Garrow** | *hesper* — the evening star; also the evening office in the Book of Common Prayer, which has a hymn about the sun going down | His grandmother, who keeps the parish almanac and the last page of numbers anyone wrote down. Evening star, and a woman who is the last light in a village. Surname shared: it is the same family, and the root repeats because the root is theirs. |
| 3 | **Ivo Parr** | A *parr* is a young salmon, a fish that returns to the river it was born in to die | The boy who fishes the drain and knows the water better than the pump does. A fish that goes home. He is the one who will leave. |
| 4 | **Anstice Coombe** | Old English *anstice* — "a thing that is opposite, a counterpoise, that which answers"; a word from riddles and charms, one of the oldest words in the language | The girl who wants the fen to flood. The name is literally *the answering thing* — the argument that answers his. The deepest root in the book, given to the person who is his opposite. |
| 5 | **Joe Cobb** | **nothing** | See §4. |

## 3. What the preference did and did not do

It did not produce `Anstice` because `Anstice` is pretty, or old, or unusual. It produced
it because the *oldest word in English for a thing that answers another thing* belongs to
the character whose entire function in the book is to answer. The name came after the
function and was checked against it. That is the direction of travel that matters — a name
chosen to fit a role, not a role built to fit a name.

`GATE_FREEZE.md` Freeze 4 says the gate is "deliberately blind to whether a name is
good." Nothing in the frozen suite could have produced `Anstice Coombe`, and nothing
would have complained. The gate's job is only to stop the model reaching for `Priya`.

## 4. The decline — character 5

**Joe Cobb gets no story-derived name, on purpose.**

He is the pump mechanic. He is not in the book's argument. He has no arc, no secret, no
lineage; he is competent, decent, unconnected, and by the end he is the only person in
the village who tells the truth without it costing him anything — which is exactly why he
is not the protagonist.

Given the logic in §2 he could have been **Wilkin Swith** (the second saint of the fen
flood calendar), or **Alba Garrow** (the almanac's word for a clear night). Both would
have been defensible. Both would have been wrong: a name that means something *makes a
promise the character will not keep*, and Joe is the character who is not carrying the
book.

So his name is left plain. `Cobb` is a fen surname — *cob* is the clay the fen is cut
from, and Cobb is a real occupational name from fen drainage — but nothing is *derived*
from it. He is the plain name in a book of loaded ones, which is the only way a reader
can tell he is not part of the myth.

`USER_PREFERENCES.md` §1 limit: *"A character sometimes needs a plain name. A name that is
over-loaded with significance can be as conspicuous as a random one."* Applied here. If
the preference had been enforced, Joe would have been given a charm-name and the reader
would have been told, wrongly, that he mattered.

## 5. Status

Naming phase only, to test the preference. Not a real book, no manuscript, no
architecture. The cast above is the deliverable; the rest of the pipeline is not run,
because running it would answer a different question.
