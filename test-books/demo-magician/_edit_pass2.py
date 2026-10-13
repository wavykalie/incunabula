#!/usr/bin/env python3
# demo-magician edit pass 2: genuine ACT III rewrite-UP expansions (EXPANSION_PASS
# targets 25, 30, 34) to finish material each chapter has not finished saying and
# clear the L1 declared floor honestly. CRLF preserved. Validates anchors first.
import io, textwrap, os

CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuscript", "chapters")
WRAP = 95

def wrap(prose):
    paras = [p.strip() for p in prose.strip().split("\n\n")]
    return "\r\n\r\n".join(textwrap.fill(" ".join(p.split()), width=WRAP) for p in paras)

def load(name):
    with io.open(os.path.join(CH, name), encoding="utf-8", newline="") as fh:
        return fh.read()

def save(name, text):
    with io.open(os.path.join(CH, name), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

EDITS = []
def A(name, anchor, prose):
    EDITS.append((name, anchor, prose))

# ch25 — the nine noes are the chapter's discovery; what it has not finished
# saying is what a room full of true answers is actually made of.
A("chapter-25.md", "without once being asked what he *had* done.", """
Not one of the nine was a lie. That was the part she kept turning over in the room over the tobacconist until two in the morning. A man who says no nine times and means it nine times is not a man who is hiding; he is a man who has arranged his whole life so that the true answer to every question a tribunal knows how to ask is the answer that costs him nothing, and the only question that could cost him anything is the one that nobody in that building had been trained to put, and she had built the building, and she had filled it with people who knew how to ask about dates and memberships and property, and not one of them had known how to ask a man where he had been looking.
""")

# ch30 — the recess is the last quiet before the statement; the chapter has not
# finished saying what she does with the twenty minutes and the four pages.
A("chapter-30.md", "Reiner sat on a bench in a corridor for the rest of the recess.", """
She did not open the notebook, because opening it would have shown her the four pages, and the four pages were the whole of what she had, and a woman with four pages who reads them in a corridor in the middle of a hearing is a woman who is going to say them out loud at two o'clock and then stop, and there had to be something after the stopping, and she had not found it, and the recess was twenty minutes long and she spent nineteen of them not being frightened and one of them being frightened in a way she had no practice at at all.
What she had was a shape and a date and a door and a prediction, and the prediction was the only one of the four that could be wrong in a way that would show, and every conjurer in that building would have told her to keep the prediction back and let the shape do the work, because a shape cannot be checked and a prediction can, and she had been taught that herself at nine years old by a man who wrote rooms down, and she was going to ignore it, and the ignoring was the whole of the case.
""")

# ch34 — the stage is the last image; the chapter has not finished saying the
# difference between the trick and the repair.
A("chapter-34.md", "She sat down on the stage.", """
Nine inches is not a height. It is the height a hall gives a person when the hall has been built for a lecturer and not for a woman of thirty-five in a good coat who has just closed a matter and does not want an audience for what she is going to think about it. She had sat on the edges of a great many stages and she had never once gone up onto one, and she was not going to start, and the reason she was not going to start was the same reason she had not opened the notebook in the recess, which was that a woman who goes up onto a stage is making a claim, and the whole of the last twelve months had been an argument with a man about what a claim costs, and she had won it with a register and four guilders, and she was not going to spend it on a stage.
""")

# validate
texts = {}
problems = []
for name, anchor, _ in EDITS:
    texts.setdefault(name, load(name))
    if texts[name].count(anchor) != 1:
        problems.append((name, anchor[:50], texts[name].count(anchor)))
if problems:
    for p in problems:
        print("ANCHOR PROBLEM:", p)
    raise SystemExit(1)

for name, anchor, prose in EDITS:
    t = texts[name].replace(anchor, anchor + "\r\n\r\n" + wrap(prose), 1)
    texts[name] = t
    save(name, t)
print("edits applied:", len(EDITS))
