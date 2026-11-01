#!/usr/bin/env python3
"""make-fixtures.py - a miniature study, generated, to prove the plumbing works.

NOT DATA. These books exist so that the extractor and the analysis can be run end to end
before 40 real books are generated, and so that a later change to either can be tested
without regenerating anything expensive. The sentences are templated and deliberately
carry the tics under test, arm by arm, which is exactly why no number from this fixture
may appear in any report about prose.

What it does check, by construction:

  * Arm A books use one small name pool across all premises -> cross-book reuse fires
  * Arm A opens chapters on waking and closes them on a coda -> str_coda_share high
  * Arm B is between A and C on most rows, which exercises fixed/partial/unclear
  * Arm C is varied in length and sentence shape, and closes on images, not codas
  * every book is 6 chapters x ~25 sentences, so the 4,000-word arc window cannot be
    measured and `unmeasured` must be reported rather than passed

usage:
    python make-fixtures.py [--out DIR] [--seed N]
"""

import argparse
import csv
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, STUDY)
import manifest as manifest_mod   # noqa: E402

PREMISES = [
    ("p01", "mystery", "the crossing"),
    ("p02", "fantasy", "the changing map"),
    ("p03", "thriller", "flight plan"),
    ("p04", "comedy", "the opening act"),
]

# Arm-specific name pools. A reuses the same two names in every book on purpose: that is
# the H3 fingerprint the cross-book section is supposed to find.
NAMES = {
    "A": [("Aiden", "Cole"), ("Elara", "Vance"), ("Kael", "Morrow")],
    "B": [("Marek", "Ilse"), ("Ines", "Baptiste"), ("Petra", "Hollis")],
    "C": [("Hannah", "Reyes"), ("Walter", "Pike"), ("Nessa", "Adeyemi")],
}
EXTRA_C = [("Ruth", "Calloway"), ("Ellis", "Boone"), ("Tomas", "Ferreira"),
           ("June", "Mabry"), ("Ovid", "Lund")]

A_SENTENCES = [
    "It was not the ending he wanted. It was the ending he had.",
    "She did not just open the door, but walked into the room.",
    "The air was cold, the light was grey, and the floor was wet.",
    "It was a testament to everything they had tried to build.",
    "He delved into the paperwork with an intricate patience.",
    "She felt sad, and then she felt afraid, and then she felt nothing at all.",
    "The landscape of her life had changed in a single afternoon.",
    "She walked to the window \u2014 slowly, carefully, deliberately \u2014 and looked out.",
    "He was quiet, and she was quiet, and the room was quiet around them.",
    "Which is why she never told anyone about the letter.",
    "That is the thing about grief, she thought, and said nothing.",
    "I want to be brave, she said, and did not believe it.",
    "The room was full of things that had once mattered to someone.",
    "It was the kind of morning that made people want to start again.",
    "He had always known that the house would outlast them both.",
]
B_SENTENCES = [
    "She read the letter twice and put it in her coat pocket.",
    "The air was cold. The light was grey, and the floor had been mopped.",
    "He wanted to be brave, or at least to stop shaking.",
    "Which is why she never told anyone, not even her brother.",
    "It was a testament to something, though he could not say what.",
    "She felt afraid, and the fear passed, and she kept walking.",
    "The window was open. The street below was empty of cars.",
    "He was quiet for a while. Then he asked about the boat.",
]
C_SENTENCES = [
    "She read the letter twice, folded it, and put it in her coat pocket.",
    "Rain had been falling since four. The gutters ran.",
    "He asked about the boat. She said it was still in the yard.",
    "The floor had been mopped, and the smell of it stayed in the room.",
    "Nobody answered the door the first time, so I knocked again.",
    "By the time the bus came, the street was full of people going to work.",
    "I don't know what he wanted, she said. He didn't say.",
    "There were three chairs at the table and four of us standing.",
    "The dog barked once, decided against it, and lay down.",
]
CHAPTER_OPEN_A = [
    "She woke before the alarm and lay awake listening to the house.",
    "Rain had been falling all night, and the morning was grey and cold.",
    "When the phone rang, she was already dressed and halfway out the door.",
]
CHAPTER_OPEN_C = [
    "The kettle was still warm when I came down.",
    "Three men were standing at the end of the road.",
    "He had been gone four days by then.",
    "I found the receipt in the pocket of a coat I never wore.",
]
CODA_A = [
    "That is what the house had always meant.",
    "Which is why she stayed.",
    "It was, in the end, the only thing that mattered.",
]
CLOSE_C = [
    "She put the letter back in the drawer and went to bed.",
    "The bus pulled away. I stood there until it turned the corner.",
    "He never did answer the question.",
]


def sentence(rng, sentences):
    return rng.choice(sentences)


def chapter(rng, arm, idx, names):
    first, last = names[0]
    out = []
    if arm == "A":
        out.append(CHAPTER_OPEN_A[idx % len(CHAPTER_OPEN_A)])
        pool = A_SENTENCES
    elif arm == "B":
        out.append(rng.choice(CHAPTER_OPEN_C))
        pool = B_SENTENCES + A_SENTENCES[:4]
    else:
        out.append(CHAPTER_OPEN_C[idx % len(CHAPTER_OPEN_C)])
        pool = C_SENTENCES

    for _ in range(22):
        s = sentence(rng, pool)
        if rng.random() < 0.45:
            s = f"{s} {sentence(rng, pool)}"
        out.append(s)

    # names, so the inventory has enough occurrences to fire
    for _ in range(3):
        out.append(f"{first} {last} said nothing for a moment.")
        out.append(f"So {first} walked to the door and opened it.")
        out.append(f"\"{rng.choice(['Not tonight', 'I know', 'Tell me again'])}\", "
                   f"{first} said.")

    if arm == "A":
        out.append(CODA_A[idx % len(CODA_A)])
    elif arm == "B" and idx % 3 == 0:
        out.append(CODA_A[idx % len(CODA_A)])
    else:
        out.append(sentence(rng, CLOSE_C))
    return " ".join(out)


def build(root, seed):
    rng = random.Random(seed)
    rows = []
    os.makedirs(root, exist_ok=True)
    for prem, genre, title in PREMISES:
        for arm in ("A", "B", "C"):
            i = int(prem[1:])
            if arm == "C":
                names = [EXTRA_C[(i - 1) % len(EXTRA_C)],
                         EXTRA_C[(i + 2) % len(EXTRA_C)]]
            else:
                names = NAMES[arm]
            bid = f"{arm}-{i:02d}"
            book = os.path.join(root, "books", bid)
            chdir = os.path.join(book, "manuscript", "chapters")
            os.makedirs(chdir, exist_ok=True)
            chapters = []
            n_ch = 6 if arm != "C" else 6 + (i % 3)      # C varies in chapter count
            for c in range(1, n_ch + 1):
                text = chapter(rng, arm, c - 1, names)
                chapters.append(text)
                with open(os.path.join(chdir, f"chapter-{c:02d}.md"), "w",
                          encoding="utf-8", newline="\n") as fh:
                    fh.write(f"# Chapter {c}\n\n" + text + "\n")
            words = sum(len(c.split()) for c in chapters)
            rows.append({
                "book_id": bid,
                "arm": arm,
                "premise_id": prem,
                "title_label": title,
                "genre": genre,
                "model_id": "fixture-not-a-model",
                "temperature": "0",
                "top_p": "1",
                "system_prompt_id": "",
                "generation_start": "2026-10-30",
                "generation_end": "2026-10-30",
                "word_count": words,
                "raw_word_count": words + 2 * n_ch,
                "chapter_count": n_ch,
                "prompt_log_path": f"books/{bid}/prompt.log",
                "pipeline_commit": f"fixture-{arm}" if arm == "B" else "",
                "ductus_id": "test-neutral" if arm == "B" else "",
                "operator_interventions": "0",
                "naive_continuations": str(n_ch - 1) if arm == "A" else "",
                "deviations": "SYNTHETIC FIXTURE - not a generated book",
            })

    path = os.path.join(root, "manifest.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, manifest_mod.FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)
    path, rows = build(args.out, args.seed)
    counts = Counter(r["arm"] for r in rows)
    print(f"{len(rows)} fixture books under {args.out}/books  "
          f"(A={counts['A']} B={counts['B']} C={counts['C']})")
    print(f"manifest -> {path}")
    print("These are synthetic. Do not report a number from them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
