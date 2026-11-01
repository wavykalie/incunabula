#!/usr/bin/env python3
"""selftest.py - run the whole harness on fixtures and assert known-true properties.

The fixtures are built so that a handful of answers are known by construction (Arm A
closes every chapter on a coda; Arm A reuses one first name across all four books). If a
change to the extractor or the analysis breaks either, this fails. The arc rows are
checked to be UNMEASURED rather than passing, because the fixtures are ~2,700 words and
the arc floor is a mean over windows; a harness that reported a pass there would be
claiming a measurement it never made.

usage:  python selftest.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
STEPS = []


def run(*args, **kw):
    return subprocess.run([PY, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def check(name, ok, detail=""):
    STEPS.append((name, bool(ok), detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    return ok


def main():
    tmp = tempfile.mkdtemp(prefix="study-selftest-")
    try:
        print("== premises ==")
        r = run(os.path.join(HERE, "premises", "premise.py"))
        check("pool validates", r.returncode == 0, r.stdout[-400:])

        frozen = os.path.join(tmp, "premises.json")
        r = run(os.path.join(HERE, "premises", "premise.py"), "--sample",
                "--seed", "20261030", "--out", frozen)
        check("freeze succeeds", r.returncode == 0, r.stdout[-400:])
        r = run(os.path.join(HERE, "premises", "premise.py"), "--verify", "--out", frozen)
        check("hash verifies", r.returncode == 0, r.stdout[-200:])
        r = run(os.path.join(HERE, "premises", "premise.py"), "--sample",
                "--seed", "20261030", "--out", frozen)
        check("re-freeze is idempotent", r.returncode == 0 and "unchanged" in r.stdout)
        r = run(os.path.join(HERE, "premises", "premise.py"), "--sample",
                "--seed", "99", "--out", frozen)
        check("different seed refuses to overwrite", r.returncode == 2)

        tampered = os.path.join(tmp, "tampered.json")
        shutil.copy(frozen, tampered)
        shutil.copy(frozen + ".sha256", tampered + ".sha256")
        with open(tampered, "a", encoding="utf-8") as fh:
            fh.write(" ")
        r = run(os.path.join(HERE, "premises", "premise.py"), "--verify", "--out", tampered)
        check("tampering is detected", r.returncode == 1)

        print("== extractor ==")
        r = run(os.path.join(HERE, "extract", "features.py"), "--selfcheck")
        check("extractor constants", r.returncode == 0, r.stdout[-300:])

        fixture_out = os.path.join(tmp, "study")
        r = run(os.path.join(HERE, "fixtures", "make-fixtures.py"), "--out", fixture_out)
        check("fixtures build", r.returncode == 0, r.stdout[-300:])

        feats = os.path.join(fixture_out, "features")
        r = run(os.path.join(HERE, "extract", "features.py"), "--all",
                os.path.join(fixture_out, "books"), "--out", feats)
        check("extraction succeeds", r.returncode == 0, r.stdout[-300:])

        import json
        names = sorted(n[:-5] for n in os.listdir(feats) if n.endswith(".json"))
        check("twelve books extracted", len(names) == 12, str(len(names)))

        recs = {}
        for n in names:
            with open(os.path.join(feats, n + ".json"), encoding="utf-8") as fh:
                recs[n] = json.load(fh)
        check("every book has >= 50 measured features",
              all(sum(1 for v in r["features"].values() if v is not None) >= 50
                  for r in recs.values()))

        arc = recs["A-01"]
        arc_un = [u for u in arc["unmeasured"] if u["feature"] == "str_arc_turns"]
        check("arc reported unmeasured, not passing",
              arc["features"]["str_arc_turns"] is None and arc_un
              and "UNMEASURED" in arc_un[0]["reason"])

        coda = {a: sorted(r["features"]["str_coda_share"] for n, r in recs.items()
                          if n.startswith(a)) for a in "ABC"}
        check("Arm A closes on codas, Arm C does not",
              min(coda["A"]) > max(coda["C"]))

        heads = {n: r["details"]["names"]["firsts"] for n, r in recs.items()}
        a_name = sorted(set.intersection(*[set(heads[n]) for n in heads if n.startswith("A")]))
        check("Arm A reuses a first name across all four books", bool(a_name), str(a_name))

        print("== analysis ==")
        out = os.path.join(fixture_out, "analysis")
        r = run(os.path.join(HERE, "analysis", "analyze.py"),
                "--features", feats,
                "--manifest", os.path.join(fixture_out, "manifest.csv"),
                "--out", out, "--iters", "500")
        check("analysis succeeds", r.returncode == 0, r.stdout[-400:])
        for f in ("report.md", "features.csv", "books.csv"):
            check(f"wrote {f}", os.path.exists(os.path.join(out, f)))

        with open(os.path.join(out, "report.md"), encoding="utf-8") as fh:
            report = fh.read()
        check("report warns about small Arm C", "Arm C is n=" in report)
        check("report names the residual section", "## Residual tells" in report)
        check("report states limits", "## Limits of this run" in report)

        with open(os.path.join(out, "features.csv"), encoding="utf-8") as fh:
            n_rows = len(fh.read().strip().splitlines()) - 1
        check("feature table covers every registered row", n_rows >= 50, str(n_rows))

        r = run(os.path.join(HERE, "analysis", "analyze.py"),
                "--features", os.path.join(tmp, "nothing-here"), "--out", out)
        check("empty input fails instead of writing a clean report", r.returncode == 1)

        print("== voices ==")
        # A synthetic arm with known answers: value x voice-b decides the verdict. Arm C
        # sets the scale, so the effects are in Arm C SDs like the real run.
        import csv as _csv
        vfeat = os.path.join(tmp, "vfeat")
        os.makedirs(vfeat)
        voice_seed = {
            "twin": {"lex_ai_terms_per_1k": 10.0, "str_coda_share": 0.90,
                     "nme_reference_unlisted_share": 0.20},
            "V": {"lex_ai_terms_per_1k": 14.0, "str_coda_share": 0.40,
                  "nme_reference_unlisted_share": 0.50},
            "W": {"lex_ai_terms_per_1k": 13.0, "str_coda_share": 1.60,
                  "nme_reference_unlisted_share": 0.20},
        }
        for i in range(1, 4):
            for kind, vals in voice_seed.items():
                bid = f"B-{i:02d}{kind}" if kind != "twin" else f"B-{i:02d}"
                with open(os.path.join(vfeat, bid + ".json"), "w", encoding="utf-8") as fh:
                    json.dump({"book": bid, "features": dict(vals)}, fh)
        c_vals = [8.0, 9.0, 10.0, 11.0], [.85, .88, .92, .95], [.15, .18, .22, .25]
        for i in range(4):
            bid = f"C-{i + 1:02d}"
            with open(os.path.join(vfeat, bid + ".json"), "w", encoding="utf-8") as fh:
                json.dump({"book": bid, "features": {
                    "lex_ai_terms_per_1k": c_vals[0][i],
                    "str_coda_share": c_vals[1][i],
                    "nme_reference_unlisted_share": c_vals[2][i]}}, fh)

        vout = os.path.join(tmp, "voices")
        r = run(os.path.join(HERE, "analysis", "voices.py"),
                "--features", vfeat, "--out", vout)
        check("voice analysis runs", r.returncode == 0, r.stdout[-400:])
        verdicts = {}
        with open(os.path.join(vout, "voices.csv"), encoding="utf-8") as fh:
            for row in _csv.DictReader(fh):
                verdicts[row["feature"]] = row["verdict"]
        check("same-way movement reads as voice-ness",
              verdicts.get("lex_ai_terms_per_1k") == "voice-ness", str(verdicts))
        check("opposite movement reads as the hand",
              verdicts.get("str_coda_share") == "hand", str(verdicts))
        check("one voice moving reads as one-hand",
              verdicts.get("nme_reference_unlisted_share") == "one-hand", str(verdicts))
        r = run(os.path.join(HERE, "analysis", "voices.py"),
                "--features", os.path.join(tmp, "no-voices"), "--out", vout)
        check("voices without voice books writes nothing", r.returncode == 1)

        print("== filing checks ==")
        r = run(os.path.join(HERE, "analysis", "check-fp.py"), "--selftest")
        check("filing-check calibration machinery", r.returncode == 0, r.stdout[-400:])
        r = run(os.path.join(HERE, "analysis", "check-fp.py"), "--premises",
                "--out", os.path.join(tmp, "premises-fp.md"))
        check("premise-pool calibration runs and probes its own loop",
              r.returncode == 0 and "the loop finds a seeded collision" in r.stdout,
              r.stdout[-400:])

        print("== dispatch ==")
        rundir = os.path.join(tmp, "run")
        books_root = os.path.join(tmp, "runbooks")
        mpath = os.path.join(tmp, "run-manifest.csv")
        dispatch = os.path.join(HERE, "run", "dispatch.py")
        r = run(dispatch, "--plan", "--out", rundir)
        check("plan builds", r.returncode == 0, r.stdout[-400:])
        check("plan covers both strata", "52 books" in r.stdout, r.stdout[-200:])
        r = run(dispatch, "--plan", "--out", rundir)
        check("plan refuses to rewrite itself", r.returncode == 2)

        # PHRASE_N is 24, so a shared passage has to be longer than an 8-word window: this one
        # is ~70 words, which is what a leaked context actually hands over.
        leak = ("The smell of the stairwell was still in her coat when she reached the street, "
                "and the rain had stopped an hour before she finally turned the key in the "
                "lock and went up the stairs without turning on the light. The landing was "
                "dark and the door to her flat stood open an inch, which was how she knew "
                "someone had been there, and had not been careful about it. ")
        resp = os.path.join(tmp, "resp.txt")
        with open(resp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("She walked to the door and opened it. The room was cold. " * 80
                     + leak * 6 + "\n")
        ingest = ["--ingest", "A-01", "--response", resp, "--out", rundir,
                  "--books-root", books_root, "--manifest", mpath]
        r = run(dispatch, *ingest, "--model-returned", "gemini-3.8-flash-001",
                "--finalize")
        check("ingest files and finalizes", r.returncode == 0, r.stdout[-400:])
        r = run(os.path.join(HERE, "manifest.py"), "--check", mpath)
        check("filed row validates", r.returncode == 0, r.stdout[-300:])

        log = os.path.join(books_root, "A-01", "logs", "prompts.jsonl")
        with open(log, encoding="utf-8") as fh:
            entry = json.loads(fh.readline())
        plan_row = {r["book_id"]: r for r in _csv.DictReader(
            open(os.path.join(rundir, "RUNPLAN.csv"), encoding="utf-8-sig"))}["A-01"]
        check("logged prompt is the planned payload, byte for byte",
              entry["prompt_sha256"] == plan_row["payload_sha256"], entry["prompt"][:60])
        check("the logged prompt is design §3's wrapper, not a paraphrase",
              entry["prompt"].startswith("Write a novel of about 60,000 words based on "
                                         "this premise: A 36-year-old cave surveyor"),
              entry["prompt"][:80])

        r = run(dispatch, "--ingest", "A-02", "--response", resp, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath)
        check("ingest refuses a row with no returned model version", r.returncode == 1)

        dup = os.path.join(tmp, "dup.txt")
        with open(dup, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("She walked to the door and opened it. Nothing else happened that "
                     "day. " * 90 + "\n")
        r = run(dispatch, "--ingest", "A-02", "--response", dup, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001")
        check("a second book opening on the same sentence is refused",
              r.returncode == 1, r.stdout[-300:])
        check("the refusal names the book it collides with", "A-01" in r.stdout,
              r.stdout[-300:])
        check("a refused opening is not appended to the manuscript",
              not os.path.exists(os.path.join(books_root, "A-02", "manuscript",
                                             "naive-text.md")))

        r = run(dispatch, "--ingest", "A-02", "--response", dup, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001",
                "--deviation", "opening repeats A-01; re-dispatch pending", "--finalize")
        check("a logged deviation files the colliding book instead of hiding it",
              r.returncode == 0, r.stdout[-400:])
        with open(os.path.join(books_root, "A-02", "logs", "prompts.jsonl"),
                  encoding="utf-8") as fh:
            a02 = json.loads(fh.readline())
        check("the log records which book it collided with",
              a02.get("opening_collision") == ["A-01"], str(a02.get("opening_collision")))
        with open(mpath, encoding="utf-8-sig") as fh:
            row_a02 = {x["book_id"]: x for x in _csv.DictReader(fh)}["A-02"]
        check("the manifest carries the collision, not just the operator's note",
              "opening collides with A-01" in row_a02["deviations"],
              row_a02["deviations"])

        swap = os.path.join(tmp, "swap.txt")
        with open(swap, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("She walked to the door and she opened it. A different book. " * 90
                     + "\n")
        r = run(dispatch, "--ingest", "A-04", "--response", swap, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001")
        check("the same opener with a pronoun swapped is still refused",
              r.returncode == 1, r.stdout[-300:])

        fresh = os.path.join(tmp, "fresh.txt")
        with open(fresh, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("The bus was already late when Oskar reached the stop. Rain had "
                     "stopped an hour before. " * 90 + "\n")
        r = run(dispatch, "--ingest", "A-05", "--response", fresh, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001")
        check("a distinct opening files with no flag", r.returncode == 0, r.stdout[-300:])

        # The runbook's step 6: a book whose last response is filed but whose row is missing
        # must gain its row without appending the text a second time.
        words_before = len(open(os.path.join(books_root, "A-05", "manuscript",
                                             "naive-text.md"), encoding="utf-8").read().split())
        r = run(dispatch, "--finalize-only", "A-05", "--out", rundir,
                "--books-root", books_root, "--manifest", mpath)
        check("finalize-only writes the row without re-ingesting",
              r.returncode == 0, r.stdout[-400:])
        words_after = len(open(os.path.join(books_root, "A-05", "manuscript",
                                            "naive-text.md"), encoding="utf-8").read().split())
        check("finalize-only appends no text", words_before == words_after,
              f"{words_before} -> {words_after}")
        with open(mpath, encoding="utf-8-sig") as fh:
            check("finalize-only's row validates",
                  "A-05" in {x["book_id"] for x in _csv.DictReader(fh)})
        r = run(dispatch, "--finalize-only", "A-05", "--out", rundir,
                "--books-root", books_root, "--manifest", mpath)
        check("finalize-only refuses a second row for one book", r.returncode == 1,
              r.stdout[-300:])

        shar = os.path.join(tmp, "shared-phrase.txt")
        with open(shar, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("Oskar counted the coins twice and put them back in his pocket. " * 100
                     + leak * 3 + "\n")
        r = run(dispatch, "--ingest", "A-06", "--response", shar, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001")
        check("a reworded opening still loses to a shared long phrase",
              r.returncode == 1, r.stdout[-400:])
        check("the phrase refusal prints the passage itself",
              "smell of the stairwell" in r.stdout, r.stdout[-400:])
        with open(os.path.join(mpath), encoding="utf-8-sig") as fh:
            check("a phrase-colliding book is not in the manifest",
                  "A-06" not in {x["book_id"] for x in _csv.DictReader(fh)})

        r = run(dispatch, "--ingest", "A-06", "--response", shar, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001",
                "--deviation", "shared phrase is a coincidence; keep", "--finalize")
        check("a logged deviation files the phrase collision too",
              r.returncode == 0, r.stdout[-400:])
        with open(os.path.join(books_root, "A-06", "logs", "prompts.jsonl"),
                  encoding="utf-8") as fh:
            a06 = json.loads(fh.readline())
        check("the log keeps the passages, not just the book id",
              bool(a06.get("passage_collision"))
              and any("smell of the stairwell" in p
                      for c in a06["passage_collision"] for p in c["passages"]),
              str(a06.get("passage_collision"))[:300])

        payload = os.path.join(rundir, "payloads", "A-03.txt")
        with open(payload, "a", encoding="utf-8") as fh:
            fh.write(" ")
        r = run(dispatch, "--ingest", "A-03", "--response", resp, "--out", rundir,
                "--books-root", books_root, "--manifest", mpath,
                "--model-returned", "gemini-3.8-flash-001")
        check("ingest refuses a payload that no longer matches the plan", r.returncode == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = [s for s in STEPS if not s[1]]
    print(f"\n{len(STEPS) - len(bad)}/{len(STEPS)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
