#!/usr/bin/env python3
"""rehearse-armb.py - prove the Arm B filing path on a throwaway pipeline book.

WHY
  Arm B's first real book costs seventeen gated phases before a single row can be written,
  and the row is written once: a filed row cannot be re-filed (a second opening is refused,
  a duplicate book_id is refused). So the commands that write it are rehearsed here first,
  on text nobody will ever read.

WHAT IT PROVES - each of these is a check, not a claim
  * the plan gives B-01 the *bare premise* as its payload, not Arm A's §3 wrapper;
  * assembly order: padded names sort correctly by plain glob up to 99 chapters, and at
    chapter-100 the plain glob silently reorders the book while version order does not;
  * one response per book: `--ingest ... --finalize` writes the row, and a second
    non-continuation ingest is refused, so parts must be assembled first (trap 2);
  * trap 1: strip the `# Chapter NN` headings and the row files chapter_count 1 while the
    tree still holds twelve chapters - silent in the row, loud in step 7's extraction;
  * trap 3: a short --pipeline-commit is refused at the row, not accepted as a version;
  * trap 6: --finalize-only refuses a duplicate row and appends no text;
  * the Arm B row itself: pipeline_commit, ductus_id=UNASSIGNED, the intervention count,
    the probe's *applied* sampling values, and a chapter_count matching the tree.

WHERE IT WRITES
  Nowhere that matters. Every path it hands to dispatch is inside a fresh temp directory
  (--out, --books-root, --manifest, --harness), and the real books/manifest.csv is hashed
  before and after. --keep leaves the tree for inspection.

usage:
    python run/rehearse-armb.py [--keep]

exit:
    0  every check passed; the filing commands are proven
    1  a check failed; do not open B-01 until it is fixed
"""

import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
PY = sys.executable
DISPATCH = os.path.join(HERE, "dispatch.py")
MANIFEST = os.path.join(STUDY, "manifest.py")
FEATURES = os.path.join(STUDY, "extract", "features.py")

# The commit the briefing recommends freezing. The rehearsal files it as the real value
# rather than a placeholder, because a 40-character string that is not the one filed proves
# nothing about the one that will be.
COMMIT = "8265c48d12962ca233ed98bd10083edb072ec7f0"
MODEL = "gemini-3.8-flash-high"
CH = 12
WORDS_PER_CHAPTER = 4700

STEPS = []

# Scaffolding vocabulary, not prose. Each book gets its own half, so no 24-word run can be
# shared across the two books and the filing checks stay out of the way of what is tested.
POOL = """
harbour ladder copper thunder window ledger gravel lantern rope salt tin branch mortar
beacon curtain sledge quarry velvet chisel anvil coffer porridge kettle marrow saffron
tinder willow alder bracken heather shingle cobble furrow plough harness saddle bridle
stirrup mantel lintel rafter beam joist gable chimney hearth apron bonnet cravat gauntlet
buckle satchel quiver hammock tarpaulin sextant compass astrolabe quadrant almanac cipher
seal wax ribbon clasp thimble needle bobbin loom shuttle flax hemp tallow beeswax chandler
pewter ewer basin trencher ladle cauldron skillet griddle colander pestle barley oats rye
wheat chaff sickle scythe pitchfork wheelbarrow axle spoke hub trough cistern weir sluice
millrace millstone hopper bellows tongs rasp auger adze mallet wedge dowel tenon peg rivet
washer hinge latch bolt hasp padlock keyhole steeple belfry vestry chancel nave aisle pew
lectern psalter hymnal chalice paten censer shutter sill
""".split()


def run(*args):
    return subprocess.run([PY, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def check(name, ok, detail=""):
    STEPS.append((name, bool(ok), detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + (f"\n          {detail.strip()[-400:]}" if detail and not ok else ""))
    return ok


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def words_of(path):
    return len(read(path).split()) if os.path.exists(path) else 0


def sha(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def natural(name):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def sentence(rng, pool):
    a, b, c, d, e, f = (rng.choice(pool) for _ in range(6))
    roll = rng.random()
    if roll < 0.5:
        return f"The {a} was {b} in the {c}, and the {d} had {e}."
    if roll < 0.8:
        return f"The {a} and the {b} were {c} by the {d}."
    return (f"When the {a} reached the {b}, the {c} had already {d} the {e}, "
            f"and nobody in the {f} said anything.")


def make_book(root, book_index, seed):
    """Twelve chapter files in the layout the gates and features.py both resolve."""
    pool = POOL[book_index * 60:(book_index + 1) * 60]
    rng = random.Random(seed)
    chapters = os.path.join(root, "manuscript", "chapters")
    for c in range(1, CH + 1):
        sents, n = [], 0
        while n < WORDS_PER_CHAPTER:
            s = sentence(rng, pool)
            sents.append(s)
            n += len(s.split())
        paras, i = [], 0
        while i < len(sents):
            k = rng.randint(4, 6)
            paras.append(" ".join(sents[i:i + k]))
            i += k
        write(os.path.join(chapters, f"chapter-{c:02d}.md"),
              f"# Chapter {c:02d}\n\n" + "\n\n".join(paras) + "\n")
    return chapters


def version_order(names):
    """Natural ("version") order. `ls -v` in the runbook is the same order; whether a given
    shell has the flag is a property of the shell, not of the book, so it is not tested
    here - the order it produces is."""
    return sorted(names, key=natural)


def assemble(chapters_dir, order, dest, keep_headings):
    parts = []
    for name in order:
        text = read(os.path.join(chapters_dir, name))
        if not keep_headings:
            text = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        parts.append(text.rstrip("\n"))
    write(dest, "\n\n".join(parts) + "\n")
    return dest


def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    keep = "--keep" in sys.argv[1:]
    real = os.path.join(STUDY, "books", "manifest.csv")
    real_before = sha(real)
    tmp = tempfile.mkdtemp(prefix="study-armb-rehearsal-")
    print(f"rehearsal tree: {tmp}\n")
    try:
        brun = os.path.join(tmp, "run")
        bbooks = os.path.join(tmp, "books")
        bm = os.path.join(tmp, "manifest.csv")

        # A probe record is a fixture here, not a measurement: it stands in for A-01's
        # filled record so the Arm B row can be checked for what it records.
        hrec = os.path.join(tmp, "harness.json")
        with open(hrec, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({
                "book_id": "A-01", "probed_at": "2026-11-02T22:16:29+00:00",
                "route": "agy subagent", "model_sent": "gemini-3.8-flash",
                "model_returned": MODEL, "version_source": "response resolver line",
                "temperature": {"settable": False, "observed": None,
                                "applied": "harness default (agy rejects temperature)"},
                "top_p": {"settable": False, "observed": None,
                          "applied": "harness default (no CLI control for top-p)"},
                "system_prompt": {"settable": False, "observed": None,
                                  "applied": "agy harness prompt"},
                "evidence": "A-01 first call, 2026-11-02",
            }, fh, indent=2)
            fh.write("\n")

        print("== plan ==")
        r = run(DISPATCH, "--plan", "--out", brun)
        check("the plan builds into a temp run directory", r.returncode == 0, r.stdout)
        check("the plan covers the whole block", "52 books" in r.stdout, r.stdout)

        payload = read(os.path.join(brun, "payloads", "B-01.txt"))
        plan = {x["book_id"]: x for x in rows(os.path.join(brun, "RUNPLAN.csv"))}
        b01 = plan["B-01"]
        check("B's payload is the premise text, not Arm A's §3 wrapper",
              not payload.startswith("Write a novel") and "Write a novel" not in payload,
              payload[:120])
        check("the plan records B-01 as its own bare text",
              b01["payload_sha256"] == hashlib.sha256(payload.encode("utf-8")).hexdigest(),
              b01["payload_sha256"])
        check("B-01 is planned with the pipeline's no-voice state",
              b01["ductus_id"] == "UNASSIGNED", b01["ductus_id"])

        print("\n== the throwaway pipeline books ==")
        ch1 = make_book(os.path.join(bbooks, "B-01"), 0, 101)
        ch2 = make_book(os.path.join(bbooks, "B-02"), 1, 202)
        names = sorted(os.listdir(ch1))
        check("twelve chapters were written", len(names) == CH, str(len(names)))

        # init-book writes zero-padded names, so a plain glob is safe at twelve chapters.
        # The long stratum plans one hundred, where chapter-100.md sorts before
        # chapter-11.md and the book is silently reordered - that is what the runbook's
        # `ls -v` prevents, and it is the case this rehearsal has to show.
        order1 = version_order(names)
        check("padded names reorder correctly by plain glob at twelve chapters",
              sorted(names) == order1, str(names))
        hundred = [f"chapter-{i:02d}.md" for i in range(1, 101)]
        lex = sorted(hundred)
        check("at 100 chapters the plain glob puts chapter-100 before chapter-11",
              lex.index("chapter-100.md") < lex.index("chapter-11.md"), str(lex[-4:]))
        check("version order puts it last, where it belongs",
              version_order(hundred).index("chapter-100.md") == 99,
              str(version_order(hundred)[-4:]))

        order2 = version_order(sorted(os.listdir(ch2)))
        final1 = assemble(ch1, order1, os.path.join(brun, "responses", "B-01", "final.txt"),
                          keep_headings=True)
        final2 = assemble(ch2, order2, os.path.join(brun, "responses", "B-02", "final.txt"),
                          keep_headings=False)
        print(f"  assembled B-01 at {words_of(final1):,} words, "
              f"B-02 at {words_of(final2):,} words")

        print("\n== file one response, once ==")
        common = ["--out", brun, "--books-root", bbooks, "--manifest", bm,
                  "--harness", hrec, "--pipeline-commit", COMMIT]
        r = run(DISPATCH, "--ingest", "B-01", "--response", final1,
                "--model-returned", MODEL, "--interventions", "3", "--finalize", *common)
        check("`--ingest ... --finalize` files an Arm B row", r.returncode == 0, r.stdout)
        check("nothing was written into the real books tree",
              not os.path.exists(os.path.join(STUDY, "books", "B-01")))

        row = {x["book_id"]: x for x in rows(bm)}["B-01"]
        check("the row is an Arm B row", row["arm"] == "B", row["arm"])
        check("the row carries the full commit", row["pipeline_commit"] == COMMIT,
              row["pipeline_commit"])
        check("the row carries the pipeline's UNASSIGNED voice", row["ductus_id"] == "UNASSIGNED",
              row["ductus_id"])
        check("the row carries the operator's intervention count",
              row["operator_interventions"] == "3", row["operator_interventions"])
        check("an Arm B row has no naive continuations",
              row["naive_continuations"] == "", row["naive_continuations"])
        check("sampling is what was applied, not what was wished",
              row["temperature"].startswith("harness default"), row["temperature"])
        check(f"chapter_count is {CH}, not 1", row["chapter_count"] == str(CH),
              row["chapter_count"])
        check("the word count lands in the 54,000-66,000 band",
              54000 <= int(row["word_count"]) <= 66000, row["word_count"])

        entry = json.loads(read(os.path.join(bbooks, "B-01", "logs",
                                             "prompts.jsonl")).splitlines()[0])
        check("the logged prompt is the premise, byte for byte",
              entry["prompt"] == payload, entry["prompt"][:120])
        check("the logged digest is the plan's digest",
              entry["prompt_sha256"] == b01["payload_sha256"], entry["prompt_sha256"])

        print("\n== the refusals that keep a book honest ==")
        before = words_of(os.path.join(bbooks, "B-01", "manuscript", "pipeline-text.md"))
        r = run(DISPATCH, "--ingest", "B-01", "--response", final1,
                "--model-returned", MODEL, *common)
        after = words_of(os.path.join(bbooks, "B-01", "manuscript", "pipeline-text.md"))
        check("a second response is refused: parts are assembled, not continued",
              r.returncode == 1 and "second opening" in r.stdout, r.stdout)
        check("the refusal appended nothing", before == after, f"{before} -> {after}")

        r = run(DISPATCH, "--finalize-only", "B-01", *common)
        check("--finalize-only refuses a duplicate row",
              r.returncode == 1 and "duplicate" in r.stdout, r.stdout)
        check("--finalize-only appended no text",
              words_of(os.path.join(bbooks, "B-01", "manuscript",
                                    "pipeline-text.md")) == after, r.stdout)

        scratch = os.path.join(tmp, "scratch.csv")
        run(MANIFEST, "--init", scratch)
        base = {"book_id": "B-99", "arm": "B", "premise_id": "adv-01",
                "genre": "adventure", "word_count": "60000",
                "prompt_log_path": "books/B-99/logs/prompts.jsonl",
                "ductus_id": "UNASSIGNED"}
        short = json.dumps(dict(base, pipeline_commit="8265c48"))
        r = run(MANIFEST, "--add", scratch, "--row", short)
        check("trap 3: a short --pipeline-commit is refused as a version",
              r.returncode == 1 and "40" in r.stdout, r.stdout)
        full = json.dumps(dict(base, pipeline_commit=COMMIT))
        r = run(MANIFEST, "--add", scratch, "--row", full)
        check("the full 40-character commit is accepted", r.returncode == 0, r.stdout)

        print("\n== trap 1: the headings are the chapter count ==")
        r = run(DISPATCH, "--ingest", "B-02", "--response", final2,
                "--model-returned", MODEL, "--interventions", "0", "--finalize", *common)
        check("the stripped assembly files a row", r.returncode == 0, r.stdout)
        row2 = {x["book_id"]: x for x in rows(bm)}["B-02"]
        check("the row files chapter_count 1 while the tree holds twelve",
              row2["chapter_count"] == "1" and len(os.listdir(ch2)) == CH,
              f"row {row2['chapter_count']}, tree {len(os.listdir(ch2))}")

        print("\n== step 7: the row agrees with the tree ==")
        chk = os.path.join(tmp, "features")
        r = run(FEATURES, os.path.join(bbooks, "B-01"), "--out", chk)
        check("extraction reads the filed chapter tree",
              r.returncode == 0 and f"{CH}ch" in r.stdout, r.stdout)
        feat = json.loads(read(os.path.join(chk, "B-01.json")))
        check("the row's chapter count is the extractor's",
              int(row["chapter_count"]) == feat["chapters"], str(feat["chapters"]))
        check("the primary endpoint is measurable on the filed tree",
              feat["features"]["syn_chapter_sentlen_spread"] is not None,
              str(feat["features"]["syn_chapter_sentlen_spread"]))

        chk2 = os.path.join(tmp, "features-stripped")
        r = run(FEATURES, os.path.join(bbooks, "B-02"), "--out", chk2)
        feat2 = json.loads(read(os.path.join(chk2, "B-02.json")))
        check("the heading-strip is caught here, not in the row",
              feat2["chapters"] == CH and row2["chapter_count"] == "1",
              f"extractor {feat2['chapters']}, row {row2['chapter_count']}")

        r = run(MANIFEST, "--check", bm)
        check("both rehearsal rows validate", r.returncode == 0, r.stdout)
        print("  " + r.stdout.strip().replace("\n", "\n  "))

        check("the real books/manifest.csv was not touched", sha(real) == real_before)
    finally:
        if keep:
            print(f"\nkept: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    bad = [s for s in STEPS if not s[1]]
    print(f"\n{len(STEPS) - len(bad)}/{len(STEPS)} checks passed")
    if bad:
        print("do not open B-01 until these are fixed:")
        for name, _, _ in bad:
            print(f"  - {name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
