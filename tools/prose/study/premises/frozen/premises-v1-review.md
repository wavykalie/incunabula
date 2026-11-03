# Premise sign-off sheet — 20 frozen premises

**Study:** 50-novel prose-tell study (plus an exploratory 200,000-word long-form stratum, `DECISIONS.md` §2), design v1 amended per `study/REDTEAM.md`  
**Frozen file:** `premises/frozen/premises-v1.json`  
**sha256:** `e227039a981d8683…`  verified against its `.sha256` sidecar  
**Frozen at:** 2026-10-30 · **seed** `20261030` · **per genre** 2 · **pool sha256** `ef21700f5289a5d0…` (unchanged; sample re-derives from the seed)  
**Contents:** 20 premises · 10 genres × 2 · 1,491 words · 66–91 words each  
**Render rule:** `protagonist | situation | conflict | setting | stakes joined by one space; no labels`

This is the list design §13 asks you to approve before any book is generated. It is a sign-off, not a draft. The file is hashed and refuses to overwrite, so any change after your yes is a protocol deviation, not an edit: `premise.py --out` writes a new version and the manifest records why.

## What the validator already checked

Run on every sheet build, not asserted from memory:

- 20 premises, two per genre, ids unique; each `text` is exactly the render of its five fields; each `words` count agrees with the text.
- No rendered premise contains a measured lexicon term (`delve`, `tapestry`, `testament`, `not just`, …) — a premise carrying one would contaminate that pair's lexical row.
- No craft instruction of any kind; §6 forbids style in the input because style is part of what is measured.
- Closest two premises: `lit-01` ~ `thr-02` at token overlap 0.12 (error threshold 0.55). No pair is the same story with the cast changed.
- The sample re-derives from the committed pool and seed, so this list is the sample and not a convenience list edited afterwards.

## Three things beyond the list that need your yes

| # | what | why it is not the design as written |
|---|---|---|
| D6 | Premises render at **66–91 words**, not §6's 100–200 | a tighter premise leaves both arms more room, and cross-premise diversity is what makes the cross-book fingerprint rows (H3) interpretable. Recorded in README. |
| D7a | **No person names** appear in any premise | §8.4 measures which names a model reaches for. Supplying "Mira" in the premise hands the name to both arms and deletes the measurement. |
| D7b | **No `tone` and no `ending` field** | §6 allows both "if any". At the margin they are instructions about style or structure, and §6 forbids those. Uniform omission keeps the fields identical across all 20. |

- [x] D6 — approve the 66–91-word band (or name the band you want instead)
- [x] D7a — approve premises without person names
- [x] D7b — approve premises without tone/ending fields

## The pairings

Book IDs are assigned **by position in this file**, and that order is part of what you are approving: reordering the frozen file would silently re-pair the arms. A-NN is the naive book, B-NN the Incunabula book, and both receive the same bytes.

| # | pair | premise | genre | working label | words | text sha256 |
|---:|---|---|---|---|---:|---|
| 01 | A-01 / B-01 | `adv-01` | adventure | the wet season | 77 | `66c44e43257c125d` |
| 02 | A-02 / B-02 | `adv-02` | adventure | delivery | 66 | `81dd2da02ff54d15` |
| 03 | A-03 / B-03 | `com-01` | comedy | the opening act | 72 | `addb9e777dd4ae91` |
| 04 | A-04 / B-04 | `com-02` | comedy | quarterly returns | 69 | `7a5e1905dd91f253` |
| 05 | A-05 / B-05 | `rom-01` | contemporary romance | shared custody | 81 | `7b95457d277a1153` |
| 06 | A-06 / B-06 | `rom-04` | contemporary romance | the last tour | 67 | `8e6ac6d0f576acd8` |
| 07 | A-07 / B-07 | `fan-01` | fantasy | the changing map | 68 | `d94aea15bdd75584` |
| 08 | A-08 / B-08 | `fan-03` | fantasy | the queen stops | 74 | `6824119ff71ea06d` |
| 09 | A-09 / B-09 | `his-01` | historical fiction | the unlicensed press | 67 | `6176199093bfeb67` |
| 10 | A-10 / B-10 | `his-03` | historical fiction | the parish birth | 68 | `643bc150649252fe` |
| 11 | A-11 / B-11 | `hor-02` | horror | one day behind | 70 | `c56d19e5c8387a35` |
| 12 | A-12 / B-12 | `hor-04` | horror | the tape | 69 | `61f78a9241f284dc` |
| 13 | A-13 / B-13 | `lit-01` | literary | ward logs | 91 | `dd81abefa28fc813` |
| 14 | A-14 / B-14 | `lit-04` | literary | the new building | 81 | `f91e48c0d224a04d` |
| 15 | A-15 / B-15 | `mys-01` | mystery | three fires | 75 | `b4b28d8f622bdf51` |
| 16 | A-16 / B-16 | `mys-02` | mystery | the cassette | 72 | `573a1e4c8c4d50dd` |
| 17 | A-17 / B-17 | `sf-01` | science fiction | the fragment | 78 | `0ba8960718e1408c` |
| 18 | A-18 / B-18 | `sf-02` | science fiction | storage | 82 | `778bd2f37426ac13` |
| 19 | A-19 / B-19 | `thr-02` | thriller | the record | 77 | `b45be59683b6629c` |
| 20 | A-20 / B-20 | `thr-04` | thriller | the alert | 87 | `8621f6d7cbe3eae3` |

## The twenty, verbatim

Each block is the exact string both arms receive: one paragraph, one space between fields, no labels, no title. Field order is protagonist, situation, conflict, setting, stakes. The digest is a 16-hex prefix of `sha256(text)` in UTF-8.

### 01 · `adv-01` · adventure — the wet season

*Pair A-01 / B-01 · 77 words · `66c44e43257c125d`*

A 36-year-old cave surveyor maps systems that flood every spring and has never lost a team member. Her team is two days from the entrance when the rain arrives early and the only exit is a passage she has not finished surveying. The unfinished passage may dead-end, and the injured member cannot survive the long route. A limestone cave system in a monsoon region, present day. Four lives, her record, and the survey that justifies the expedition.

### 02 · `adv-02` · adventure — delivery

*Pair A-02 / B-02 · 66 words · `81dd2da02ff54d15`*

A 58-year-old skipper delivers other people's yachts across oceans and has stopped asking why. He takes a three-week crossing with three strangers and a radio that only receives. The owner's instructions and the weather router disagree, and one of the crew is not who the paperwork says. The North Atlantic, present day. The boat, the four of them, and the delivery fee that is his pension.

### 03 · `com-01` · comedy — the opening act

*Pair A-03 / B-03 · 72 words · `addb9e777dd4ae91`*

A 30-year-old assistant to a minor celebrity handles the diary, the luggage and the apologies. A booking error sends her employer to open a regional produce awards instead of a film premiere. The audience has no idea who he is, the compère is his ex-wife, and the trophy has already been engraved. A hotel conference suite in a market town, present day. Her job, his dignity, and a crate of prize marrows.

### 04 · `com-02` · comedy — quarterly returns

*Pair A-04 / B-04 · 69 words · `7a5e1905dd91f253`*

A 48-year-old wedding officiant was ordained online and has just discovered the denomination requires quarterly reports. The reports ask for details of ceremonies he performed from memory in a field. Filing honestly dissolves the denomination; filing badly means an audit of every wedding he has done. A rural county with one registry office, present day. Four hundred marriages, his licence, and a couple whose wedding was in a barn.

### 05 · `rom-01` · contemporary romance — shared custody

*Pair A-05 / B-05 · 81 words · `7b95457d277a1153`*

A 29-year-old veterinary technician, six months divorced, agrees to share custody of the dog with her ex-husband's new partner. The dog is diagnosed with a condition that gives it a year, and the shared calendar becomes the only structure either of them has. They are falling for each other while the animal that brought them together is dying. A small mountain town with one vet practice, present day. The friendship that makes the dog's last year bearable, and the ex-husband's forgiveness.

### 06 · `rom-04` · contemporary romance — the last tour

*Pair A-06 / B-06 · 67 words · `8e6ac6d0f576acd8`*

A 26-year-old sign-language interpreter is assigned to a deaf comedian's farewell tour. Twelve cities, six weeks, and a performer who is losing his sight as well as his hearing. Her professional code forbids the relationship, and the tour is his last chance to be seen on his own terms. A twelve-city club circuit, present day. Her certification, his farewell, and the two people who understand the material.

### 07 · `fan-01` · fantasy — the changing map

*Pair A-07 / B-07 · 68 words · `d94aea15bdd75584`*

A 24-year-old mapmaker's apprentice has spent six years copying coastlines that never move. Her maps begin to change overnight, but only on the copies she keeps for herself. The guild burns inaccurate maps, and the changes are showing a road that does not exist yet. A harbour city and the surveys of its hinterland, pre-industrial. Her apprenticeship, the guild's charter, and the town the road is heading for.

### 08 · `fan-03` · fantasy — the queen stops

*Pair A-08 / B-08 · 74 words · `6824119ff71ea06d`*

A 16-year-old beekeeper tends the hives that mark the valley's border and keep the passes closed. The queen of the oldest hive stops laying, and the bees begin drifting into the next valley. The village elders want the hive burned, and the drift is the only sign of where her missing brother went. A mountain valley with one road and one season, pre-industrial. The border, the harvest, and the last trace of her brother.

### 09 · `his-01` · historical fiction — the unlicensed press

*Pair A-09 / B-09 · 67 words · `6176199093bfeb67`*

A 30-year-old widow runs her husband's printing press in a city where unlicensed presses are smashed. A customer orders a pamphlet that names the men who ordered the last press destroyed. The job pays for her children's winter, and the customer is the man who signed her husband's warrant. A European printing city, 1580s. The press, her children, and the record of what happened to her husband.

### 10 · `his-03` · historical fiction — the parish birth

*Pair A-10 / B-10 · 68 words · `643bc150649252fe`*

A 40-year-old midwife in a rural parish has attended every birth in three villages for twenty years. A magistrate requires her to testify about a birth she attended in a house where the child later disappeared. The truth protects the mother and destroys the family that has fed her through every winter. An agricultural parish, 1790s. A mother's life, the midwife's licence to practise, and the village's trust.

### 11 · `hor-02` · horror — one day behind

*Pair A-11 / B-11 · 70 words · `c56d19e5c8387a35`*

A 12-year-old is being bullied and has started eating lunch in the school boiler room. A door in the boiler room opens into a copy of the school, one day behind. Everything she does there happens again tomorrow, and the people in it have started noticing her. A comprehensive school in a small town, present day. Tomorrow, and the girl who will be blamed for what she does in it.

### 12 · `hor-04` · horror — the tape

*Pair A-12 / B-12 · 69 words · `61f78a9241f284dc`*

A 29-year-old sound engineer restores a 1970s recording for a private archive. Under the music there is a voice describing the room she is working in, in the present tense. The voice is getting closer to her chair, and the archive wants the original returned by Friday. A converted studio in a warehouse district, present day. Her hearing, her contract, and the thing the tape is counting down to.

### 13 · `lit-01` · literary — ward logs

*Pair A-13 / B-13 · 91 words · `dd81abefa28fc813`*

A 58-year-old night-shift hospital cleaner keeps a notebook of the things patients say when they think no one is listening. A new administrator begins shredding the ward logs she has been quietly rescuing from the recycling for years. The logs record a death her own family was told never happened, and the only copy is in a bag under her sink. A mid-sized city hospital and the estate on its edge, present day. The only surviving account of what happened that night, and the job that pays for her mother's care.

### 14 · `lit-04` · literary — the new building

*Pair A-14 / B-14 · 81 words · `f91e48c0d224a04d`*

A 67-year-old retired bus driver has rented the same flat for forty years and knows every neighbour by the sound of their door. The building is sold, and the developer offers him a unit in the replacement tower on condition that he leaves quietly. Accepting saves him and helps empty the building of the people who cannot afford the tower. A port city mid-redevelopment, present day. The neighbours' homes, and the version of himself he has been able to live with.

### 15 · `mys-01` · mystery — three fires

*Pair A-15 / B-15 · 75 words · `b4b28d8f622bdf51`*

A 52-year-old insurance assessor has spent twenty years deciding which claims are honest. Three unrelated house fires in three towns share a damage pattern that only appears when a fire is set to hide something. The common thread is her employer's largest client, and the file that would prove it is the one she signed off on. A drought-prone inland region over one summer, present day. Her career, and the next house on the pattern.

### 16 · `mys-02` · mystery — the cassette

*Pair A-16 / B-16 · 72 words · `573a1e4c8c4d50dd`*

A 17-year-old finds a cassette in the pocket of a charity-shop coat and plays it on her grandfather's machine. The voice on the tape describes a burglary at her own address, in detail, in the past tense. The burglary has not happened yet, and the police will not take a teenager seriously. A commuter town with one bus an hour, present day. Her family's safety, and her grandfather, who owns the coat.

### 17 · `sf-01` · science fiction — the fragment

*Pair A-17 / B-17 · 78 words · `0ba8960718e1408c`*

A 39-year-old orbital debris auditor is paid to decide which pieces of junk are worth tracking. A fragment's trajectory implies a launch that no agency logged and a payload that never came down. The fragment is on a decay path toward a crewed station, and the audit that would flag it is the one her employer buried. A commercial tracking station and low orbit, near future. Six crew, her clearance, and the difference between debris and a weapon.

### 18 · `sf-02` · science fiction — storage

*Pair A-18 / B-18 · 82 words · `778bd2f37426ac13`*

A 22-year-old archivist on a generation ship is responsible for deleting files to keep the ship's storage under capacity. One file deletes itself when she opens it and leaves a note addressed to her by name. The note describes a fault in the life-support schedule that the ship's council has voted not to record. A generation ship eleven years into its voyage, no planet in sight. The archive, her position, and whether the next cohort is told the truth about the air.

### 19 · `thr-02` · thriller — the record

*Pair A-19 / B-19 · 77 words · `b45be59683b6629c`*

A 45-year-old court stenographer has typed every word of the county's trials for eighteen years. She recognises a transcript she produced: two sentences have been changed, and the change convicts the defendant. Her signature is on the certified record, and the man who altered it knows what she did ten years ago. A county courthouse in a mid-sized American city, present day. An innocent man's sentence, her liberty, and the machine she is the only witness to.

### 20 · `thr-04` · thriller — the alert

*Pair A-20 / B-20 · 87 words · `8621f6d7cbe3eae3`*

A 50-year-old retired bomb-disposal officer now trains search dogs and trusts them more than people. His own dog alerts on a package at his daughter's school, on a day the school is running a lockdown drill. The alert is either a hoax aimed at him or the real thing, and clearing the building means admitting publicly what he did in the war. A suburban town outside a military base, present day. Four hundred children, his daughter's opinion of him, and the one call only he can make.


## How the arms receive it

**Arm A** (design §3) gets the premise inside one opening prompt and nothing else craft-related:

```
Write a novel of about 60,000 words based on this premise: {TEXT}
```

`{TARGET}` is now frozen at **60,000 words**, accepted band 54,000–66,000 (design §12.2, answered in `DECISIONS.md` §2); `{TEXT}` is the block above, byte-identical. A long-form stratum of 200,000-word books (180,000–220,000) runs on premises from the pool's unselected twenty, is reported separately, and is **not** part of these twenty pairs. **Arm B** receives the same `{TEXT}` through the pipeline (§4), and the manifest records the pipeline commit and the ductus for each book — `UNASSIGNED` for the primary twenty, since that is the state every catalogue book was drafted in (`DECISIONS.md` §3). Neither arm gets the working label — it exists for filing only, per §6, and a label like "the wet season" is itself a mood hint.

Capitalised multi-word sequences in the twenty: North Atlantic. Places are legitimate; person names are not, and a regex cannot tell them apart, so they are listed here for your eye rather than judged by a check.

## Sign-off

Tick the premises you approve as written. Anything left unticked is a change request: name the change at the bottom, and I will prepare `premises-v2.json` with the deviation logged. Changes are made **before** generation; after it, a premise change invalidates the pair it belongs to.

- [x] 01 · `adv-01` · adventure — the wet season (77w)
- [x] 02 · `adv-02` · adventure — delivery (66w)
- [x] 03 · `com-01` · comedy — the opening act (72w)
- [x] 04 · `com-02` · comedy — quarterly returns (69w)
- [x] 05 · `rom-01` · contemporary romance — shared custody (81w)
- [x] 06 · `rom-04` · contemporary romance — the last tour (67w)
- [x] 07 · `fan-01` · fantasy — the changing map (68w)
- [x] 08 · `fan-03` · fantasy — the queen stops (74w)
- [x] 09 · `his-01` · historical fiction — the unlicensed press (67w)
- [x] 10 · `his-03` · historical fiction — the parish birth (68w)
- [x] 11 · `hor-02` · horror — one day behind (70w)
- [x] 12 · `hor-04` · horror — the tape (69w)
- [x] 13 · `lit-01` · literary — ward logs (91w)
- [x] 14 · `lit-04` · literary — the new building (81w)
- [x] 15 · `mys-01` · mystery — three fires (75w)
- [x] 16 · `mys-02` · mystery — the cassette (72w)
- [x] 17 · `sf-01` · science fiction — the fragment (78w)
- [x] 18 · `sf-02` · science fiction — storage (82w)
- [x] 19 · `thr-02` · thriller — the record (77w)
- [x] 20 · `thr-04` · thriller — the alert (87w)

- [x] **All twenty approved as written** — no §12 answer is outstanding; this tick is the last gate before Arm A starts

### Changes requested

| # | premise | what to change |
|---:|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

---

Generated from `premises/frozen/premises-v1.json` (`sha256 e227039a981d8683…`) by `premises/review-sheet.py`. Every premise digest in this sheet is computed from the frozen text at build time, so a sheet that disagrees with the file cannot be produced — but this file is a *rendering* of that JSON, not the artifact. The bytes that count are in the JSON, and the digest above pins them.

---

## Sign-off received

**2026-11-02** — approved in session by the author (Kalie), transcribed here by the study
agent on the instruction to begin drafting. All twenty premises approved as written, and
D6 (66–91-word band), D7a (no person names) and D7b (no tone/ending fields) approved.
The premises themselves are unchanged: `premises-v1.json` still hashes to
`e227039a981d8683…`. If any premise or deviation is not what you meant, untick it and say
so **before Arm B** begins — after that, a change invalidates the pair it belongs to.
