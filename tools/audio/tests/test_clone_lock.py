#!/usr/bin/env python3
"""Acceptance tests for the clone-lock voice workflow.

The five acceptance criteria from the brief, each as a test:

  1. The same character across 3+ chapters stays above the similarity threshold
     against its golden reference.              -> test_same_character_across_three_chapters
  2. A scene with 2+ speakers keeps every voice distinct and matched to its own
     reference.                                 -> test_two_speaker_scene_is_one_pass_and_distinct
  3. A chapter referencing a character with no frozen reference hard-stops with a
     clear error — no silent design fallback, no substitution.
                                                -> test_unfrozen_character_hard_stops
  4. Re-rendering a chapter from the frozen references matches the first render's
     voice (similarity above threshold).        -> test_rerender_reproduces_the_voice
  5. Frozen references survive a full book render byte-identical.
                                                -> test_frozen_references_survive_book_render

Plus the workflow guarantees the brief makes non-negotiable: no auto-approve, a
freeze is versioned and never overwritten, design renders from book prose and
refuses when the character has too little of it, and the real CLI refuses to
render an unfrozen cast.

The tests drive the production code paths with the deterministic reference engine
(`ming`), which is byte-reproducible and needs no model download: the workflow,
the gating and the instrumentation are what is under test, not the acoustic
quality of a particular engine. The engine-swappable renderer is exercised through
its real interface, so an engine that cannot render a scene in one pass still
fails here rather than being papered over.

Run:  python -m unittest discover -s tools/audio/tests -v
"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.dirname(HERE)

NARRATION_LINES = [
    "The rain came off the ridge all afternoon and the quay ran grey with it.",
    "Three ledgers lay open across the steel table, weighted at the corners with brass.",
    "Nobody on that street ever agreed about anything except the price of fish.",
    "The barometer on the stairwell wall had dropped another four millibars by midnight.",
    "Every window along the north corridor carried a thin bead of condensation.",
    "She worked methodically from the earliest survey folder to the latest.",
    "The radiator in the charting room knocked twice whenever the boiler cycled.",
    "Outside, a lorry shifted down at the crossroads and kept going toward the coast.",
]
MITTENS_LINES = [
    "Two of the good ones, and none of your clever ones this time.",
    "I have been standing here since six and nobody has offered me anything.",
    "That is not a price, that is a rumour with a number attached to it.",
    "If the board was wrong then the man who hung it there was lying to you.",
]
ROCKY_LINES = [
    "The third column from the bottom is the only one that was ever honest.",
    "I have sat in this room for nine years signing my name to a sentence.",
    "Read the date, and then tell me again that nobody was in the vault.",
    "You do not have to stay, but the generator will not hold the pumps past four.",
]

CONFIG_TEMPLATE = """audiobook:
  backend: ming
  paralinguistic_cap_per_chapter: 2
  voices:
    NARRATOR:
      role: narrator
      voice_design: "a London woman of forty-five with a bright, ringing, unmistakably feminine voice pitched at the top of a woman's range, warm and loud from years of reading aloud"
    Mittens Brisk:
      role: character
      voice_design: "a young man of twenty-two with a light, slightly nasal tenor pitched higher than his frame suggests, quick flat East London vowels"
      aliases: [Mittens]
    Rocky Cavaltone:
      role: character
      voice_design: "a very deep-voiced old man of fifty-eight, a bass-baritone with gravel at the bottom, dry received pronunciation, speaking slowly"
      aliases: [Rocky]
"""


def load_clone_lock():
    spec = importlib.util.spec_from_file_location(
        "clone_lock_under_test", os.path.join(AUDIO, "clone_lock.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_casting():
    spec = importlib.util.spec_from_file_location(
        "casting_under_test", os.path.join(AUDIO, "casting.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CL = load_clone_lock()
CASTING = load_casting()


class BookFixture:
    """A minimal but real book tree: config, manuscripts, scripts, frozen cast."""

    def __init__(self, characters=("NARRATOR", "Mittens Brisk", "Rocky Cavaltone"),
                 chapters=1):
        self.root = tempfile.mkdtemp(prefix="clone-lock-book-")
        self.characters = characters
        self.write_config()
        self.scripts = {}
        for chapter in range(1, chapters + 1):
            self.scripts[chapter] = self.write_chapter(chapter)
        self.renderer = self.make_renderer()

    # -- filesystem -------------------------------------------------------
    def path(self, *parts):
        return os.path.join(self.root, *parts)

    def write(self, rel, text):
        path = self.path(*rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return path

    def write_config(self):
        self.write("audiobook/config.yaml", CONFIG_TEMPLATE)

    def write_chapter(self, chapter, segments=None, speakers=None):
        """Write a manuscript file and a narration script derived from it."""
        if segments is None:
            segments = []
            for index in range(3):
                segments.append(("narration", "NARRATOR",
                                 NARRATION_LINES[(chapter + index) % len(NARRATION_LINES)]))
            if "Mittens Brisk" in self.characters:
                segments.append(("dialogue", "Mittens Brisk",
                                 MITTENS_LINES[chapter % len(MITTENS_LINES)]))
                segments.append(("dialogue", "Mittens Brisk",
                                 MITTENS_LINES[(chapter + 1) % len(MITTENS_LINES)]))
            if "Rocky Cavaltone" in self.characters:
                segments.append(("dialogue", "Rocky Cavaltone",
                                 ROCKY_LINES[chapter % len(ROCKY_LINES)]))
                segments.append(("dialogue", "Rocky Cavaltone",
                                 ROCKY_LINES[(chapter + 1) % len(ROCKY_LINES)]))
        source_rel = f"manuscript/chapters/ch-{chapter:02d}.md"
        manuscript = "\n\n".join(text for _kind, _speaker, text in segments)
        self.write(source_rel, manuscript + "\n")
        script = {
            "schema": "incunabula.audiobook.script.v1",
            "chapter": chapter,
            "source_file": source_rel,
            "source_sha256": hashlib.sha256(
                (manuscript + "\n").encode("utf-8")).hexdigest(),
            "summary": {"speakers": sorted({s for _k, s, _t in segments})},
            "segments": [
                {
                    "segment_id": f"ch{chapter:02d}-seg{index + 1:04d}",
                    "kind": kind,
                    "speaker": speaker,
                    "spoken_text": text,
                    "pause_after_ms": 300,
                    "style": {"speed": 1.0, "pitch": 0.0, "volume": 0.0,
                              "emotion": "neutral"},
                    "paralinguistic_tags": [],
                }
                for index, (kind, speaker, text) in enumerate(segments)
            ],
        }
        path = self.write(f"audiobook/scripts/chapter-{chapter:02d}.json",
                          json.dumps(script, indent=2))
        self.scripts[chapter] = (path, script)
        return path, script

    # -- cast -------------------------------------------------------------
    def make_renderer(self, cls=None):
        spec = importlib.util.spec_from_file_location(
            "renderer_under_test", os.path.join(AUDIO, "renderer.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return (cls or mod.DeterministicRenderer)()

    def freeze_cast(self, characters=None, target_words=40, min_words=20):
        registry, _voices, _lookup = CL.sync_registry_with_cast(self.root)
        for character in (characters or self.characters):
            CL.design_character(self.root, character, self.renderer,
                                target_words=target_words, min_words=min_words,
                                registry=registry)
            CL.approve_character(self.root, character, "Test Listener",
                                 "listened on headphones")
            CL.freeze_character(self.root, character, registry=registry)
        return CL.load_registry(self.root)

    def script_for(self, chapter):
        return self.scripts[chapter][1]

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class SpyRenderer:

    """Deterministic engine that counts design and scene calls."""

    def __init__(self, renderer):
        self._inner = renderer
        self.backend = renderer.backend
        self.design_calls = []
        self.scene_calls = []

    def design_to_wav(self, **kwargs):
        self.design_calls.append(kwargs.get("character"))
        return self._inner.design_to_wav(**kwargs)

    def synthesize_scene_to_wav(self, turns, out_wav_path, cast, sample_rate=24000):
        self.scene_calls.append({"turns": len(turns),
                                 "cast": sorted(cast),
                                 "speakers": sorted({t['speaker'] for t in turns})})
        return self._inner.synthesize_scene_to_wav(
            turns=turns, out_wav_path=out_wav_path, cast=cast,
            sample_rate=sample_rate)

    def extract_speaker_embedding(self, wav_path):
        return self._inner.extract_speaker_embedding(wav_path)


class CloneLockTestCase(unittest.TestCase):
    MAX_CHAPTERS = 3

    def setUp(self):
        self.book = BookFixture(chapters=self.MAX_CHAPTERS)
        self.addCleanup(self.book.cleanup)

    def render_chapter(self, chapter, out_dir=None, floor=None, renderer=None,
                       registry=None):
        out_dir = out_dir or self.book.path("audiobook", "audio")
        renderer = renderer or self.book.renderer
        return CL.render_chapter(
            renderer=renderer,
            book_root=self.book.root,
            script=self.book.script_for(chapter),
            script_path=self.book.scripts[chapter][0],
            out_dir=out_dir,
            drift_floor=CL.DEFAULT_DRIFT_FLOOR if floor is None else floor,
            verifier=self.make_verifier(),
            registry=registry,
        )

    def make_verifier(self):
        spec = importlib.util.spec_from_file_location(
            "verifier_under_test", os.path.join(AUDIO, "verifier.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.RendererVerifier(self.book.renderer)

    def assert_drift_ok(self, record, characters):
        for character in characters:
            row = record["drift"][character]
            self.assertGreaterEqual(
                row["cosine"], record["drift_floor"],
                f"{character} drift {row['cosine']} below floor {record['drift_floor']}")
            self.assertEqual(row["status"], "OK", f"{character}: {row}")


class TestAcceptance1SameCharacterAcrossChapters(CloneLockTestCase):
    def test_same_character_across_three_chapters(self):
        self.book.freeze_cast()
        for chapter in (1, 2, 3):
            record, fails = self.render_chapter(chapter)
            self.assertEqual(fails, [], fails)
            self.assert_drift_ok(record, ["NARRATOR", "Mittens Brisk", "Rocky Cavaltone"])
            CL.append_drift_log(self.book.root, record)

        log = CL.load_drift_log(self.book.root)
        self.assertEqual(sorted(log["chapters"]), ["01", "02", "03"])
        for chapter in ("01", "02", "03"):
            self.assertEqual(sorted(log["chapters"][chapter]["characters"]),
                             ["Mittens Brisk", "NARRATOR", "Rocky Cavaltone"])
            for row in log["chapters"][chapter]["characters"].values():
                self.assertEqual(row["status"], "OK")
        table = CL.format_drift_table(log)
        self.assertIn("chapter", table)
        self.assertEqual(len(table.splitlines()), 10)  # header + 3 chapters x 3 voices


class TestAcceptance2MultiSpeakerScene(CloneLockTestCase):
    def test_two_speaker_scene_is_one_pass_and_distinct(self):
        self.book.freeze_cast()
        spy = SpyRenderer(self.book.renderer)
        record, fails = self.render_chapter(1, renderer=spy)
        self.assertEqual(fails, [], fails)

        # One scene in the fixture -> exactly one engine pass, with both speakers.
        self.assertEqual(len(spy.scene_calls), 1, spy.scene_calls)
        self.assertEqual(spy.scene_calls[0]["speakers"],
                         ["Mittens Brisk", "NARRATOR", "Rocky Cavaltone"])
        self.assertEqual(spy.scene_calls[0]["cast"],
                         ["Mittens Brisk", "NARRATOR", "Rocky Cavaltone"])
        self.assertEqual(record["scenes"][0]["passes"], 1)
        # Rendering never designs.
        self.assertEqual(spy.design_calls, [])

        for character in ("NARRATOR", "Mittens Brisk", "Rocky Cavaltone"):
            row = record["drift"][character]
            self.assertEqual(row["status"], "OK", row)
            self.assertGreater(row["margin"], 0.0,
                               f"{character} is not closer to its own reference: {row}")


class TestAcceptance3UnfrozenCharacterHardStops(CloneLockTestCase):
    def test_unfrozen_character_hard_stops(self):
        # Rocky is declared in config and speaks in chapter 1, but is never frozen.
        self.book.freeze_cast(["NARRATOR", "Mittens Brisk"])
        spy = SpyRenderer(self.book.renderer)
        out_dir = self.book.path("audiobook", "audio")
        with self.assertRaises(CL.CloneLockError) as ctx:
            self.render_chapter(1, renderer=spy, out_dir=out_dir)
        message = str(ctx.exception)
        self.assertIn("Rocky Cavaltone", message)
        self.assertIn("no frozen golden reference", message)
        self.assertEqual(spy.design_calls, [], "design ran to fill a missing voice")
        self.assertEqual(spy.scene_calls, [], "a scene rendered with an unfrozen cast")
        self.assertFalse(
            os.path.isfile(os.path.join(out_dir, "chapter-01.wav")),
            "audio was written despite the refusal")

    def test_render_book_cli_refuses_unfrozen_cast(self):
        self.book.freeze_cast(["NARRATOR", "Mittens Brisk"])
        result = subprocess.run(
            [sys.executable, os.path.join(AUDIO, "render-book.py"), self.book.root,
             "--chapter", "1", "--verifier", "campplus"],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Rocky Cavaltone", result.stderr)


class TestAcceptance4RerenderReproducesVoice(CloneLockTestCase):
    def test_rerender_reproduces_the_voice(self):
        self.write_single_voice_config()  # one character keeps this test unambiguous
        self.book.freeze_cast(["NARRATOR"])
        first_dir = self.book.path("out-first")
        second_dir = self.book.path("out-second")
        first, fails = self.render_chapter(1, out_dir=first_dir)
        self.assertEqual(fails, [], fails)
        second, fails = self.render_chapter(1, out_dir=second_dir)
        self.assertEqual(fails, [], fails)

        first_wav = self.book.path("out-first", "chapter-01.wav")
        second_wav = self.book.path("out-second", "chapter-01.wav")
        with open(first_wav, "rb") as fh:
            first_bytes = fh.read()
        with open(second_wav, "rb") as fh:
            second_bytes = fh.read()

        # The criterion is "similarity above threshold"; the deterministic engine
        # delivers the stronger property, so assert both.
        first_emb = self.book.renderer.extract_speaker_embedding(first_wav)
        second_emb = self.book.renderer.extract_speaker_embedding(second_wav)
        similarity = CASTING.cosine_similarity(first_emb, second_emb)
        self.assertGreaterEqual(similarity, CL.DEFAULT_DRIFT_FLOOR,
                                f"re-render similarity {similarity}")
        self.assertEqual(hashlib.sha256(first_bytes).hexdigest(),
                         hashlib.sha256(second_bytes).hexdigest(),
                         "re-render introduced voice randomness")

    def write_single_voice_config(self):
        self.book.write("audiobook/config.yaml", """audiobook:
  backend: ming
  voices:
    NARRATOR:
      role: narrator
      voice_design: "a London woman of forty-five with a bright, ringing, unmistakably feminine voice pitched at the top of a woman's range, warm and loud from years of reading aloud"
""")
        # One character in the book: chapter 1 is narration, 2 and 3 are removed so
        # the config's script cross-check does not see undeclared speakers.
        self.book.write_chapter(1, segments=[
            ("narration", "NARRATOR", line) for line in NARRATION_LINES[:4]])
        for chapter in (2, 3):
            os.remove(self.book.scripts[chapter][0])


class TestAcceptance5ReferencesSurviveBookRender(CloneLockTestCase):
    def test_frozen_references_survive_book_render(self):
        self.book.freeze_cast()
        before = CL.reference_snapshot(self.book.root)
        self.assertEqual(len(before), 3)
        for chapter in (1, 2, 3):
            record, fails = self.render_chapter(chapter)
            self.assertEqual(fails, [], fails)
            CL.append_drift_log(self.book.root, record)
        after = CL.reference_snapshot(self.book.root)
        self.assertEqual(before, after, "a render altered a frozen reference")
        problems, _reg = CL.verify_registry(self.book.root)
        self.assertEqual(problems, [])
        for character, snap in after.items():
            with open(self.book.path(*snap["wav"].split("/")), "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                                 snap["wav_sha256"], character)


class TestWorkflowGuarantees(CloneLockTestCase):
    def test_freeze_requires_a_human_listening_pass(self):
        registry, _v, _l = CL.sync_registry_with_cast(self.book.root)
        CL.design_character(self.book.root, "NARRATOR", self.book.renderer,
                            target_words=40, min_words=20, registry=registry)
        with self.assertRaises(CL.CloneLockError) as ctx:
            CL.freeze_character(self.book.root, "NARRATOR")
        self.assertIn("not been listened to", str(ctx.exception))

        for reviewer in ("", "auto", "pipeline", "n/a"):
            with self.assertRaises(CL.CloneLockError):
                CL.approve_character(self.book.root, "NARRATOR", reviewer)

        CL.approve_character(self.book.root, "NARRATOR", "A. Human", "listened twice")
        entry = CL.freeze_character(self.book.root, "NARRATOR")
        self.assertTrue(entry["frozen"])
        self.assertEqual(entry["version"], 1)
        self.assertTrue(os.path.isfile(
            self.book.path("audiobook", "voices", "NARRATOR", "v001",
                           "golden_reference.wav")))

    def test_refreeze_is_explicit_and_keeps_old_version(self):
        self.book.freeze_cast(["NARRATOR"])
        v001 = CL.load_registry(self.book.root)["characters"]["NARRATOR"]["reference"]
        with self.assertRaises(CL.CloneLockError) as ctx:
            CL.freeze_character(self.book.root, "NARRATOR")
        self.assertIn("already frozen", str(ctx.exception))

        registry, _v, _l = CL.sync_registry_with_cast(self.book.root)
        CL.design_character(self.book.root, "NARRATOR", self.book.renderer,
                            target_words=40, min_words=20, registry=registry,
                            allow_redesign=True)
        CL.approve_character(self.book.root, "NARRATOR", "A. Human", "new take")
        with self.assertRaises(CL.CloneLockError):
            CL.freeze_character(self.book.root, "NARRATOR", allow_refreeze=True,
                                reviewer="auto", reason="wanted another")
        with self.assertRaises(CL.CloneLockError):
            CL.freeze_character(self.book.root, "NARRATOR", allow_refreeze=True,
                                reviewer="A. Human", reason="")

        entry = CL.freeze_character(self.book.root, "NARRATOR", allow_refreeze=True,
                                    reviewer="A. Human", reason="re-recorded the take")
        self.assertEqual(entry["version"], 2)
        self.assertEqual(len(entry["history"]), 1)
        self.assertEqual(entry["history"][0]["version"], 1)
        old_wav = self.book.path(*v001["wav"].split("/"))
        self.assertTrue(os.path.isfile(old_wav), "re-freeze destroyed v001")
        with open(old_wav, "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                             v001["wav_sha256"])

    def test_design_renders_from_book_prose(self):
        registry, _v, lookup = CL.sync_registry_with_cast(self.book.root)
        entry = CL.design_character(self.book.root, "Mittens Brisk",
                                    self.book.renderer, target_words=40,
                                    min_words=20, registry=registry)
        candidate = entry["design_candidate"]
        with open(self.book.path(*candidate["transcript"].split("/")),
                  encoding="utf-8") as fh:
            transcript = fh.read()
        for line in MITTENS_LINES:
            if line in " ".join(
                    seg["spoken_text"] for seg in self.book.script_for(1)["segments"]):
                self.assertIn(line, transcript)
        self.assertGreaterEqual(candidate["duration_sec"], CL.REFERENCE_MIN_SEC)
        self.assertLessEqual(candidate["duration_sec"], CL.REFERENCE_MAX_SEC)
        self.assertFalse(entry["frozen"], "design alone froze a voice")

    def test_design_refuses_thin_book_material(self):
        self.book.write_chapter(1, segments=[
            ("dialogue", "Mittens Brisk", "Two of the good ones.")])
        registry, _v, _l = CL.sync_registry_with_cast(self.book.root)
        with self.assertRaises(CL.CloneLockError) as ctx:
            CL.design_character(self.book.root, "Mittens Brisk",
                                self.book.renderer, registry=registry)
        self.assertIn("Mittens Brisk", str(ctx.exception))
        self.assertIn("No golden reference", str(ctx.exception))

    def test_drift_below_floor_fails_the_chapter(self):
        self.book.freeze_cast()
        record, fails = self.render_chapter(1, floor=0.9999)
        self.assertTrue(fails, "audio below the floor was accepted silently")
        self.assertEqual(record["status"], "FAIL")
        self.assertTrue(any("NARRATOR" in f for f in fails), fails)

    def test_render_book_cli_writes_drift_log(self):
        self.book.freeze_cast()
        result = subprocess.run(
            [sys.executable, os.path.join(AUDIO, "render-book.py"), self.book.root,
             "--chapter", "1", "--verifier", "campplus"],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        log = CL.load_drift_log(self.book.root)
        self.assertIn("01", log["chapters"])
        self.assertEqual(sorted(log["chapters"]["01"]["characters"]),
                         ["Mittens Brisk", "NARRATOR", "Rocky Cavaltone"])
        with open(self.book.path("audiobook", "audio", "render-manifest.json"),
                  encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertEqual(manifest["render_mode"], "CLONE_LOCK_SINGLE_PASS")
        self.assertEqual(manifest["chapters"]["01"]["scenes"][0]["passes"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
