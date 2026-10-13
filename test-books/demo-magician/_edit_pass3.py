#!/usr/bin/env python3
import io, textwrap, os
CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuscript", "chapters")
WRAP = 95
def wrap(prose):
    return "\r\n\r\n".join(textwrap.fill(" ".join(p.split()), width=WRAP) for p in prose.strip().split("\n\n"))
def load(n):
    with io.open(os.path.join(CH, n), encoding="utf-8", newline="") as fh: return fh.read()
def save(n, t):
    with io.open(os.path.join(CH, n), "w", encoding="utf-8", newline="") as fh: fh.write(t)

name = "chapter-34.md"
anchor = "She took them out and put them back."
prose = """
That was the whole of the dossier of a woman who had kept notes for eleven months and then stopped, and it was four pages long and it was not a case and it was never going to be a case, and she had kept it anyway, because a thing you have written down is a thing you can hand to somebody on a bad afternoon, and she had not had a bad afternoon yet, and the four pages were in the bag in case she did, and she did not think they would be needed, and she was right, and being right about that is the loneliest thing in the whole account.
"""
t = load(name)
assert t.count(anchor) == 1, t.count(anchor)
t = t.replace(anchor, anchor + "\r\n\r\n" + wrap(prose), 1)
save(name, t)
print("applied")
