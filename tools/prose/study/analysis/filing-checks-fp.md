# How often the two filing checks fire on unrelated human novels

Corpus: **109** books, 9,288,425 words (21,680–316,142 per book), one work per author — every pair is unrelated by construction, so every flag here is a false positive.
Gates measured exactly as shipped in `run/dispatch.py`, imported not copied: an opening either equal after normalisation or at least 0.85 token overlap with openers of >= 5 words; a passage of `24` words carrying >= 3 content words. All 5,886 pairs compared, no sampling.

| gate | pairs flagged | books flagged | per-pair rate |
|---|---|---|---|
| opening sentence, as filed | 0 of 5,886 | 0 of 109 | 0.000% |
| opening sentence, from the first chapter heading (prose opener) | 0 of 5,886 | 0 of 109 | 0.000% |
| shared 24-word passage | 1 of 5,886 | 2 of 109 | 0.017% |

## How the passage length was chosen

The same pass at each candidate length. A gate has to be quiet on unrelated books; a leaked context hands over paragraphs, so length costs almost no sensitivity.

| run length | pairs flagged | books flagged | as a share of pairs |
|---|---|---|---|
| 8 words | 435 of 5,886 | 102 of 109 | 7.390% |
| 12 words | 9 of 5,886 | 13 of 109 | 0.153% |
| 16 words | 5 of 5,886 | 7 of 109 | 0.085% |
| 20 words | 4 of 5,886 | 6 of 109 | 0.068% |
| 24 words **shipped** | 1 of 5,886 | 2 of 109 | 0.017% |
| 32 words | 1 of 5,886 | 2 of 109 | 0.017% |

## What that means at this study's arm sizes

A filing is refused if it collides with **any** book already filed, so the exposure is the pair count, not the pair rate.

| arm | pairs | expected false refusals (openings) | expected (passages) |
|---|---|---|---|
| primary Arm A or B (20 books) | 190 | 0.000 | 0.032 |
| voice arm (6) | 15 | 0.000 | 0.003 |
| full run (52 books) | 1,326 | 0.000 | 0.225 |

Boilerplate diagnostic: no gram appears in 10+ books, so the corpus carries no shared header text and the passage numbers are about prose.

## Passage collisions

### `C-dist-008` Eliot — *Middlemarch* / `C-dist-027` Bunyan — *The Pilgrim's Progress from this world to that which is to come
Delivered under the similitude of a dream, by John Bunyan* — 88 shared grams

- `to a very miry slough that was in the midst of the plain and they being heedless did both fall suddenly into the bog the name of the slough was despond`
- `mr no good mr malice mr love lust mr live loose mr heady mr high mind mr enmity mr liar mr cruelty mr hate light`
- `mr implacable who every one gave in his private verdict against him among themselves and afterwards unanimously concluded to bring him in guilty before the judge and first among themselves mr`
- `the foreman said i see clearly that this man is a heretic then said mr no good away with such a fellow from the earth ay said mr malice for i hate the very`

## Limits of this measurement

- Human novels are the honest control for *false* positives but not for the true positive rate: a leak produces many long shared passages, and nothing here says how many. The gate only has to be quiet on unrelated books and loud on a copy.
- C-dist is 19th- and early-20th-century public-domain prose: more formulaic, more shared idiom, longer chapters than a 2026 generated novel. If anything that overstates the false-positive rate, which is the safe direction for a gate.
- One work per author means a pair is never two books by one hand. An author repeating themselves is not a leak and is not measured here.
